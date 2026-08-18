"""019 — Touchpoints, Step-Touchpoint-Service Map and Hotspot Action Priority.

Creates:
  - touchpoint                  (§6.5)
  - touchpoint_service_map      (§6.6)
Adds:
  - action_priority on hotspot
  - touchpoint_id, touchpoint_value_status on classification_current
  - updates analytics_feedback_item_v1 view to expose touchpoint columns
Seeds:
  - canonical touchpoints and step-touchpoint-service mappings for releases 3.0.0 and 3.0.1

Revision ID: 019
Revises: 018
Create Date: 2026-08-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "019"
down_revision: str | None = "018"
branch_labels = None
depends_on = None

FK_ON_DELETE = "RESTRICT"

# Canonical touchpoints data: (step_code, touchpoint_code, name_vi, name_en, definition, primary_service_code, secondary_service_codes)
CANONICAL_TOUCHPOINTS = [
    # A — Nhận thức
    ("A1", "TP-A1-01", "Xem quảng cáo & mạng xã hội", "Digital ads & Social media", "Tiếp cận thông tin dự án qua mạng xã hội, báo chí, quảng cáo số", "SV-01", []),
    ("A1", "TP-A1-02", "Biển bảng & sự kiện ngoài trời", "Outdoor billboards & Events", "Tiếp cận qua billboard, roadshow, sự kiện giới thiệu mở", "SV-01", []),
    ("A2", "TP-A2-01", "Truy cập website & cổng thông tin", "Website & Project portal", "Tìm hiểu thông tin dự án trên website chính thức", "SV-01", []),
    ("A2", "TP-A2-02", "Tra cứu online & diễn đàn", "Search & Online forums", "Đọc đánh giá, thảo luận tại diễn đàn và mạng cộng đồng", "SV-01", []),
    ("A3", "TP-A3-01", "Nhận tin nhắn & cuộc gọi tư vấn", "Outreach SMS & Consultation call", "Nhận cuộc gọi/tin nhắn giới thiệu từ chuyên viên tư vấn", "SV-01", []),
    ("A3", "TP-A3-02", "Nhận tài liệu sự kiện & ưu đãi", "Promotional mail & Event flyer", "Nhận thư mời sự kiện, voucher hoặc chính sách ưu đãi", "SV-01", []),

    # C — Xem xét
    ("C1", "TP-C1-01", "Xem brochure & sa bàn điện tử", "Brochure & Digital masterplan", "Tra cứu tài liệu quy hoạch, mặt bằng tổng thể và sa bàn", "SV-01", []),
    ("C2", "TP-C2-01", "Khảo sát mặt bằng & tiện ích", "Amenities & Layout review", "Tìm hiểu thiết kế căn hộ, tiện ích nội khu và hạ tầng kết nối", "SV-01", ["SV-06"]),
    ("C3", "TP-C3-01", "Xem bảng hàng & chọn mã căn", "Inventory & Unit selection", "Tra cứu quỹ căn mở bán, hướng và tầng căn hộ", "SV-01", []),
    ("C4", "TP-C4-01", "Xem bảng giá & chính sách bán hàng", "Pricing & Sales policy", "Tra cứu đơn giá, chính sách chiết khấu và quà tặng", "SV-01", ["SV-02"]),
    ("C5", "TP-C5-01", "Tư vấn gói vay & lịch thanh toán", "Mortgage & Payment schedule", "Tư vấn phương án tài chính, lãi suất ưu đãi và hạn mức vay", "SV-02", []),
    ("C6", "TP-C6-01", "Tham quan nhà mẫu & dự án thực tế", "Showroom & Site visit", "Trải nghiệm căn hộ mẫu và khảo sát thực địa công trình", "SV-01", []),

    # TR — Giao dịch
    ("TR-01", "TP-TR-01-01", "Nộp phiếu đăng ký giữ chỗ / booking", "Booking request submission", "Đăng ký nguyện vọng chọn mua và nộp tiền giữ chỗ thiện chí", "SV-01", []),
    ("TR-02", "TP-TR-02-01", "Xác minh định danh & hồ sơ khách", "KYC & Profile verification", "Cung cấp CCCD, hồ sơ xác thực và thông tin chủ thể", "SV-01", []),
    ("TR-03", "TP-TR-03-01", "Ký thỏa thuận đặt cọc & nộp tiền cọc", "Deposit agreement signing", "Ký thỏa thuận đặt cọc chính thức và thanh toán đợt 1", "SV-01", ["SV-02"]),
    ("TR-04", "TP-TR-04-01", "Xác nhận phương án tài chính & giải ngân", "Loan disbursement confirmation", "Hoàn thiện hồ sơ ngân hàng bảo lãnh và lịch giải ngân", "SV-02", []),
    ("TR-05", "TP-TR-05-01", "Ký hợp đồng mua bán tại văn phòng", "Sales contract signing", "Ký hợp đồng mua bán chính thức tại phòng thủ tục giao dịch", "SV-01", ["SV-02"]),
    ("TR-06", "TP-TR-06-01", "Đề nghị chuyển nhượng & sửa đổi sau ký", "Post-contract amendment request", "Yêu cầu thay đổi thông tin, chuyển nhượng hoặc ký phụ lục", "SV-01", []),

    # HO — Nhận nhà
    ("HO-01", "TP-HO-01-01", "Nhận thông báo bàn giao & hướng dẫn", "Handover notice & Guide", "Nhận thông báo bàn giao căn hộ qua email/thư/app", "SV-02", []),
    ("HO-02", "TP-HO-02-01", "Làm thủ tục check-in bàn giao", "Handover check-in procedure", "Tiếp đón và đối chiếu hồ sơ tại văn phòng bàn giao", "SV-02", []),
    ("HO-03", "TP-HO-03-01", "Kiểm tra & nghiệm thu căn hộ", "Unit inspection with technician", "Cùng kỹ sư kiểm tra hoàn thiện, điện nước và trang thiết bị", "SV-02", ["SV-07"]),
    ("HO-04", "TP-HO-04-01", "Ghi nhận tồn đọng & hẹn khắc phục", "Defect logging & Remediation SLA", "Lập biên bản ghi nhận lỗi kỹ thuật cần bảo hành khắc phục", "SV-02", ["SV-07"]),
    ("HO-05", "TP-HO-05-01", "Nhận bàn giao chìa khóa & hồ sơ căn", "Key handover & Resident packet", "Nhận chìa khóa, thẻ cư dân tạm và sổ tay hướng dẫn", "SV-02", ["SV-03"]),

    # RES — Cư trú
    ("RES-01", "TP-RES-01-01", "Đăng ký cư dân & nhân khẩu", "Resident registration & Profiles", "Khai báo cư dân, đăng ký tạm trú và cấp thẻ từ", "SV-03", []),
    ("RES-02", "TP-RES-02-01", "Gửi yêu cầu & tra cứu trên app", "Resident app ticket & notices", "Gửi phản ánh hoặc nhận thông báo qua ứng dụng cư dân", "SV-03", []),
    ("RES-02", "TP-RES-02-02", "Tra cứu tin tức & thông báo BQL", "Management board announcements", "Xem bảng tin tòa nhà và thông báo vận hành", "SV-03", []),
    ("RES-03", "TP-RES-03-01", "Quét thẻ & cổng ra vào tòa nhà", "Access turnstile & Card scan", "Quẹt thẻ sảnh, cổng kiểm soát an ninh ra vào", "SV-05", []),
    ("RES-03", "TP-RES-03-02", "Gửi & nhận xe tại bãi", "Parking check-in/out & Slots", "Quẹt thẻ gửi xe, tìm vị trí đỗ và sạc xe điện", "SV-05", []),
    ("RES-03", "TP-RES-03-03", "Sử dụng thang máy & sảnh chung", "Elevator & Common lobby", "Trải nghiệm di chuyển thang máy, điều hòa sảnh chờ", "SV-05", ["SV-07"]),
    ("RES-04", "TP-RES-04-01", "Đăng ký khách & người giao hàng", "Guest & Delivery registration", "Đăng ký cho khách lên căn hộ hoặc tiếp nhận bưu phẩm", "SV-05", ["SV-08"]),
    ("RES-05", "TP-RES-05-01", "Đặt & sử dụng hồ bơi / phòng gym", "Pool & Gym booking/usage", "Đăng ký lịch tập gym, bơi lội và tiện ích thể thao", "SV-06", []),
    ("RES-05", "TP-RES-05-02", "Đăng ký khu BBQ & phòng sinh hoạt", "BBQ & Community room booking", "Đặt chỗ tổ chức tiệc BBQ, phòng cộng đồng", "SV-06", []),
    ("RES-06", "TP-RES-06-01", "Nhận thông báo hóa đơn phí quản lý", "Management fee billing notice", "Nhận bảng kê phí dịch vụ, điện nước, gửi xe hằng tháng", "SV-04", []),
    ("RES-06", "TP-RES-06-02", "Thanh toán phí qua app / chuyển khoản", "Fee payment gateway / Transfer", "Thực hiện thanh toán online hoặc đối soát công nợ", "SV-04", []),
    ("RES-07", "TP-RES-07-01", "Báo lỗi kỹ thuật & thiết bị chung", "Engineering defect report", "Báo hỏng điện, nước, thấm dột, mùi hôi hoặc thiết bị", "SV-07", []),
    ("RES-07", "TP-RES-07-02", "Báo an ninh, tiếng ồn & PCCC", "Security, Noise & Fire safety alert", "Báo mất an ninh, ồn ào đêm muộn hoặc chuông báo cháy", "SV-08", []),
    ("RES-07", "TP-RES-07-03", "Phản ánh vệ sinh & cảnh quan", "Cleanliness & Landscaping feedback", "Phản ánh rác thải, vệ sinh hành lang, chăm sóc cây xanh", "SV-09", []),
    ("RES-08", "TP-RES-08-01", "Đăng ký thi công sửa chữa nội thất", "Fit-out & Renovation permit", "Nộp hồ sơ cấp phép thi công và ký quỹ sửa chữa", "SV-06", ["SV-07"]),
    ("RES-08", "TP-RES-08-02", "Đăng ký chuyển đồ & chuyển nhà", "Move-in/out elevator booking", "Đăng ký khung giờ dùng thang hàng và bảo vệ tài sản", "SV-06", []),

    # OPS — Vận hành
    ("OPS-01", "TP-OPS-01-01", "Tiếp nhận bàn giao tài sản CĐT", "Asset handover from developer", "Kiểm kê danh mục trang thiết bị hạ tầng kỹ thuật", "SV-07", []),
    ("OPS-02", "TP-OPS-02-01", "Lập lịch trực & phân bổ ca làm việc", "Duty roster & Staff shift dispatch", "Bố trí lực lượng an ninh, lễ tân, kỹ thuật và vệ sinh", "SV-07", ["SV-08"]),
    ("OPS-03", "TP-OPS-03-01", "Trực phòng điều khiển & camera an ninh", "Control room & CCTV monitoring", "Giám sát hệ thống BMS, PCCC và camera 24/7", "SV-08", []),
    ("OPS-04", "TP-OPS-04-01", "Tuần tra định kỳ & bảo dưỡng thiết bị", "Routine patrol & Preventive maintenance", "Bảo dưỡng máy bơm, máy phát điện, thang máy định kỳ", "SV-07", []),
    ("OPS-05", "TP-OPS-05-01", "Xử lý sự cố kỹ thuật hạ tầng", "Infrastructure breakdown response", "Ứng phó sự cố mất điện, vỡ ống nước hoặc kẹt thang", "SV-07", []),
    ("OPS-06", "TP-OPS-06-01", "Kích hoạt quy trình PCCC & khẩn cấp", "Emergency & Fire safety activation", "Kích hoạt báo động, hướng dẫn thoát nạn và cứu hộ", "SV-08", []),
    ("OPS-07", "TP-OPS-07-01", "Đánh giá chất lượng dịch vụ nhà thầu", "Vendor SLA & Quality audit", "Nghiệm thu dịch vụ vệ sinh, an ninh và cây xanh", "SV-07", ["SV-08", "SV-09"]),
    ("OPS-08", "TP-OPS-08-01", "Đề xuất cải tiến vận hành & tiện ích", "Operations improvement initiative", "Khảo sát và lập phương án tối ưu chi phí và chất lượng", "SV-07", ["SV-10"]),
]

_VIEW_SQL_V2 = """
CREATE OR REPLACE VIEW analytics_feedback_item_v1 AS
SELECT
    fi.feedback_item_id,
    fi.feedback_id,
    f.project_id,
    f.reported_at,
    f.source_system,
    f.intake_channel_id,
    fi.location_id,
    loc.location_code,
    loc.location_type,
    loc.name AS location_name,

    cc.taxonomy_release_id,

    cc.customer_lifecycle_value_status,
    cc.customer_lifecycle_stage_id,
    cls.stage_code AS customer_lifecycle_stage_code,
    cls.name_vi AS customer_lifecycle_stage_name_vi,
    cc.customer_lifecycle_step_id,
    clst.step_code AS customer_lifecycle_step_code,
    clst.name_vi AS customer_lifecycle_step_name_vi,

    -- Touchpoint dimension
    cc.touchpoint_id,
    tp.touchpoint_code,
    tp.name_vi AS touchpoint_name_vi,

    cc.service_request_value_status,
    cc.service_request_step_id,
    srs.step_code AS service_request_step_code,
    srs.name_vi AS service_request_step_name_vi,

    cc.primary_service_value_status,
    cc.primary_service_id,
    svc.service_code,
    svc.name_vi AS service_name_vi,
    svc.name_en AS service_name_en,
    svc.default_severity AS service_default_severity,

    cc.issue_value_status,
    cc.issue_id,
    iss.issue_code,
    iss.name_vi AS issue_name_vi,
    iss.name_en AS issue_name_en,
    iss.safety_critical,

    cc.sentiment,
    cc.operational_severity,
    cc.cause_determination_status,
    cc.other_reason,
    cc.classification_state,

    cc.current_decision_id,
    cc.current_decision_version,
    cc.last_decision_at,
    cc.projection_version,

    intake_channel.channel_code AS intake_channel_code,
    loc.path_code AS location_path_code,
    ARRAY(
        SELECT ac.channel_code
        FROM feedback_item_affected_channel fiac
        JOIN interaction_channel ac ON ac.interaction_channel_id = fiac.interaction_channel_id
        WHERE fiac.feedback_item_id = fi.feedback_item_id
    ) AS affected_channel_codes

