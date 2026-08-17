"""018 — Publish concise dashboard labels in taxonomy v3.0.1.

The v3.0.0 taxonomy remains immutable for historical classification
decisions. This release keeps every code and definition intact, while making
Vietnamese display names concise enough to scan in analytics dashboards.

Revision ID: 018
Revises: 017
Create Date: 2026-08-17
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

revision: str = "018"
down_revision: str | None = "017"
branch_labels = None
depends_on = None

SOURCE_VERSION = "3.0.0"
TARGET_VERSION = "3.0.1"

STEP_LABELS = {
    "A1": "Biết đến dự án", "A2": "Tìm hiểu ban đầu", "A3": "Giới thiệu & ưu đãi",
    "C1": "Tìm hiểu dự án", "C2": "Đánh giá sản phẩm", "C3": "Chọn căn",
    "C4": "Giá & chính sách", "C5": "Khả năng tài chính", "C6": "Tư vấn & tham quan",
    "TR-01": "Giữ chỗ", "TR-02": "Xác minh hồ sơ", "TR-03": "Đặt cọc",
    "TR-04": "Chọn phương án tài chính", "TR-05": "Ký hợp đồng", "TR-06": "Thay đổi sau ký",
    "HO-01": "Chuẩn bị nhận nhà", "HO-02": "Thủ tục nhận nhà", "HO-03": "Kiểm tra căn",
    "HO-04": "Ghi nhận lỗi", "HO-05": "Hoàn tất nhận nhà",
    "RES-01": "Hồ sơ cư dân", "RES-02": "Ứng dụng & kênh cư dân", "RES-03": "Ra vào & di chuyển",
    "RES-04": "Tiếp khách", "RES-05": "Tiện ích cư dân", "RES-06": "Phí & thanh toán",
    "RES-07": "Yêu cầu & phản ánh", "RES-08": "Thay đổi căn hộ",
    "OPS-01": "Tiếp nhận vận hành", "OPS-02": "Kế hoạch & nguồn lực", "OPS-03": "Vận hành & giám sát",
    "OPS-04": "Kiểm tra & bảo trì", "OPS-05": "Sửa chữa & khôi phục", "OPS-06": "Ứng phó khẩn cấp",
    "OPS-07": "Tuân thủ & hiệu suất", "OPS-08": "Cải tiến vận hành",
}

SERVICE_LABELS = {
    "SV-01": "Thông tin & giao dịch", "SV-02": "Tài chính, bàn giao & bảo hành",
    "SV-03": "Hồ sơ & hỗ trợ cư dân", "SV-04": "Hóa đơn & thanh toán",
    "SV-05": "Ra vào & bãi xe", "SV-06": "Tiện ích & chuyển nhà",
    "SV-07": "Kỹ thuật & tài sản chung", "SV-08": "An ninh & khẩn cấp",
    "SV-09": "Vệ sinh & cảnh quan", "SV-10": "Khác",
}

ISSUE_LABELS = {
    "IS-01-01": "Thông tin sai hoặc thiếu", "IS-01-02": "Tư vấn, tham quan & giữ chỗ",
    "IS-01-03": "Hồ sơ/giao dịch chưa hoàn tất", "IS-02-01": "Tài chính & quyết toán",
    "IS-02-02": "Bàn giao & nghiệm thu", "IS-02-03": "Bảo hành & khắc phục",
    "IS-03-01": "Hồ sơ hoặc quyền cư dân", "IS-03-02": "Nền tảng số & case",
    "IS-03-03": "Hỗ trợ & truyền thông", "IS-04-01": "Hóa đơn hoặc phí sai",
    "IS-04-02": "Thanh toán/ghi nhận thất bại", "IS-04-03": "Điều chỉnh/hoàn tiền chậm",
    "IS-05-01": "Ra vào hoặc tiếp khách", "IS-05-02": "Bãi xe", "IS-05-03": "Di chuyển nội khu",
    "IS-06-01": "Đặt hoặc dùng tiện ích", "IS-06-02": "Phê duyệt cải tạo",
    "IS-06-03": "Chuyển vào/chuyển ra", "IS-07-01": "Hệ thống suy giảm",
    "IS-07-02": "Rò rỉ/rủi ro kỹ thuật", "IS-07-03": "Tài sản chung & bảo trì",
    "IS-08-01": "Sự cố an ninh", "IS-08-02": "Giám sát/phản ứng an ninh",
    "IS-08-03": "PCCC & khẩn cấp", "IS-09-01": "Vệ sinh", "IS-09-02": "Rác thải & côn trùng",
    "IS-09-03": "Cảnh quan & môi trường", "IS-10-01": "Vấn đề khác cần review",
}


def _checksum() -> str:
    return hashlib.sha256(json.dumps({
        "source_version": SOURCE_VERSION, "target_version": TARGET_VERSION,
        "step_labels": STEP_LABELS, "service_labels": SERVICE_LABELS, "issue_labels": ISSUE_LABELS,
    }, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _copy_release(conn: sa.Connection, source_id: str, target_id: str) -> None:
    conn.execute(sa.text("""
        INSERT INTO customer_lifecycle_stage
            (customer_lifecycle_stage_id, taxonomy_release_id, stage_code, name_vi, name_en, definition, sort_order, active)
        SELECT gen_random_uuid(), :target_id, stage_code, name_vi, name_en, definition, sort_order, active
        FROM customer_lifecycle_stage WHERE taxonomy_release_id = :source_id
    """), {"source_id": source_id, "target_id": target_id})
    conn.execute(sa.text("""
        INSERT INTO customer_lifecycle_step
            (customer_lifecycle_step_id, taxonomy_release_id, customer_lifecycle_stage_id, step_code, name_vi, name_en, definition, sort_order, active)
        SELECT gen_random_uuid(), :target_id, target_stage.customer_lifecycle_stage_id,
               source_step.step_code, source_step.name_vi, source_step.name_en, source_step.definition,
               source_step.sort_order, source_step.active
        FROM customer_lifecycle_step AS source_step
        JOIN customer_lifecycle_stage AS source_stage
          ON source_stage.customer_lifecycle_stage_id = source_step.customer_lifecycle_stage_id
        JOIN customer_lifecycle_stage AS target_stage
          ON target_stage.taxonomy_release_id = :target_id AND target_stage.stage_code = source_stage.stage_code
        WHERE source_step.taxonomy_release_id = :source_id
    """), {"source_id": source_id, "target_id": target_id})
    conn.execute(sa.text("""
        INSERT INTO service_request_step
            (service_request_step_id, taxonomy_release_id, step_code, name_vi, name_en, definition, sort_order, active)
        SELECT gen_random_uuid(), :target_id, step_code, name_vi, name_en, definition, sort_order, active
        FROM service_request_step WHERE taxonomy_release_id = :source_id
    """), {"source_id": source_id, "target_id": target_id})
    conn.execute(sa.text("""
        INSERT INTO service
            (service_id, taxonomy_release_id, service_code, name_vi, name_en, outcome_definition, in_scope, out_of_scope, default_severity, active)
        SELECT gen_random_uuid(), :target_id, service_code, name_vi, name_en, outcome_definition,
               in_scope, out_of_scope, default_severity, active
        FROM service WHERE taxonomy_release_id = :source_id
    """), {"source_id": source_id, "target_id": target_id})
    conn.execute(sa.text("""
        INSERT INTO issue
            (issue_id, taxonomy_release_id, service_id, issue_code, name_vi, name_en, definition,
             inclusion_examples, exclusion_examples, safety_critical, severity_override, active)
        SELECT gen_random_uuid(), :target_id, target_service.service_id, source_issue.issue_code,
               source_issue.name_vi, source_issue.name_en, source_issue.definition,
               source_issue.inclusion_examples, source_issue.exclusion_examples,
               source_issue.safety_critical, source_issue.severity_override, source_issue.active
        FROM issue AS source_issue
        JOIN service AS source_service ON source_service.service_id = source_issue.service_id
        JOIN service AS target_service
          ON target_service.taxonomy_release_id = :target_id
         AND target_service.service_code = source_service.service_code
        WHERE source_issue.taxonomy_release_id = :source_id
    """), {"source_id": source_id, "target_id": target_id})


def _apply_labels(conn: sa.Connection, target_id: str, table: str, code_column: str, labels: dict[str, str]) -> None:
    statement = sa.text(
        f"UPDATE {table} SET name_vi = :label "
        f"WHERE taxonomy_release_id = :target_id AND {code_column} = :code"
    )
    for code, label in labels.items():
        conn.execute(statement, {"target_id": target_id, "code": code, "label": label})


def upgrade() -> None:
    conn = op.get_bind()
    source_id = conn.execute(sa.text(
        "SELECT taxonomy_release_id FROM taxonomy_release WHERE version = :version"
    ), {"version": SOURCE_VERSION}).scalar_one()
    now = datetime.now(timezone.utc)
    target_id = conn.execute(sa.text("""
        INSERT INTO taxonomy_release
            (taxonomy_release_id, version, status, effective_from, source_checksum,
             notes, approved_by, approved_at, published_by, published_at, created_at, created_by)
        VALUES (gen_random_uuid(), :version, 'PUBLISHED', :now, :checksum,
                :notes, gen_random_uuid(), :now, gen_random_uuid(), :now, :now, gen_random_uuid())
        ON CONFLICT (version) DO NOTHING
        RETURNING taxonomy_release_id
    """), {
        "version": TARGET_VERSION, "now": now, "checksum": _checksum(),
        "notes": "Nhãn dashboard ngắn gọn; mã và định nghĩa kế thừa từ taxonomy 3.0.0.",
    }).scalar_one_or_none()
    if target_id is None:
        return
    target_id = str(target_id)
    _copy_release(conn, str(source_id), target_id)
    _apply_labels(conn, target_id, "customer_lifecycle_step", "step_code", STEP_LABELS)
    _apply_labels(conn, target_id, "service", "service_code", SERVICE_LABELS)
    _apply_labels(conn, target_id, "issue", "issue_code", ISSUE_LABELS)


def downgrade() -> None:
    raise RuntimeError(
        "A published taxonomy release is immutable. Retire v3.0.1 instead of downgrading it."
    )
