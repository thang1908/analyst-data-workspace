"""Generate rich, realistic residential CX mock dataset and seed into database."""
from __future__ import annotations

import asyncio
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import text
from packages.infrastructure.db.session import AsyncSessionLocal

PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
ACTOR_ID = UUID("00000000-0000-0000-0000-000000000002")

LOCATIONS = [
    {"code": "LOC-S1001", "name": "Tòa S10.01 - Vinhomes Grand Park"},
    {"code": "LOC-S1002", "name": "Tòa S10.02 - Vinhomes Grand Park"},
    {"code": "LOC-S801", "name": "Tòa S8.01 - Vinhomes Smart City"},
    {"code": "LOC-S802", "name": "Tòa S8.02 - Vinhomes Smart City"},
    {"code": "LOC-R6", "name": "Tòa R6 - Vinhomes Royal City"},
    {"code": "LOC-L81", "name": "Tòa Landmark 81 - Central Park"},
]

CHANNELS = ["CH-APP", "CH-HOTLINE", "CH-FRONTDESK", "CH-WEB", "CH-SOCIAL", "CH-EMAIL"]

# Realistic Vietnamese Feedback Templates categorized by Service & Issue
SCENARIOS = [
    # SV-07: Kỹ thuật & Thang máy (Cluster hotspot candidate for S10.02)
    {
        "service_code": "SV-07", "issue_code": "IS-07-01", "step_code": "RES-07", "stage_code": "RES",
        "touchpoint_code": "TP-RES-03-03", "sentiment": "NEGATIVE", "severity": "SEV-2", "valid": True,
        "texts": [
            "Thang máy số 3 toà S10.02 sáng nay bị kẹt ở tầng 15 khoảng 10 phút, bấm chuông báo động không ai nghe.",
            "Thang máy toà S10.02 rung lắc rất mạnh khi di chuyển qua tầng 12, đề nghị kỹ thuật kiểm tra gấp.",
            "Thang máy toà nhà chạy giật cục và phát ra tiếng kêu cọt kẹt bất thường, rất nguy hiểm cho trẻ nhỏ.",
            "Sáng nay giờ cao điểm thang máy toà S10.02 bị hỏng 2 trên 4 thang, cư dân xếp hàng chờ nửa tiếng.",
            "Thang máy toà S10.02 mở cửa rất chậm và hay bị kẹt tầng hầm B1, đã phản ánh nhiều lần chưa thấy sửa.",
            "Thang máy số 2 bảng điều khiển bị đơ liệt nút bấm tầng 8 và tầng 10.",
            "Hệ thống điều hòa sảnh tầng 1 toà nhà bị hỏng không hoạt động, không khí ngột ngạt và nóng bức.",
            "Đường ống nước sinh hoạt hành lang tầng 7 bị rò rỉ nước chảy tràn ra sàn gạch trơn trượt.",
            "Áp lực nước yếu vào các khung giờ tối, vòi sen hầu như không chảy được nước nóng.",
            "Hành lang tầng 9 bị cháy 2 bóng đèn chiếu sáng từ tuần trước tới nay chưa được thay mới.",
        ],
    },
    # SV-05: Bãi xe & Ra vào (Cluster hotspot candidate for S8.01)
    {
        "service_code": "SV-05", "issue_code": "IS-05-02", "step_code": "RES-03", "stage_code": "RES",
        "touchpoint_code": "TP-RES-03-02", "sentiment": "NEGATIVE", "severity": "SEV-3", "valid": True,
        "texts": [
            "Bãi đỗ xe tầng hầm B2 toà S8.01 lúc nào cũng hết chỗ đỗ ô tô, nhiều xe đỗ chắn lối đi chung.",
            "Trạm sạc xe điện dưới hầm toà S8.01 bị xe xăng đỗ chiếm chỗ cả ngày không sạc được.",
            "Cổng barrier quẹt thẻ xe máy nhận diện biển số rất chậm, giờ tan tầm hay gây ùn tắc lối vào.",
            "Thẻ từ thang máy và thẻ gửi xe của tôi bị lỗi không quét được tại cửa kiểm soát sảnh.",
            "Bãi xe tầng hầm nhiều vị trí bị dột nước từ trần xuống làm bẩn xe cư dân.",
            "Hệ thống quẹt thẻ nhận diện khuôn mặt ở cửa sảnh toà nhà hay bị đơ không mở cửa.",
        ],
    },
    # SV-09: Vệ sinh & Môi trường (Cluster candidate for R6)
    {
        "service_code": "SV-09", "issue_code": "IS-09-01", "step_code": "RES-07", "stage_code": "RES",
        "touchpoint_code": "TP-RES-07-03", "sentiment": "NEGATIVE", "severity": "SEV-3", "valid": True,
        "texts": [
            "Hành lang tầng 12 toà R6 có mùi rác thải hôi nồng nặc do phòng rác chưa được khử khuẩn.",
            "Thùng rác khu vực sảnh chờ và lối đi dạo công viên đầy tràn rác từ sáng chưa thấy ai thu gom.",
            "Khu vực sân chơi trẻ em có nhiều rác thải nhựa và lá cây mục ẩm ướt gây trơn trượt.",
            "Khu vực vườn hoa toà nhà dạo này xuất hiện rất nhiều muỗi và côn trùng, đề nghị phun thuốc diệt muỗi.",
            "Nhân viên vệ sinh lau sàn sảnh không đặt biển cảnh báo sàn ướt, suýt nữa có người ngã.",
        ],
    },
    # SV-08: An ninh & PCCC
    {
        "service_code": "SV-08", "issue_code": "IS-08-01", "step_code": "RES-07", "stage_code": "RES",
        "touchpoint_code": "TP-RES-07-02", "sentiment": "NEGATIVE", "severity": "SEV-2", "valid": True,
        "texts": [
            "Căn hộ bên cạnh hát karaoke gây tiếng ồn lớn sau 23h đêm, gọi bảo vệ 3 lần nhưng không ai lên nhắc nhở.",
            "Hệ thống chuông báo cháy toà nhà kêu reo giả 2 lần lúc nửa đêm làm cư dân hoảng loạn chạy bộ xuống đất.",
            "Bảo vệ chốt cổng phụ không túc trực vị trí, để người lạ tự do đi vào toà nhà không cần quẹt thẻ.",
            "Phát hiện có người hút thuốc lá tại cầu thang bộ thoát hiểm, đề nghị BQL xử phạt nghiêm khắc.",
        ],
    },
    # SV-04: Phí & Hóa đơn
    {
        "service_code": "SV-04", "issue_code": "IS-04-01", "step_code": "RES-06", "stage_code": "RES",
        "touchpoint_code": "TP-RES-06-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "texts": [
            "Hóa đơn tiền nước sinh hoạt tháng này của căn hộ tôi tăng gấp đôi dù số lượng người ở không đổi.",
            "Tôi đã thanh toán phí quản lý qua chuyển khoản ngân hàng 3 ngày trước nhưng trên App vẫn báo nợ.",
            "Bảng kê chi tiết tiền điện và phí dịch vụ tháng này đề nghị BQL giải thích cách tính chỉ số bậc thang.",
            "Tôi muốn đăng ký nhận hóa đơn điện tử VAT về email công ty thì làm thủ tục như thế nào?",
        ],
    },
    # SV-03: Hồ sơ, Thủ tục, App CSKH
    {
        "service_code": "SV-03", "issue_code": "IS-03-01", "step_code": "RES-01", "stage_code": "RES",
        "touchpoint_code": "TP-RES-01-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "texts": [
            "Tôi muốn làm thủ tục đăng ký tạm trú cho người thân thì cần mang những giấy tờ gì lên văn phòng BQL?",
            "Ứng dụng cư dân hay bị văng khi bấm vào mục gửi yêu cầu sửa chữa, đề nghị đội IT fix lỗi.",
            "Gia đình tôi mới mua căn hộ, cần đăng ký cấp lại 2 thẻ cư dân mới bị mất.",
            "BQL có thể thông báo trước lịch cắt điện/nước ít nhất 24h trên app để cư dân chủ động không?",
        ],
    },
    # SV-06: Tiện ích nội khu (Hồ bơi, Gym, BBQ)
    {
        "service_code": "SV-06", "issue_code": "IS-06-01", "step_code": "RES-05", "stage_code": "RES",
        "touchpoint_code": "TP-RES-05-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "texts": [
            "Tôi muốn đặt chỗ sân nướng BBQ cho 10 người vào tối thứ 7 tuần này qua app nhưng hệ thống báo lỗi.",
            "Máy chạy bộ số 2 tại phòng gym toà nhà bị hỏng băng chuyền từ tuần trước chưa thấy kỹ thuật sửa.",
            "Hồ bơi nước dạo này hơi đục và có mùi clo nồng, đề nghị đội vận hành kiểm tra chất lượng nước thường xuyên.",
            "Tôi muốn đăng ký sử dụng thang máy hàng để chuyển đồ đạc nội thất vào chiều chủ nhật.",
        ],
    },
    # POSITIVE: Khen ngợi dịch vụ
    {
        "service_code": "SV-05", "issue_code": "IS-05-01", "step_code": "RES-03", "stage_code": "RES",
        "touchpoint_code": "TP-RES-03-01", "sentiment": "POSITIVE", "severity": "SEV-4", "valid": True,
        "texts": [
            "Rất cảm ơn các bạn bảo vệ toà nhà đã nhiệt tình hỗ trợ che ô và dắt xe cho cư dân lúc trời mưa to.",
            "Bạn lễ tân sảnh toà nhà rất chu đáo, xử lý đăng ký khách đến thăm nhanh gọn và lịch sự.",
            "Đội ngũ kỹ thuật hỗ trợ sửa chữa vòi nước trong căn hộ rất nhanh và chuyên nghiệp, 10 điểm!",
            "Khuôn viên cây xanh và công viên nội khu dạo này được chăm sóc rất đẹp, không khí trong lành.",
            "BQL xử lý khiếu nại tiếng ồn rất nhanh và thỏa đáng, gia đình tôi rất hài lòng.",
            "Dịch vụ vệ sinh toà nhà luôn giữ cho sảnh và thang máy sạch sẽ thơm tho, cảm ơn các cô lao công.",
        ],
    },
    # SPAM / RÁC / NON_FEEDBACK (EXCLUDED)
    {
        "service_code": "SV-10", "issue_code": "IS-10-01", "step_code": "RES-07", "stage_code": "RES",
        "touchpoint_code": None, "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": False,
        "texts": [
            "alo alo test 123",
            "test thử tính năng phản hồi cư dân abc",
            "chấm hóng",
            "Cần bán gấp xe máy Honda Air Blade chính chủ giá rẻ liên hệ 0912345678",
            "Nhận làm bằng lái xe máy và ô tô bao đậu toàn quốc",
            "Cho thuê căn hộ 2 phòng ngủ full nội thất giá tốt",
            "Hôm nay trời đẹp quá cả nhà ơi",
            "ok",
            "hi",
        ],
    },
]