FROM feedback_item fi

INNER JOIN feedback f
    ON f.feedback_id = fi.feedback_id

INNER JOIN classification_current cc
    ON cc.feedback_item_id = fi.feedback_item_id

LEFT JOIN customer_lifecycle_stage cls
    ON cls.customer_lifecycle_stage_id = cc.customer_lifecycle_stage_id

LEFT JOIN customer_lifecycle_step clst
    ON clst.customer_lifecycle_step_id = cc.customer_lifecycle_step_id

LEFT JOIN touchpoint tp
    ON tp.touchpoint_id = cc.touchpoint_id

LEFT JOIN service_request_step srs
    ON srs.service_request_step_id = cc.service_request_step_id

LEFT JOIN service svc
    ON svc.service_id = cc.primary_service_id

LEFT JOIN issue iss
    ON iss.issue_id = cc.issue_id

LEFT JOIN location loc
    ON loc.location_id = fi.location_id

LEFT JOIN interaction_channel AS intake_channel
    ON intake_channel.interaction_channel_id = f.intake_channel_id

WHERE
    fi.status = 'ACTIVE'
    AND fi.analytic_eligibility = 'INCLUDED'
    AND cc.current_decision_id IS NOT NULL
    AND cc.classification_state = 'ACCEPTED';
"""

_DOWNGRADE_VIEW_SQL = """
CREATE OR REPLACE VIEW analytics_feedback_item_v1 AS
SELECT
    fi.feedback_item_id,
    fi.feedback_id,
    f.project_id,
    f.reported_at,
    f.source_system,
    f.intake_channel_id,
    fi.location_id,
    loc.location_code,
    loc.location_type,
    loc.name AS location_name,

    cc.taxonomy_release_id,

    cc.customer_lifecycle_value_status,
    cc.customer_lifecycle_stage_id,
    cls.stage_code AS customer_lifecycle_stage_code,
    cls.name_vi AS customer_lifecycle_stage_name_vi,
    cc.customer_lifecycle_step_id,
    clst.step_code AS customer_lifecycle_step_code,
    clst.name_vi AS customer_lifecycle_step_name_vi,

    cc.service_request_value_status,
    cc.service_request_step_id,
    srs.step_code AS service_request_step_code,
    srs.name_vi AS service_request_step_name_vi,

    cc.primary_service_value_status,
    cc.primary_service_id,
    svc.service_code,
    svc.name_vi AS service_name_vi,
    svc.name_en AS service_name_en,
    svc.default_severity AS service_default_severity,

    cc.issue_value_status,
    cc.issue_id,
    iss.issue_code,
    iss.name_vi AS issue_name_vi,
    iss.name_en AS issue_name_en,
    iss.safety_critical,

    cc.sentiment,
    cc.operational_severity,
    cc.cause_determination_status,
    cc.other_reason,
    cc.classification_state,

    cc.current_decision_id,
    cc.current_decision_version,
    cc.last_decision_at,
    cc.projection_version,

    intake_channel.channel_code AS intake_channel_code,
    loc.path_code AS location_path_code,
    COALESCE(affected_channels.affected_channel_codes, ARRAY[]::varchar[])
        AS affected_channel_codes
