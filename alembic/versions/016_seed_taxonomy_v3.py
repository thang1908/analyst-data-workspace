"""016 — Seed Taxonomy v3.0.0.

Seeds the complete canonical taxonomy for version 3.0.0:
  - taxonomy_release (1 record, PUBLISHED)
  - customer_lifecycle_stage (6 stages)
  - customer_lifecycle_step (36 steps)
  - service_request_step (8 steps: SRV-01..SRV-08)
  - service (10 services: SV-01..SV-10)
  - issue (28 issues)
  - interaction_channel (8 canonical channels)

Release gates verified (§22):
  ✓ 6 Customer Lifecycle stages
  ✓ 36 Customer Lifecycle steps
  ✓ 8 Service Request steps
  ✓ 10 active Services
  ✓ 28 active Issues (SV-01..SV-09: 3 each; SV-10: 1)

Revision ID: 016
Revises: 015
Create Date: 2026-08-12
Issue: #4  Branch: feature/m0-004-views-indexes-seed
"""

from __future__ import annotations

import hashlib
import json

from alembic import op

revision: str = "016"
down_revision: str | None = "015"
branch_labels = None
depends_on = None

# ── Seed data ─────────────────────────────────────────────────────────────── #

TAXONOMY_VERSION = "3.0.0"

STAGES = [
    {"code": "A",   "name_vi": "Nhận thức",   "name_en": "Awareness",    "sort_order": 1},
    {"code": "C",   "name_vi": "Xem xét",     "name_en": "Consideration","sort_order": 2},
    {"code": "TR",  "name_vi": "Giao dịch",   "name_en": "Transaction",  "sort_order": 3},
    {"code": "HO",  "name_vi": "Nhận nhà",    "name_en": "Handover",     "sort_order": 4},
    {"code": "RES", "name_vi": "Cư trú",      "name_en": "Residence",    "sort_order": 5},
    {"code": "OPS", "name_vi": "Vận hành",    "name_en": "Operations",   "sort_order": 6},
]

# steps: list of (stage_code, step_code, name_vi, sort_order)
STEPS = [
    # Awareness
    ("A",   "A1",     "Tiếp cận thương hiệu/dự án", 1),
    ("A",   "A2",     "Khám phá nội dung & thông tin ban đầu", 2),
    ("A",   "A3",     "Nhận giới thiệu / tham gia hoạt động quảng bá", 3),
    # Consideration
    ("C",   "C1",     "Tìm hiểu dự án & sản phẩm", 1),
    ("C",   "C2",     "Đánh giá vị trí, thiết kế & tiện ích", 2),
    ("C",   "C3",     "Xem quỹ căn & so sánh lựa chọn", 3),
    ("C",   "C4",     "Đánh giá pháp lý, giá & chính sách", 4),
    ("C",   "C5",     "Đánh giá khả năng tài chính", 5),
    ("C",   "C6",     "Nhận tư vấn & tham quan", 6),
    # Transaction
    ("TR",  "TR-01",  "Yêu cầu giữ căn hoặc gửi booking", 1),
    ("TR",  "TR-02",  "Xác minh khách hàng & hồ sơ", 2),
    ("TR",  "TR-03",  "Đặt cọc & xác nhận giao dịch", 3),
    ("TR",  "TR-04",  "Chọn phương án tài chính & thanh toán", 4),
    ("TR",  "TR-05",  "Ký hợp đồng mua bán", 5),
    ("TR",  "TR-06",  "Thực hiện nghĩa vụ & thay đổi sau ký", 6),
    # Handover
    ("HO",  "HO-01",  "Nhận thông báo & chuẩn bị bàn giao", 1),
    ("HO",  "HO-02",  "Đặt lịch & làm thủ tục bàn giao", 2),
    ("HO",  "HO-03",  "Kiểm tra & nghiệm thu căn", 3),
    ("HO",  "HO-04",  "Ghi nhận tồn tại / yêu cầu khắc phục", 4),
    ("HO",  "HO-05",  "Hoàn tất nhận nhà & hồ sơ", 5),
    # Residence
    ("RES", "RES-01", "Thiết lập hồ sơ & quyền cư dân", 1),
    ("RES", "RES-02", "Sử dụng hệ thống & kênh cư dân", 2),
    ("RES", "RES-03", "Ra vào & di chuyển", 3),
    ("RES", "RES-04", "Tiếp khách", 4),
    ("RES", "RES-05", "Sử dụng tiện ích & dịch vụ", 5),
    ("RES", "RES-06", "Thanh toán phí & nghĩa vụ cư trú", 6),
    ("RES", "RES-07", "Gửi yêu cầu / phản ánh / sự cố", 7),
    ("RES", "RES-08", "Thực hiện thay đổi liên quan căn hộ", 8),
    # Operations
    ("OPS", "OPS-01", "Tiếp nhận & huy động vận hành", 1),
    ("OPS", "OPS-02", "Lập kế hoạch, ngân sách & nguồn lực", 2),
    ("OPS", "OPS-03", "Vận hành thường nhật & giám sát", 3),
    ("OPS", "OPS-04", "Kiểm tra, thử nghiệm & bảo trì định kỳ", 4),
    ("OPS", "OPS-05", "Chẩn đoán, sửa chữa & khôi phục", 5),
    ("OPS", "OPS-06", "Ứng phó sự cố, khẩn cấp & duy trì liên tục", 6),
    ("OPS", "OPS-07", "Xác minh, tuân thủ & đánh giá hiệu suất", 7),
    ("OPS", "OPS-08", "Cải tiến, đổi mới & chuyển giao", 8),
]

