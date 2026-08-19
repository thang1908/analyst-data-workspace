"""LangChain structured classifier for CX resident feedback."""
from __future__ import annotations

import json
import logging
import os
from typing import Sequence

from langchain_core.prompts import ChatPromptTemplate

from packages.ai.prompts import SYSTEM_PROMPT_TAXONOMY
from packages.ai.schemas import (
    BatchClassificationOutput,
    FeedbackClassificationResult,
    FeedbackItemInput,
)

logger = logging.getLogger(__name__)


class FeedbackClassifier:
    """Multi-provider LangChain structured classifier for residential CX feedback."""

    def __init__(
        self,
        model_name: str | None = None,
        provider: str | None = None,
        temperature: float = 0.1,
    ) -> None:
        self.provider = provider or os.getenv("AI_PROVIDER", "gemini").lower()
        self.temperature = temperature
        self._llm = self._init_llm(model_name)
        self._prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_TAXONOMY),
                (
                    "human",
                    "Hãy phân tích và phân loại danh sách các phản hồi của cư dân dưới đây:\n\n{items_json}",
                ),
            ]
        )
        if self._llm is not None:
            self._chain = self._prompt | self._llm.with_structured_output(
                BatchClassificationOutput
            )
        else:
            self._chain = None

    def _init_llm(self, model_name: str | None) -> Any:
        gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        if (self.provider == "gemini" or gemini_key) and not self.provider.startswith("openai"):
            if not gemini_key:
                logger.warning("GEMINI_API_KEY is not configured. Falling back to local heuristic mode.")
                return None
            from langchain_google_genai import ChatGoogleGenerativeAI

            selected_model = model_name or os.getenv("AI_MODEL_NAME", "gemini-2.0-flash")
            return ChatGoogleGenerativeAI(
                model=selected_model,
                temperature=self.temperature,
                google_api_key=gemini_key,
            )

        if self.provider == "openai" or openai_key:
            if not openai_key:
                logger.warning("OPENAI_API_KEY is not configured. Falling back to local heuristic mode.")
                return None
            from langchain_openai import ChatOpenAI

            selected_model = model_name or os.getenv("AI_MODEL_NAME", "gpt-4o-mini")
            return ChatOpenAI(
                model=selected_model,
                temperature=self.temperature,
                api_key=openai_key,
            )

        return None

    async def classify_batch(
        self, items: Sequence[FeedbackItemInput]
    ) -> BatchClassificationOutput:
        """Classify a batch of feedback items."""
        if not items:
            return BatchClassificationOutput(results=[])

        # If LLM is available, invoke structured output chain
        if self._chain is not None:
            items_payload = [
                {
                    "item_id": item.item_id,
                    "text": item.text,
                    "location": item.location or "",
                    "channel": item.channel or "",
                    "reported_date": item.reported_date or "",
                }
                for item in items
            ]
            items_json = json.dumps(items_payload, ensure_ascii=False, indent=2)
            try:
                result: BatchClassificationOutput = await self._chain.ainvoke(
                    {"items_json": items_json}
                )
                return result
            except Exception as exc:
                logger.error(f"Error calling LLM structured classification: {exc}")

        # Fallback heuristic classifier if LLM is unavailable or failed
        return self._heuristic_fallback(items)

    def _heuristic_fallback(
        self, items: Sequence[FeedbackItemInput]
    ) -> BatchClassificationOutput:
        """Rule-based fallback ensuring 100% schema conformance when LLM is offline."""
        results: list[FeedbackClassificationResult] = []
        for item in items:
            text_lower = item.text.lower().strip()

            # 1. Spam / Test / Non-feedback check
            is_spam = (
                len(text_lower) < 5
                or text_lower in ["test", "alo", "chào", "hi", "ok", "123", "abc", "chấm", "...", "test 123", "alo 123"]
                or any(phrase in text_lower for phrase in ["alo alo", "test 123", "test test", "chào bạn", "hello test"])
            )
            if is_spam:
                results.append(
                    FeedbackClassificationResult(
                        item_id=item.item_id,
                        is_valid_feedback=False,
                        analytic_eligibility="EXCLUDED",
                        exclusion_reason="NON_FEEDBACK",
                        primary_service_code="SV-10",
                        issue_code="IS-10-01",
                        journey_stage_code="RES",
                        journey_step_code="RES-07",
                        sentiment="NEUTRAL",
                        operational_severity="SEV-4",
                        confidence=0.95,
                        rationale="Đoạn văn bản quá ngắn hoặc là câu test/chào hỏi không có nội dung phản ánh.",
                    )
                )
                continue

            # 2. Sentiment
            sentiment = "NEUTRAL"
            if any(w in text_lower for w in ["khen", "tốt", "hài lòng", "cảm ơn", "nhanh", "chu đáo", "tuyệt vời"]):
                sentiment = "POSITIVE"
            elif any(w in text_lower for w in ["hỏng", "kẹt", "lỗi", "chậm", "bẩn", "ồn", "mất", "bực", "tắc", "mùi"]):
                sentiment = "NEGATIVE"

            # 3. Severity
            severity = "SEV-4"
            if any(w in text_lower for w in ["cháy", "nổ", "khói", "nguy hiểm", "cứu", "khẩn cấp", "chập điện"]):
                severity = "SEV-1"
            elif any(w in text_lower for w in ["kẹt thang", "mất nước", "mất điện", "vỡ ống"]):
                severity = "SEV-2"
            elif sentiment == "NEGATIVE":
                severity = "SEV-3"

            # 4. Service & Issue
            service = "SV-07"
            issue = "IS-07-01"
            if any(w in text_lower for w in ["bãi xe", "đỗ xe", "bãi đỗ", "thẻ xe", "sạc xe", "hầm xe", "gửi xe", "tìm xe"]):
                service = "SV-05"
                issue = "IS-05-02"
            elif any(w in text_lower for w in ["thang máy", "điều hòa", "mất điện", "mất nước", "thấm dột", "vỡ ống", "hạ tầng", "kỹ thuật"]):
                service = "SV-07"
                issue = "IS-07-01"
            elif any(w in text_lower for w in ["bảo vệ", "an ninh", "trộm", "tiếng ồn", "pccc", "báo cháy"]):
                service = "SV-08"
                issue = "IS-08-01"
            elif any(w in text_lower for w in ["rác", "vệ sinh", "bẩn", "lau dọn", "cây xanh", "côn trùng", "mùi hôi"]):
                service = "SV-09"
                issue = "IS-09-01"
            elif any(w in text_lower for w in ["phí", "hóa đơn", "thanh toán", "chuyển khoản", "tiền nước", "tiền điện"]):
                service = "SV-04"
                issue = "IS-04-01"
            elif any(w in text_lower for w in ["hồ bơi", "gym", "bbq", "tiện ích", "sân bóng"]):
                service = "SV-06"
                issue = "IS-06-01"
            elif any(w in text_lower for w in ["hợp đồng", "app", "thủ tục", "cskh", "sổ hồng"]):
                service = "SV-03"
                issue = "IS-03-01"
            elif any(w in text_lower for w in ["điện", "nước"]):
                service = "SV-07"
                issue = "IS-07-01"

            results.append(
                FeedbackClassificationResult(
                    item_id=item.item_id,
                    is_valid_feedback=True,
                    analytic_eligibility="INCLUDED",
                    exclusion_reason="NONE",
                    primary_service_code=service,
                    issue_code=issue,
                    journey_stage_code="RES",
                    journey_step_code="RES-07",
                    sentiment=sentiment,
                    operational_severity=severity,
                    confidence=0.85,
                    rationale=f"Phân loại tự động theo nội dung liên quan đến dịch vụ {service}.",
                )
            )

        return BatchClassificationOutput(results=results)