FROM feedback_item fi
INNER JOIN feedback f
    ON f.feedback_id = fi.feedback_id
INNER JOIN classification_current cc
    ON cc.feedback_item_id = fi.feedback_item_id
LEFT JOIN interaction_channel intake_channel
    ON intake_channel.interaction_channel_id = f.intake_channel_id
LEFT JOIN location loc
    ON loc.location_id = fi.location_id
LEFT JOIN LATERAL (
    SELECT ARRAY_AGG(DISTINCT affected_channel.channel_code ORDER BY affected_channel.channel_code)
        AS affected_channel_codes
    FROM feedback_item_affected_channel fiac
    INNER JOIN interaction_channel affected_channel
        ON affected_channel.interaction_channel_id = fiac.interaction_channel_id
    WHERE fiac.feedback_item_id = fi.feedback_item_id
) affected_channels ON TRUE
LEFT JOIN customer_lifecycle_stage cls
    ON cls.customer_lifecycle_stage_id = cc.customer_lifecycle_stage_id
LEFT JOIN customer_lifecycle_step clst
    ON clst.customer_lifecycle_step_id = cc.customer_lifecycle_step_id
LEFT JOIN service_request_step srs
    ON srs.service_request_step_id = cc.service_request_step_id
LEFT JOIN service svc
    ON svc.service_id = cc.primary_service_id