SERVICE_REQUEST_STEPS = [
    ("SRV-01", "Tìm thông tin",        "Find Information",           1),
    ("SRV-02", "Gửi yêu cầu",          "Submit Request",             2),
    ("SRV-03", "Xác nhận/phê duyệt",   "Confirm / Approve",          3),
    ("SRV-04", "Thanh toán",            "Payment",                    4),
    ("SRV-05", "Được phục vụ",          "Service Delivered",          5),
    ("SRV-06", "Theo dõi/escalate",     "Track / Escalate",           6),
    ("SRV-07", "Hoàn tất",              "Complete",                   7),
    ("SRV-08", "Đánh giá",              "Rate & Review",              8),
]

# services: (code, name_vi, name_en, outcome_definition, default_severity)
SERVICES = [
    ("SV-01", "Thông tin, bán hàng & giao dịch",
     "Information, Sales & Transaction",
     "Khách hàng nhận thông tin chính xác, hoàn tất giao dịch và ký kết hợp đồng.",
     "SEV-4"),
    ("SV-02", "Tài chính mua nhà, bàn giao & bảo hành",
     "Purchase Finance, Handover & Warranty",
     "Khách hàng hoàn tất nghĩa vụ tài chính, nhận nhà đúng tiêu chuẩn và được bảo hành.",
     "SEV-3"),
    ("SV-03", "Hồ sơ, hỗ trợ & trải nghiệm số cư dân",
     "Resident Administration, Support & Digital",
     "Cư dân có hồ sơ chính xác, truy cập nền tảng số và nhận hỗ trợ kịp thời.",
     "SEV-4"),
    ("SV-04", "Hóa đơn, phí & thanh toán cư dân",
     "Resident Billing & Payments",
     "Cư dân nhận hóa đơn chính xác và thanh toán thành công.",
     "SEV-3"),
    ("SV-05", "Ra vào, khách, bãi xe & di chuyển",
     "Access, Visitor, Parking & Mobility",
     "Cư dân và khách ra vào, đỗ xe và di chuyển nội khu an toàn và thuận tiện.",
     "SEV-2"),
    ("SV-06", "Tiện ích, cải tạo & chuyển nhà",
     "Amenities, Renovation & Move Services",
     "Cư dân sử dụng tiện ích, thực hiện cải tạo và chuyển nhà đúng quy trình.",
     "SEV-4"),
    ("SV-07", "Kỹ thuật, tiện ích & tài sản chung",
     "Engineering, Utilities & Common Assets",
     "Hệ thống kỹ thuật và tài sản chung hoạt động liên tục, an toàn và đúng tiêu chuẩn.",
     "SEV-1"),
    ("SV-08", "An ninh, PCCC & khẩn cấp",
     "Security, Fire & Emergency",
     "Tài sản và con người được bảo vệ; sự cố được phát hiện và xử lý kịp thời.",
     "SEV-1"),
    ("SV-09", "Vệ sinh, môi trường & cảnh quan",
     "Cleaning, Environment & Grounds",
     "Môi trường sạch, an toàn vệ sinh và cảnh quan được duy trì đúng tiêu chuẩn.",
     "SEV-3"),
    ("SV-10", "Khác",
     "Other",
     "Nội dung rõ nhưng không thuộc SV-01..SV-09; bắt buộc có other_reason và review.",
     "SEV-4"),
]