async def seed_data() -> None:
    async with AsyncSessionLocal() as session:
        print("1. Truncating existing transactional data...")
        tables = [
            "feedback_item_hotspot",
            "feedback_item_affected_channel",
            "hotspot",
            "classification_decision",
            "classification_current",
            "feedback_item",
            "feedback",
            "prediction_event",
            "prediction_run",
            "review_event",
        ]
        for t in tables:
            try:
                await session.execute(text(f"TRUNCATE TABLE {t} CASCADE"))
            except Exception as e:
                await session.rollback()
                print(f"  Skip table {t}: {e}")
        await session.commit()

        # 2. Taxonomy and Reference mappings
        tax = await session.execute(text("SELECT taxonomy_release_id FROM taxonomy_release WHERE status = 'PUBLISHED' LIMIT 1"))
        taxonomy_release_id = tax.scalar_one_or_none()
        if not taxonomy_release_id:
            tax = await session.execute(text("SELECT taxonomy_release_id FROM taxonomy_release LIMIT 1"))
            taxonomy_release_id = tax.scalar_one_or_none()

        services_res = await session.execute(text("SELECT service_id, service_code FROM service"))
        service_map = {r["service_code"]: r["service_id"] for r in services_res.mappings().all()}

        issues_res = await session.execute(text("SELECT issue_id, issue_code FROM issue"))
        issue_map = {r["issue_code"]: r["issue_id"] for r in issues_res.mappings().all()}

        steps_res = await session.execute(text("SELECT customer_lifecycle_step_id, customer_lifecycle_stage_id, step_code FROM customer_lifecycle_step"))
        step_map = {r["step_code"]: (r["customer_lifecycle_step_id"], r["customer_lifecycle_stage_id"]) for r in steps_res.mappings().all()}

        channels_res = await session.execute(text("SELECT interaction_channel_id, channel_code FROM interaction_channel"))
        channel_map = {r["channel_code"]: r["interaction_channel_id"] for r in channels_res.mappings().all()}

        # 3. Create Locations
        print("2. Ensuring Locations exist in database...")
        loc_ids = []
        for loc in LOCATIONS:
            loc_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO location (location_id, project_id, location_code, name, location_type, active)
                    VALUES (:id, :project_id, :code, :name, 'BUILDING', true)
                    ON CONFLICT (project_id, location_code) DO UPDATE SET name = EXCLUDED.name
                """),
                {"id": loc_id, "project_id": PROJECT_ID, "code": loc["code"], "name": loc["name"]},
            )
            # Re-fetch the actual ID
            cur = await session.execute(text("SELECT location_id FROM location WHERE project_id = :project_id AND location_code = :code"), {"project_id": PROJECT_ID, "code": loc["code"]})
            loc_ids.append((cur.scalar_one(), loc["code"], loc["name"]))
        await session.commit()

        # 4. Generate ~500 items over the last 30 days
        print("3. Generating realistic resident feedback items...")
        now = datetime.now(timezone.utc)
        feedback_batch = []
        item_batch = []
        decision_batch = []
        current_batch = []

        total_count = 0
        for i in range(520):
            # Pick scenario with realistic weights
            scenario = random.choices(
                SCENARIOS,
                weights=[25, 20, 15, 12, 10, 8, 8, 12, 10],  # higher weights for elevator, parking, clean, praise
                k=1,
            )[0]

            # Pick location (bias elevator issues toward S10.02, parking toward S8.01)
            if scenario["service_code"] == "SV-07" and random.random() < 0.6:
                loc_tuple = next(l for l in loc_ids if l[1] == "LOC-S1002")
            elif scenario["service_code"] == "SV-05" and random.random() < 0.6:
                loc_tuple = next(l for l in loc_ids if l[1] == "LOC-S801")
            elif scenario["service_code"] == "SV-09" and random.random() < 0.5:
                loc_tuple = next(l for l in loc_ids if l[1] == "LOC-R6")
            else:
                loc_tuple = random.choice(loc_ids)

            loc_id, loc_code, loc_name = loc_tuple
            text_content = random.choice(scenario["texts"])
            ch_code = random.choice(CHANNELS)
            ch_id = channel_map.get(ch_code)

            # Randomize reported time within last 25 days
            days_ago = random.uniform(0.1, 25.0)
            reported_at = now - timedelta(days=days_ago, hours=random.uniform(0, 23), minutes=random.uniform(0, 59))

            ticket_num = 840000 + i
            ticket_id = f"TC-{ticket_num}"
            checksum = hashlib.sha256(text_content.encode()).hexdigest()

            f_id = uuid4()
            fi_id = uuid4()
            dec_id = uuid4()

            svc_id = service_map.get(scenario["service_code"])
            iss_id = issue_map.get(scenario["issue_code"])
            step_id, stage_id = step_map.get(scenario["step_code"], (None, None))
            eligibility = "INCLUDED" if scenario["valid"] else "EXCLUDED"
            ex_reason = None if scenario["valid"] else "NON_FEEDBACK"

            metadata = {
                "ticket_id": ticket_id,
                "building": loc_name,
                "location_code": loc_code,
                "channel": ch_code,
                "reported_date": reported_at.strftime("%Y-%m-%d %H:%M:%S"),
                "sentiment": scenario["sentiment"],
                "service_domain": scenario["service_code"],
                "content_masked": text_content,
            }

            feedback_batch.append({
                "feedback_id": f_id,
                "project_id": PROJECT_ID,
                "source_record_key": f"{ticket_id}_{f_id.hex[:6]}",
                "intake_channel_id": ch_id,
                "external_ticket_id": ticket_id,
                "reported_at": reported_at,
                "now": now,
                "content_raw": text_content,
                "content_masked": text_content,
                "source_metadata_json": json.dumps(metadata, ensure_ascii=False),
                "checksum": checksum,
            })

            item_batch.append({
                "feedback_item_id": fi_id,
                "feedback_id": f_id,
                "masked_content": text_content,
                "location_id": loc_id,
                "eligibility": eligibility,
                "reason": ex_reason,
            })

            if svc_id:
                issue_status = "KNOWN" if iss_id else "NOT_APPLICABLE"
                decision_batch.append({
                    "decision_id": dec_id,
                    "feedback_item_id": fi_id,
                    "taxonomy_release_id": taxonomy_release_id,
                    "step_id": step_id,
                    "service_id": svc_id,
                    "issue_status": issue_status,
                    "issue_id": iss_id,
                    "sentiment": scenario["sentiment"],
                    "severity": scenario["severity"],
                    "reported_at": reported_at,
                })

                current_batch.append({
                    "feedback_item_id": fi_id,
                    "decision_id": dec_id,
                    "taxonomy_release_id": taxonomy_release_id,
                    "stage_id": stage_id,
                    "step_id": step_id,
                    "service_id": svc_id,
                    "issue_status": issue_status,
                    "issue_id": iss_id,
                    "sentiment": scenario["sentiment"],
                    "severity": scenario["severity"],
                    "reported_at": reported_at,
                })

            total_count += 1

        print(f"4. Inserting {total_count} records into PostgreSQL...")
        await session.execute(
            text("""
                INSERT INTO feedback (
                    feedback_id, project_id, source_system, source_record_key,
                    intake_channel_id, external_ticket_id,
                    reported_at, ingested_at, content_raw, content_masked,
                    source_metadata_json, raw_content_checksum, created_at
                ) VALUES (
                    :feedback_id, :project_id, 'mock-generator', :source_record_key,
                    :intake_channel_id, :external_ticket_id,
                    :reported_at, :now, :content_raw, :content_masked,
                    CAST(:source_metadata_json AS jsonb), :checksum, :now
                )
            """),
            feedback_batch,
        )

        await session.execute(
            text("""
                INSERT INTO feedback_item (
                    feedback_item_id, feedback_id, item_index, item_text_masked,
                    location_id, status, analytic_eligibility, eligibility_reason
                ) VALUES (
                    :feedback_item_id, :feedback_id, 1, :masked_content,
                    :location_id, 'ACTIVE', :eligibility, :reason
                )
            """),
            item_batch,
        )

        await session.execute(
            text("""
                INSERT INTO classification_decision (
                    classification_decision_id, feedback_item_id, decision_version, taxonomy_release_id,
                    customer_lifecycle_value_status, customer_lifecycle_step_id,
                    service_request_value_status,
                    primary_service_value_status, primary_service_id, issue_value_status, issue_id,
                    sentiment, operational_severity, cause_determination_status, classification_state,
                    decision_source, decision_reason, decided_by, decided_at
                ) VALUES (
                    :decision_id, :feedback_item_id, 1, :taxonomy_release_id,
                    'KNOWN', :step_id, 'NOT_APPLICABLE',
                    'KNOWN', :service_id, :issue_status, :issue_id,
                    :sentiment, :severity, 'NOT_ASSESSED', 'ACCEPTED',
                    'SOURCE_TRUSTED', 'Mock Synthetic Seeder', UUID('00000000-0000-0000-0000-000000000002'), :reported_at
                )
            """),
            decision_batch,
        )

        await session.execute(
            text("""
                INSERT INTO classification_current (
                    feedback_item_id, current_decision_id, current_decision_version, taxonomy_release_id,
                    customer_lifecycle_value_status, customer_lifecycle_stage_id, customer_lifecycle_step_id,
                    service_request_value_status,
                    primary_service_value_status, primary_service_id, issue_value_status, issue_id,
                    sentiment, operational_severity, cause_determination_status, classification_state,
                    last_decision_at, projection_version
                ) VALUES (
                    :feedback_item_id, :decision_id, 1, :taxonomy_release_id,
                    'KNOWN', :stage_id, :step_id, 'NOT_APPLICABLE',
                    'KNOWN', :service_id, :issue_status, :issue_id,
                    :sentiment, :severity, 'NOT_ASSESSED', 'ACCEPTED',
                    :reported_at, 1
                )
            """),
            current_batch,
        )

        await session.commit()
        print(f"5. Seeding completed! Total items: {total_count}")


asyncio.run(seed_data())