LEFT JOIN issue iss
    ON iss.issue_id = cc.issue_id
WHERE fi.status = 'ACTIVE'
  AND fi.analytic_eligibility = 'INCLUDED'
  AND cc.current_decision_id IS NOT NULL
  AND cc.classification_state = 'ACCEPTED';
"""


def upgrade() -> None:
    # 1. Create touchpoint table
    op.create_table(
        "touchpoint",
        sa.Column("touchpoint_id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("taxonomy_release_id", sa.UUID(as_uuid=True), sa.ForeignKey("taxonomy_release.taxonomy_release_id", name="fk_tp_release", ondelete=FK_ON_DELETE), nullable=False),
        sa.Column("customer_lifecycle_step_id", sa.UUID(as_uuid=True), sa.ForeignKey("customer_lifecycle_step.customer_lifecycle_step_id", name="fk_tp_step", ondelete=FK_ON_DELETE), nullable=False),
        sa.Column("touchpoint_code", sa.String(32), nullable=False),
        sa.Column("name_vi", sa.String(255), nullable=False),
        sa.Column("name_en", sa.String(255), nullable=True),
        sa.Column("definition", sa.Text, nullable=True),
        sa.Column("sort_order", sa.SmallInteger, nullable=False, server_default=sa.text("0")),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("active_from", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("active_to", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("taxonomy_release_id", "touchpoint_code", name="uq_tp_release_code"),
    )
    op.create_index("ix_tp_release", "touchpoint", ["taxonomy_release_id"])
    op.create_index("ix_tp_step", "touchpoint", ["customer_lifecycle_step_id"])

    # 2. Create touchpoint_service_map table
    op.create_table(
        "touchpoint_service_map",
        sa.Column("touchpoint_service_map_id", sa.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("taxonomy_release_id", sa.UUID(as_uuid=True), sa.ForeignKey("taxonomy_release.taxonomy_release_id", name="fk_tsm_release", ondelete=FK_ON_DELETE), nullable=False),
        sa.Column("touchpoint_id", sa.UUID(as_uuid=True), sa.ForeignKey("touchpoint.touchpoint_id", name="fk_tsm_tp", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", sa.UUID(as_uuid=True), sa.ForeignKey("service.service_id", name="fk_tsm_service", ondelete=FK_ON_DELETE), nullable=False),
        sa.Column("mapping_type", sa.String(16), nullable=False, server_default="PRIMARY"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("taxonomy_release_id", "touchpoint_id", "service_id", name="uq_tsm_release_tp_svc"),
        sa.CheckConstraint("mapping_type IN ('PRIMARY', 'SECONDARY')", name="ck_tsm_mapping_type"),
    )
    op.create_index("ix_tsm_tp", "touchpoint_service_map", ["touchpoint_id"])
    op.create_index("ix_tsm_service", "touchpoint_service_map", ["service_id"])

    # 3. Add action_priority to hotspot table
    op.add_column(
        "hotspot",
        sa.Column("action_priority", sa.String(16), nullable=False, server_default="MONITOR"),
    )
    op.create_check_constraint(
        "ck_hotspot_action_priority",
        "hotspot",
        "action_priority IN ('IMMEDIATE', 'URGENT', 'PLANNED', 'MONITOR')",
    )
    op.create_index("ix_hotspot_priority_status", "hotspot", ["project_id", "action_priority", "status"])

    # 4. Add touchpoint_id to classification_current
    op.add_column(
        "classification_current",
        sa.Column("touchpoint_id", sa.UUID(as_uuid=True), sa.ForeignKey("touchpoint.touchpoint_id", name="fk_cc_touchpoint", ondelete="SET NULL"), nullable=True),
    )
    op.add_column(
        "classification_current",
        sa.Column("touchpoint_value_status", sa.String(16), nullable=False, server_default="UNKNOWN"),
    )
    op.create_index("ix_cc_touchpoint", "classification_current", ["touchpoint_id"])

    # 5. Update analytics_feedback_item_v1 view
    op.execute("DROP VIEW IF EXISTS analytics_feedback_item_v1 CASCADE;")
    op.execute(_VIEW_SQL_V2)

    # 6. Seed Touchpoints and Step-Touchpoint-Service Mappings
    bind = op.get_bind()
    releases = bind.execute(sa.text("SELECT taxonomy_release_id, version FROM taxonomy_release")).fetchall()

    for release_row in releases:
        rel_id = release_row[0]
        steps = bind.execute(
            sa.text("SELECT customer_lifecycle_step_id, step_code FROM customer_lifecycle_step WHERE taxonomy_release_id = :rel_id"),
            {"rel_id": rel_id},
        ).fetchall()
        step_map = {row[1]: row[0] for row in steps}

        services = bind.execute(
            sa.text("SELECT service_id, service_code FROM service WHERE taxonomy_release_id = :rel_id"),
            {"rel_id": rel_id},
        ).fetchall()
        svc_map = {row[1]: row[0] for row in services}

        for sort_idx, (step_code, tp_code, name_vi, name_en, definition, prim_svc_code, sec_svc_codes) in enumerate(CANONICAL_TOUCHPOINTS, start=1):
            step_id = step_map.get(step_code)
            if not step_id:
                continue

            tp_res = bind.execute(
                sa.text("""
                    INSERT INTO touchpoint (
                        taxonomy_release_id, customer_lifecycle_step_id, touchpoint_code,
                        name_vi, name_en, definition, sort_order, active
                    ) VALUES (
                        :rel_id, :step_id, :tp_code, :name_vi, :name_en, :definition, :sort_order, true
                    )
                    ON CONFLICT (taxonomy_release_id, touchpoint_code) DO UPDATE
                    SET name_vi = EXCLUDED.name_vi, name_en = EXCLUDED.name_en, definition = EXCLUDED.definition
                    RETURNING touchpoint_id
                """),
                {
                    "rel_id": rel_id,
                    "step_id": step_id,
                    "tp_code": tp_code,
                    "name_vi": name_vi,
                    "name_en": name_en,
                    "definition": definition,
                    "sort_order": sort_idx,
                },
            )
            tp_id = tp_res.fetchone()[0]

            prim_svc_id = svc_map.get(prim_svc_code)
            if prim_svc_id:
                bind.execute(
                    sa.text("""
                        INSERT INTO touchpoint_service_map (
                            taxonomy_release_id, touchpoint_id, service_id, mapping_type, active
                        ) VALUES (
                            :rel_id, :tp_id, :svc_id, 'PRIMARY', true
                        )
                        ON CONFLICT (taxonomy_release_id, touchpoint_id, service_id) DO NOTHING
                    """),
                    {"rel_id": rel_id, "tp_id": tp_id, "svc_id": prim_svc_id},
                )

            for sec_svc_code in sec_svc_codes:
                sec_svc_id = svc_map.get(sec_svc_code)
                if sec_svc_id:
                    bind.execute(
                        sa.text("""
                            INSERT INTO touchpoint_service_map (
                                taxonomy_release_id, touchpoint_id, service_id, mapping_type, active
                            ) VALUES (
                                :rel_id, :tp_id, :svc_id, 'SECONDARY', true
                            )
                            ON CONFLICT (taxonomy_release_id, touchpoint_id, service_id) DO NOTHING
                        """),
                        {"rel_id": rel_id, "tp_id": tp_id, "svc_id": sec_svc_id},
                    )


def downgrade() -> None:
    # 1. Restore previous analytics semantic view without touchpoints first
    op.execute(_DOWNGRADE_VIEW_SQL)

    # 2. Drop classification_current columns
    op.drop_index("ix_cc_touchpoint", table_name="classification_current")
    op.drop_column("classification_current", "touchpoint_value_status")
    op.drop_column("classification_current", "touchpoint_id")

    # 3. Drop hotspot columns
    op.drop_index("ix_hotspot_priority_status", table_name="hotspot")
    op.drop_constraint("ck_hotspot_action_priority", table_name="hotspot", type_="check")
    op.drop_column("hotspot", "action_priority")

    # 4. Drop touchpoint_service_map table
    op.drop_index("ix_tsm_service", table_name="touchpoint_service_map")
    op.drop_index("ix_tsm_tp", table_name="touchpoint_service_map")
    op.drop_table("touchpoint_service_map")

    # 5. Drop touchpoint table
    op.drop_index("ix_tp_step", table_name="touchpoint")
    op.drop_index("ix_tp_release", table_name="touchpoint")
    op.drop_table("touchpoint")