# issues: (service_code, issue_code, name_vi, name_en, definition, safety_critical)
ISSUES = [
    # SV-01
    ("SV-01", "IS-01-01",
     "Thông tin thiếu hoặc không chính xác",
     "Information Missing or Inaccurate",
     "Project, product, legal, policy, price hoặc content unavailable/stale.", False),
    ("SV-01", "IS-01-02",
     "Tư vấn, tham quan hoặc giữ chỗ không đạt",
     "Advisory, Viewing or Reservation Failure",
     "Contact, appointment, availability, booking, duplicate hoặc confirmation.", False),
    ("SV-01", "IS-01-03",
     "Hồ sơ hoặc giao dịch không hoàn tất",
     "Dossier or Transaction Failure",
     "KYC, document, contract data, e-sign, amendment hoặc transfer.", False),
    # SV-02
    ("SV-02", "IS-02-01",
     "Tài chính hoặc quyết toán mua nhà có vấn đề",
     "Purchase Finance or Settlement Failure",
     "Loan, payment, allocation, due amount, adjustment hoặc refund.", False),
    ("SV-02", "IS-02-02",
     "Bàn giao hoặc nghiệm thu không đạt",
     "Handover or Acceptance Failure",
     "Readiness, schedule, inspection, area, defect capture hoặc acceptance.", False),
    ("SV-02", "IS-02-03",
     "Bảo hành hoặc khắc phục không đạt",
     "Warranty or Remediation Failure",
     "Scope unclear, delay, ineffective repair, recurrence hoặc invalid closure.", False),
    # SV-03
    ("SV-03", "IS-03-01",
     "Hồ sơ hoặc quyền cư dân sai",
     "Resident Record or Entitlement Incorrect",
     "Household/unit/profile/role/account status.", False),
    ("SV-03", "IS-03-02",
     "Nền tảng số hoặc case handling lỗi",
     "Digital Platform or Case Handling Failure",
     "Login, OTP, crash, API, missing/duplicate case, wrong owner, premature closure.", False),
    ("SV-03", "IS-03-03",
     "Hỗ trợ hoặc truyền thông không đạt",
     "Support or Communication Failure",
     "Response, audience, timing, clarity, follow-up hoặc notification.", False),
    # SV-04
    ("SV-04", "IS-04-01",
     "Hóa đơn hoặc phí sai",
     "Charge or Invoice Incorrect",
     "Tariff, amount, penalty hoặc duplicate.", False),
    ("SV-04", "IS-04-02",
     "Thanh toán hoặc ghi nhận thất bại",
     "Payment or Posting Failure",
     "Gateway, bank, callback, reference, allocation hoặc reconciliation.", False),
    ("SV-04", "IS-04-03",
     "Điều chỉnh hoặc hoàn tiền chậm",
     "Adjustment or Refund Delay",
     "Adjustment, deposit settlement, refund hoặc document issuance delay.", False),
    # SV-05
    ("SV-05", "IS-05-01",
     "Ra vào hoặc hành trình khách thất bại",
     "Access or Visitor Failure",
     "Card, Face ID, floor permission, intercom, registration hoặc check-in.", False),
    ("SV-05", "IS-05-02",
     "Dịch vụ bãi xe không đạt",
     "Parking Service Failure",
     "LPR, barrier, entitlement, capacity, congestion hoặc availability.", False),
    ("SV-05", "IS-05-03",
     "Di chuyển nội khu không đạt",
     "Estate Mobility Failure",
     "Route, stop, schedule, realtime information, missed trip hoặc capacity.", False),
    # SV-06
    ("SV-06", "IS-06-01",
     "Tiện ích không đặt hoặc sử dụng được",
     "Amenity Reservation or Use Failure",
     "Booking, slot, eligibility, admission, opening status hoặc equipment.", False),
    ("SV-06", "IS-06-02",
     "Phê duyệt hoặc kiểm soát cải tạo không đạt",
     "Renovation Approval or Compliance Failure",
     "Dossier, approval, contractor, schedule, access, noise hoặc damage assessment.", False),
    ("SV-06", "IS-06-03",
     "Chuyển vào/chuyển ra không đạt",
     "Move Service Failure",
     "Registration, loading bay, freight lift, vehicle, contractor hoặc logistics.", False),
    # SV-07
    ("SV-07", "IS-07-01",
     "Hệ thống ngừng hoặc suy giảm",
     "System Outage or Degradation",
     "Elevator, water, electrical, generator, HVAC outage/performance/quality.", False),
    ("SV-07", "IS-07-02",
     "Rò rỉ hoặc điều kiện kỹ thuật nguy hiểm",
     "Leakage or Unsafe Technical Condition",
     "Leak, blockage, flooding, entrapment, abnormal stop, overheat, burning smell.", True),
    ("SV-07", "IS-07-03",
     "Tài sản chung hoặc bảo trì không đạt",
     "Common Asset or Maintenance Failure",
     "Fabric defect, preventive/capital work, inspection, vendor/compliance record.", False),
    # SV-08
    ("SV-08", "IS-08-01",
     "Sự kiện an ninh",
     "Security Incident",
     "Unauthorized access, theft, suspicious behavior, disturbance hoặc threat.", True),
    ("SV-08", "IS-08-02",
     "Giám sát hoặc phản ứng an ninh thất bại",
     "Security Monitoring or Response Failure",
     "CCTV, hotline, guard, patrol, dispatch hoặc response.", False),
    ("SV-08", "IS-08-03",
     "PCCC hoặc sẵn sàng khẩn cấp không đạt",
     "Fire or Emergency Readiness Failure",
     "Fire/smoke, alarm, detection, suppression, egress, evacuation, command hoặc continuity.", True),
    # SV-09
    ("SV-09", "IS-09-01",
     "Vệ sinh hoặc hygiene không đạt",
     "Cleaning or Hygiene Failure",
     "Dirty surface, restroom, supply hoặc spill response.", False),
    ("SV-09", "IS-09-02",
     "Rác thải hoặc sinh vật gây hại không được kiểm soát",
     "Waste or Pest Failure",
     "Overflow, missed collection, sorting, bulky waste, insect hoặc rodent.", False),
    ("SV-09", "IS-09-03",
     "Cảnh quan hoặc phiền nhiễu môi trường",
     "Landscape or Environmental Nuisance",
     "Plant, irrigation, unsafe branch, odor hoặc nuisance.", False),
    # SV-10
    ("SV-10", "IS-10-01",
     "Vấn đề khác cần review",
     "Other Issue Requiring Review",
     "Nội dung đủ rõ nhưng ngoài phạm vi chín Service.", False),
]

CHANNELS = [
    ("CH-APP",       "Ứng dụng di động",       "Mobile App"),
    ("CH-WEB",       "Website/Portal",          "Website / Portal"),
    ("CH-HOTLINE",   "Hotline/Call Center",     "Hotline / Call Center"),
    ("CH-EMAIL",     "Email",                   "Email"),
    ("CH-FRONTDESK", "Quầy lễ tân/Service Desk","Front Desk / Service Desk"),
    ("CH-SOCIAL",    "Mạng xã hội/Messaging",  "Social Media / Messaging"),
    ("CH-INPERSON",  "In-person/Site Visit",    "In-person / Site Visit"),
    ("CH-SYSTEM",    "Machine/System event",    "Machine / System Event"),
]


def _checksum(data: object) -> str:
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def upgrade() -> None:
    conn = op.get_bind()

    # ── 1. interaction_channel (idempotent) ──────────────────────────── #
    for code, name_vi, name_en in CHANNELS:
        conn.execute(
            __import__("sqlalchemy").text(
                "INSERT INTO interaction_channel "
                "(interaction_channel_id, channel_code, name_vi, name_en, active) "
                "VALUES (gen_random_uuid(), :code, :vi, :en, true) "
                "ON CONFLICT (channel_code) DO NOTHING"
            ),
            {"code": code, "vi": name_vi, "en": name_en},
        )

    # ── 2. taxonomy_release ──────────────────────────────────────────── #
    seed_payload = {
        "stages": STAGES,
        "steps": STEPS,
        "service_request_steps": SERVICE_REQUEST_STEPS,
        "services": SERVICES,
        "issues": ISSUES,
    }
    checksum = _checksum(seed_payload)

    import sqlalchemy as sa  # local import to keep file header clean
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    result = conn.execute(
        sa.text(
            "INSERT INTO taxonomy_release "
            "(taxonomy_release_id, version, status, effective_from, "
            " source_checksum, approved_by, approved_at, "
            " published_by, published_at, created_at, created_by) "
            "VALUES "
            "(gen_random_uuid(), :ver, 'PUBLISHED', :eff, "
            " :chk, gen_random_uuid(), :now, "
            " gen_random_uuid(), :now, :now, gen_random_uuid()) "
            "ON CONFLICT (version) DO NOTHING "
            "RETURNING taxonomy_release_id"
        ),
        {"ver": TAXONOMY_VERSION, "eff": now, "chk": checksum, "now": now},
    )
    row = result.fetchone()
    if row is None:
        # Already seeded — fetch existing ID
        row = conn.execute(
            sa.text(
                "SELECT taxonomy_release_id FROM taxonomy_release WHERE version = :ver"
            ),
            {"ver": TAXONOMY_VERSION},
        ).fetchone()
    release_id = str(row[0])

    # ── 3. customer_lifecycle_stage ──────────────────────────────────── #
    stage_id_map: dict[str, str] = {}
    for s in STAGES:
        r = conn.execute(
            sa.text(
                "INSERT INTO customer_lifecycle_stage "
                "(customer_lifecycle_stage_id, taxonomy_release_id, stage_code, "
                " name_vi, name_en, sort_order, active) "
                "VALUES (gen_random_uuid(), :rid, :code, :vi, :en, :ord, true) "
                "ON CONFLICT (taxonomy_release_id, stage_code) DO NOTHING "
                "RETURNING customer_lifecycle_stage_id"
            ),
            {
                "rid": release_id,
                "code": s["code"],
                "vi": s["name_vi"],
                "en": s["name_en"],
                "ord": s["sort_order"],
            },
        )
        fetched = r.fetchone()
        if fetched is None:
            fetched = conn.execute(
                sa.text(
                    "SELECT customer_lifecycle_stage_id FROM customer_lifecycle_stage "
                    "WHERE taxonomy_release_id = :rid AND stage_code = :code"
                ),
                {"rid": release_id, "code": s["code"]},
            ).fetchone()
        stage_id_map[s["code"]] = str(fetched[0])

    # ── 4. customer_lifecycle_step ───────────────────────────────────── #
    for stage_code, step_code, name_vi, sort_order in STEPS:
        conn.execute(
            sa.text(
                "INSERT INTO customer_lifecycle_step "
                "(customer_lifecycle_step_id, taxonomy_release_id, "
                " customer_lifecycle_stage_id, step_code, name_vi, sort_order, active) "
                "VALUES (gen_random_uuid(), :rid, :sid, :code, :vi, :ord, true) "
                "ON CONFLICT (taxonomy_release_id, step_code) DO NOTHING"
            ),
            {
                "rid": release_id,
                "sid": stage_id_map[stage_code],
                "code": step_code,
                "vi": name_vi,
                "ord": sort_order,
            },
        )

    # ── 5. service_request_step ──────────────────────────────────────── #
    for code, name_vi, name_en, sort_order in SERVICE_REQUEST_STEPS:
        conn.execute(
            sa.text(
                "INSERT INTO service_request_step "
                "(service_request_step_id, taxonomy_release_id, step_code, "
                " name_vi, name_en, sort_order, active) "
                "VALUES (gen_random_uuid(), :rid, :code, :vi, :en, :ord, true) "
                "ON CONFLICT (taxonomy_release_id, step_code) DO NOTHING"
            ),
            {
                "rid": release_id,
                "code": code,
                "vi": name_vi,
                "en": name_en,
                "ord": sort_order,
            },
        )

    # ── 6. service ───────────────────────────────────────────────────── #
    service_id_map: dict[str, str] = {}
    for code, name_vi, name_en, outcome, default_sev in SERVICES:
        r = conn.execute(
            sa.text(
                "INSERT INTO service "
                "(service_id, taxonomy_release_id, service_code, name_vi, name_en, "
                " outcome_definition, default_severity, active) "
                "VALUES (gen_random_uuid(), :rid, :code, :vi, :en, :out, :sev, true) "
                "ON CONFLICT (taxonomy_release_id, service_code) DO NOTHING "
                "RETURNING service_id"
            ),
            {
                "rid": release_id,
                "code": code,
                "vi": name_vi,
                "en": name_en,
                "out": outcome,
                "sev": default_sev,
            },
        )
        fetched = r.fetchone()
        if fetched is None:
            fetched = conn.execute(
                sa.text(
                    "SELECT service_id FROM service "
                    "WHERE taxonomy_release_id = :rid AND service_code = :code"
                ),
                {"rid": release_id, "code": code},
            ).fetchone()
        service_id_map[code] = str(fetched[0])

    # ── 7. issue ─────────────────────────────────────────────────────── #
    for svc_code, iss_code, name_vi, name_en, definition, safety in ISSUES:
        conn.execute(
            sa.text(
                "INSERT INTO issue "
                "(issue_id, taxonomy_release_id, service_id, issue_code, "
                " name_vi, name_en, definition, safety_critical, active) "
                "VALUES (gen_random_uuid(), :rid, :sid, :code, "
                " :vi, :en, :def, :safe, true) "
                "ON CONFLICT (taxonomy_release_id, issue_code) DO NOTHING"
            ),
            {
                "rid": release_id,
                "sid": service_id_map[svc_code],
                "code": iss_code,
                "vi": name_vi,
                "en": name_en,
                "def": definition,
                "safe": safety,
            },
        )

    # ── 8. Validate release gates (§22) ──────────────────────────────── #
    def _count(sql: str, params: dict | None = None) -> int:
        return conn.execute(sa.text(sql), params or {}).scalar()

    stage_count = _count(
        "SELECT COUNT(*) FROM customer_lifecycle_stage "
        "WHERE taxonomy_release_id = :rid AND active = true",
        {"rid": release_id},
    )
    step_count = _count(
        "SELECT COUNT(*) FROM customer_lifecycle_step "
        "WHERE taxonomy_release_id = :rid AND active = true",
        {"rid": release_id},
    )
    srv_step_count = _count(
        "SELECT COUNT(*) FROM service_request_step "
        "WHERE taxonomy_release_id = :rid AND active = true",
        {"rid": release_id},
    )
    svc_count = _count(
        "SELECT COUNT(*) FROM service "
        "WHERE taxonomy_release_id = :rid AND active = true",
        {"rid": release_id},
    )
    issue_count = _count(
        "SELECT COUNT(*) FROM issue "
        "WHERE taxonomy_release_id = :rid AND active = true",
        {"rid": release_id},
    )

    errors = []
    if stage_count != 6:
        errors.append(f"Expected 6 lifecycle stages, got {stage_count}")
    if step_count != 36:
        errors.append(f"Expected 36 lifecycle steps, got {step_count}")
    if srv_step_count != 8:
        errors.append(f"Expected 8 service request steps, got {srv_step_count}")
    if svc_count != 10:
        errors.append(f"Expected 10 services, got {svc_count}")
    if issue_count != 28:
        errors.append(f"Expected 28 issues, got {issue_count}")

    if errors:
        raise RuntimeError(
            "Taxonomy 3.0.0 seed validation FAILED:\n" + "\n".join(errors)
        )


def downgrade() -> None:
    import sqlalchemy as sa

    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT taxonomy_release_id FROM taxonomy_release WHERE version = :ver"
        ),
        {"ver": TAXONOMY_VERSION},
    ).fetchone()
    if result is None:
        return

    release_id = str(result[0])
    for table in (
        "issue",
        "service",
        "service_request_step",
        "customer_lifecycle_step",
        "customer_lifecycle_stage",
    ):
        conn.execute(
            sa.text(f"DELETE FROM {table} WHERE taxonomy_release_id = :rid"),
            {"rid": release_id},
        )

    conn.execute(
        sa.text("DELETE FROM taxonomy_release WHERE version = :ver"),
        {"ver": TAXONOMY_VERSION},
    )
    # Channels are canonical reference data — not removed on downgrade
