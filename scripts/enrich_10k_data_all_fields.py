"""Enrich 10,000 feedback records with rich customer profiles, operational metrics, SLA, assigned staff, root causes, touchpoints, and resolution notes."""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import text
from packages.infrastructure.db.session import AsyncSessionLocal

random.seed(42)

CSV_PATH = Path("/Users/thangnguyen/Documents/analyst-data-workspace/data/cx_resident_feedback_10000.csv")
PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")

# Realistic Vietnamese Names
FIRST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
MIDDLE_NAMES = ["Văn", "Thị", "Hữu", "Đức", "Minh", "Hoàng", "Thanh", "Ngọc", "Quốc", "Hải", "Khánh", "Thu", "Mai", "Xuân", "Gia", "Bảo"]
LAST_NAMES = ["Nam", "Hùng", "Dũng", "Tuấn", "Anh", "Long", "Bảo", "Linh", "Trang", "Hương", "Mai", "Yến", "Phương", "Hà", "Cường", "Thắng", "Quân", "Đạt", "Thảo", "Hạnh"]

RESIDENT_TYPES = ["CHỦ HỘ", "KHÁCH THUÊ", "CHỦ HỘ", "CHỦ HỘ", "KHÁCH THUÊ", "MÔI GIỚI", "KHÁCH VÃNG LAI"]

SOURCE_SYSTEMS = [
    "VinID Resident App",
    "VinID Resident App",
    "Genesys Contact Center",
    "Zalo Official Account",
    "Quầy Lễ Tân Kiosk",
    "Web Portal Cư Dân",
    "Hệ Thống BMS Tòa Nhà",
]

DEPARTMENTS = {
    "SV-01": "Phòng Kinh Doanh & Bán Hàng",
    "SV-02": "Ban Quản Lý Bàn Giao & Bảo Hành",
    "SV-03": "Bộ Phận Chăm Sóc Cư Dân & Dịch Vụ Số",
    "SV-04": "Phòng Kế Toán & Quản Lý Thu Phí",
    "SV-05": "Đội Vận Hành Bãi Xe & Kiểm Soát Ra Vào",
    "SV-06": "Ban Quản Lý Tiện Ích & Dịch Vụ Cư Dân",
    "SV-07": "Phòng Kỹ Thuật Cơ Điện & Hạ Tầng (M&E)",
    "SV-08": "Đội An Ninh Trật Tự & PCCC",
    "SV-09": "Công Ty Dịch Vụ Môi Trường & Cây Xanh",
    "SV-10": "Bộ Phận Tiếp Nhận Chung",
}

ASSIGNED_TEAMS = {
    "SV-01": ["Tổ Tư Vấn Bán Hàng 1", "Tổ Chăm Sóc Khách Hàng Tiềm Năng"],
    "SV-02": ["Tổ Nghiệm Thu Căn Hộ", "Tổ Bảo Hành Hoàn Thiện"],
    "SV-03": ["Tổ CSKH App Cư Dân", "Tổ Lễ Tân Sảnh A", "Tổ Lễ Tân Sảnh B"],
    "SV-04": ["Tổ Kế Toán Thu Phí", "Tổ Đối Soát Ngân Hàng"],
    "SV-05": ["Tổ Quản Lý Bãi Xe Hầm B1-B2", "Tổ Kỹ Thuật Trạm Sạc Xe Điện", "Tổ Kiểm Soát Barrier"],
    "SV-06": ["Tổ Quản Lý Hồ Bơi & Gym", "Tổ Tiện Ích BBQ Ngoài Trời", "Tổ Điều Phối Thang Hàng"],
    "SV-07": ["Đội Bảo Trì Thang Máy KONE", "Tổ Kỹ Thuật Điện Nước Tòa Nhà", "Tổ Điều Hòa Thông Gió (HVAC)"],
    "SV-08": ["Tổ Tuần Tra An Ninh Ca Đêm", "Tổ Trực Phòng Giám Sát Camera & PCCC", "Tổ Bảo Vệ Cổng Chính"],
    "SV-09": ["Tổ Vệ Sinh Sảnh & Hành Lang", "Tổ Thu Gom & Khử Khuẩn Rác Thải", "Tổ Chăm Sóc Cây Xanh Công Viên"],
    "SV-10": ["Bộ Phận Sàng Lọc Phản Hồi"],
}

ASSIGNED_AGENTS = [
    "KTV. Lê Văn Dũng", "KTV. Phạm Quốc Tuấn", "KTV. Trần Minh Quang",
    "Bảo vệ trưởng Trần Văn Hùng", "Bảo vệ ca đêm Nguyễn Văn Thắng", "Bảo vệ Nguyễn Hữu Đạt",
    "Lễ tân Hoàng Thị Yến", "Lễ tân Đặng Thu Hà", "CSKH Nguyễn Mai Anh", "CSKH Lê Hoàng Long",
    "Kế toán viên Vũ Bích Thảo", "Chuyên viên bảo hành Đỗ Minh Quân",
]

RESOLUTION_NOTES = {
    "SV-07": [
        "Đã căn chỉnh tiếp điểm hành trình cửa thang máy và test vận hành 5 vòng an toàn, thang đã êm ái.",
        "Đã thay thế 2 bóng đèn led chiếu sáng hành lang bị cháy, khu vực đã sáng rõ.",
        "Đã xử lý thông tắc và siết lại van cấp nước sinh hoạt, áp lực nước căn hộ đã ổn định.",
        "Đã reset tủ điều khiển trung tâm và bơm bù áp hệ thống điều hòa sảnh.",
        "Đã dán lại gioăng chống thấm và trám silicon mép nối cửa sổ.",
    ],
    "SV-05": [
        "Đã điều phối 2 bảo vệ xuống hầm phân luồng xe ô tô và kẻ lại vạch hướng dẫn đỗ xe.",
        "Đã khởi động lại modem điều khiển trạm sạc xe điện số 3, cư dân đã sạc bình thường.",
        "Đã cập nhật lại camera nhận diện biển số cổng barrier và đổi thẻ từ mới cho cư dân.",
        "Đã lắp thêm tấm chắn chống giọt bắn nước ngưng trần hầm B1 khu vực đỗ xe.",
    ],
    "SV-08": [
        "Đã cử 2 bảo vệ trực tiếp lên căn hộ nhắc nhở tắt nhạc karaoke, cam kết không tái phạm.",
        "Đã kiểm tra đầu báo khói sự cố và reset tủ trung tâm báo cháy tòa nhà.",
        "Đã trích xuất camera an ninh xác định đối tượng vứt tàn thuốc và gửi thông báo nhắc nhở.",
        "Đã tăng cường tần suất tuần tra ca đêm của tổ bảo vệ lên 30 phút/lượt.",
    ],
    "SV-09": [
        "Đã cọ rửa, xịt khử trùng bằng Cloramin B toàn bộ phòng rác và đóng kín cửa thoát khí.",
        "Đã dọn dẹp sạch sẽ toàn bộ thùng rác công viên và thay túi rác mới.",
        "Đã phun thuốc diệt muỗi và côn trùng khu vực bồn hoa quanh sảnh tòa nhà.",
        "Đã nhắc nhở nhân viên vệ sinh bắt buộc đặt biển cảnh báo sàn ướt khi lau dọn.",
    ],
    "SV-04": [
        "Đã đối soát với ngân hàng và cập nhật trạng thái Đã Thanh Toán trên App cho căn hộ.",
        "Đã cử nhân viên kỹ thuật xuống cùng cư dân kiểm tra lại chỉ số công tơ nước.",
        "Đã xuất hóa đơn điện tử VAT và gửi về hòm thư email của cư dân.",
    ],
    "SV-03": [
        "Đã cấp lại thẻ cư dân mới tại quầy lễ tân trong 5 phút.",
        "Đã hỗ trợ hướng dẫn cư dân hoàn thiện hồ sơ đăng ký tạm trú trực tuyến.",
        "Đã thông báo đội IT đẩy bản vá cập nhật sửa lỗi văng ứng dụng trên iOS.",
    ],
    "SV-06": [
        "Đã xác nhận đặt chỗ khu vực nướng BBQ và gửi mã QR check-in qua App.",
        "Đã thay dây curoa mới cho máy chạy bộ số 1 tại phòng gym.",
        "Đã kiểm tra nồng độ pH và Clo bể bơi, các chỉ số đạt tiêu chuẩn an toàn.",
    ],
    "SV-02": [
        "Đã cử thợ sơn bả xử lý vết nứt trần và sơn lại đồng màu trong 2 giờ.",
        "Đã căn chỉnh lại bản lề cửa ra vào và bôi trơn khóa vân tay.",
    ],
    "SV-01": [
        "Đã gửi bản mềm PDF tài liệu dự án và bảng tính dòng tiền qua email cho khách hàng.",
    ],
    "SV-10": [
        "Tin nhắn rác/spam, hệ thống tự động lưu trữ và đóng yêu cầu.",
    ],
}

ROOT_CAUSES = {
    "SV-07": ["HARDWARE_WEAR (Hao mòn cơ khí)", "ELECTRICAL_SURGE (Biến áp nguồn)", "PREVENTIVE_MAINT_DUE (Đến kỳ bảo dưỡng)"],
    "SV-05": ["PEAK_CAPACITY_OVERLOAD (Quá tải giờ cao điểm)", "SENSOR_GLITCH (Lỗi cảm biến nhận diện)", "USER_MISPARK (Cư dân đỗ sai làn)"],
    "SV-08": ["RESIDENT_RULE_VIOLATION (Vi phạm quy chế chung cư)", "FALSE_ALARM (Báo động giả do cảm biến bụi)", "STAFF_ATTENDANCE (Nhân viên lơ là)"],
    "SV-09": ["SUMMER_PEAK_TRASH (Tải lượng rác tăng cao)", "CLEANING_SCHEDULE_DELAY (Chậm tiến độ ca dọn)", "WEATHER_RAIN (Thời tiết mưa ẩm)"],
    "SV-04": ["BANK_GATEWAY_DELAY (Trễ cổng thanh toán)", "METER_READING_VARIANCE (Sai lệch chỉ số đồng hồ)", "TARIFF_ADJUSTMENT (Điều chỉnh biểu giá)"],
    "SV-03": ["MOBILE_APP_VERSION_BUG (Lỗi phiên bản ứng dụng)", "USER_PROFILE_MISMATCH (Lệch thông tin hồ sơ)"],
    "SV-06": ["EQUIPMENT_OVERUSE (Thiết bị hoạt động liên tục)", "BOOKING_SLOT_CONFLICT (Trùng lịch hệ thống)"],
    "SV-02": ["CONSTRUCTION_DEFECT (Lỗi hoàn thiện nhà thầu)", "HANDOVER_RUSH (Áp lực tiến độ bàn giao)"],
    "SV-01": ["INQUIRY_GENERAL (Khách hàng hỏi thông tin chung)"],
    "SV-10": ["SPAM_PROMOTION (Rao vặt quảng cáo)", "SYSTEM_TEST (Kiểm thử hệ thống)"],
}

TOUCHPOINT_MAP = {
    "SV-07": "TP-RES-03-03", # Thang máy / Hạ tầng
    "SV-05": "TP-RES-03-02", # Bãi xe / Ra vào
    "SV-08": "TP-RES-07-02", # An ninh / PCCC
    "SV-09": "TP-RES-07-03", # Vệ sinh / Môi trường
    "SV-04": "TP-RES-06-01", # Thu phí / Hoá đơn
    "SV-03": "TP-RES-02-01", # App / CSKH
    "SV-06": "TP-RES-05-01", # Tiện ích BBQ/Gym
    "SV-02": "TP-HO-03-01",  # Nghiệm thu bàn giao
    "SV-01": "TP-C-01-01",   # Tư vấn dự án
    "SV-10": None,
}


def rand_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(LAST_NAMES)}"

def rand_phone():
    prefix = random.choice(["090", "091", "098", "097", "093", "094", "086", "088"])
    suffix = f"{random.randint(1000, 9999)}"
    return f"{prefix}***{suffix}"

def rand_email(name):
    clean = name.lower().replace(" ", ".").replace("đ", "d")
    for ch in "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ":
        clean = clean.replace(ch, "a")
    return f"{clean[:8]}***@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'vinhomes.vn'])}"

def rand_apt(building):
    b_code = building.split(" - ")[0].replace("Tòa ", "").strip()
    floor = random.randint(2, 35)
    unit = random.choice(["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"])
    return f"{b_code}-{floor:02d}{unit}"


async def enrich_all():
    print("1. Reading 10,000 CSV rows...")
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"   Loaded {len(rows)} rows.")

    # Enrich rows with all fields
    print("2. Generating rich resident profiles and operational data...")
    enriched_rows = []
    for r in rows:
        svc = r.get("service_code", "SV-07")
        building = r.get("building", "Tòa S10.02 - Vinhomes Grand Park")
        sentiment = r.get("sentiment", "NEUTRAL")
        sev = r.get("operational_severity", "SEV-4")
        elig = r.get("analytic_eligibility", "INCLUDED")

        name = rand_name()
        res_type = random.choice(RESIDENT_TYPES)
        apt = rand_apt(building)
        phone = rand_phone()
        email = rand_email(name)
        src_sys = random.choice(SOURCE_SYSTEMS)
        dept = DEPARTMENTS.get(svc, "Ban Quản Lý Tòa Nhà")
        team = random.choice(ASSIGNED_TEAMS.get(svc, ["Tổ Quản Lý Vận Hành"]))
        agent = random.choice(ASSIGNED_AGENTS)

        if elig == "EXCLUDED":
            status = "TỪ CHỐI DO KHÔNG HỢP LỆ"
            sla = "MET_SLA"
            handling_hours = 0.1
            csat = None
            resolution = "Hệ thống tự động lọc và đóng yêu cầu ngoài phạm vi."
            root_cause = "SPAM_OR_TEST"
        elif sentiment == "POSITIVE":
            status = "ĐÃ TIẾP NHẬN & GHI NHẬN"
            sla = "MET_SLA"
            handling_hours = 0.5
            csat = 5
            resolution = f"Đã chuyển lời khen ngợi của cư dân tới {team} và {agent}."
            root_cause = "EXCELLENT_SERVICE"
        elif sev in ("SEV-1", "SEV-2"):
            status = random.choice(["ĐÃ XỬ LÝ XONG", "ĐÃ XỬ LÝ XONG", "ĐANG XỬ LÝ"])
            sla = random.choice(["MET_SLA", "MET_SLA", "IN_SLA", "NEAR_BREACH"])
            handling_hours = round(random.uniform(0.5, 4.0), 1)
            csat = random.choice([3, 4, 4, 5]) if status == "ĐÃ XỬ LÝ XONG" else None
            resolution = random.choice(RESOLUTION_NOTES.get(svc, ["Đã xử lý xong sự cố."]))
            root_cause = random.choice(ROOT_CAUSES.get(svc, ["HARDWARE_FAILURE"]))
        else:
            status = random.choice(["ĐÃ XỬ LÝ XONG", "ĐÃ XỬ LÝ XONG", "ĐÃ TIẾP NHẬN"])
            sla = random.choice(["MET_SLA", "MET_SLA", "IN_SLA"])
            handling_hours = round(random.uniform(1.0, 12.0), 1)
            csat = random.choice([4, 5, 5, 4]) if status == "ĐÃ XỬ LÝ XONG" else None
            resolution = random.choice(RESOLUTION_NOTES.get(svc, ["Đã hỗ trợ cư dân."]))
            root_cause = random.choice(ROOT_CAUSES.get(svc, ["GENERAL_INQUIRY"]))

        tp_code = TOUCHPOINT_MAP.get(svc)

        # Build enriched metadata JSON
        meta_dict = {
            "ticket_id": r["ticket_id"],
            "building": building,
            "channel": r["channel"],
            "reported_date": r["reported_date"],
            "sentiment": sentiment,
            "operational_severity": sev,
            "service_code": svc,
            "issue_code": r["issue_code"],
            "journey_stage": r["journey_stage"],
            "journey_step": r["journey_step"],
            "analytic_eligibility": elig,
            "content_masked": r["content_masked"],
            # Rich fields:
            "resident_name": name,
            "resident_type": res_type,
            "apartment_number": apt,
            "phone_masked": phone,
            "email_masked": email,
            "source_system": src_sys,
            "department": dept,
            "assigned_team": team,
            "assigned_agent": agent,
            "handling_status": status,
            "sla_status": sla,
            "handling_time_hours": handling_hours,
            "csat_rating": csat,
            "resolution_note": resolution,
            "root_cause": root_cause,
            "touchpoint_code": tp_code,
        }

        r_enriched = dict(r)
        r_enriched.update({
            "resident_name": name,
            "resident_type": res_type,
            "apartment_number": apt,
            "phone_masked": phone,
            "email_masked": email,
            "source_system": src_sys,
            "department": dept,
            "assigned_team": team,
            "assigned_agent": agent,
            "handling_status": status,
            "sla_status": sla,
            "handling_time_hours": handling_hours,
            "csat_rating": csat if csat is not None else "",
            "resolution_note": resolution,
            "root_cause": root_cause,
            "touchpoint_code": tp_code or "",
            "_meta_json": meta_dict,
        })
        enriched_rows.append(r_enriched)

    # 3. Rewrite CSV with all new columns
    print(f"3. Writing enriched CSV to {CSV_PATH}...")
    fieldnames = [
        "ticket_id", "content_masked", "building", "apartment_number",
        "resident_name", "resident_type", "phone_masked", "email_masked",
        "channel", "source_system", "reported_date", "department",
        "assigned_team", "assigned_agent", "handling_status", "sla_status",
        "handling_time_hours", "csat_rating", "resolution_note", "root_cause",
        "sentiment", "operational_severity", "service_code", "issue_code",
        "touchpoint_code", "journey_stage", "journey_step", "analytic_eligibility"
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for r in enriched_rows:
            writer.writerow(r)

    print("   CSV file updated with all 28 enriched columns!")

    # 4. Update Database records
    print("4. Updating PostgreSQL database with enriched JSONB and metadata...")
    async with AsyncSessionLocal() as session:
        # Fetch touchpoints mapping
        tps_res = await session.execute(text("SELECT touchpoint_id, touchpoint_code FROM touchpoint"))
        tp_map = {r["touchpoint_code"]: r["touchpoint_id"] for r in tps_res.mappings().all()}

        # Batch update database in chunks of 1000
        for i in range(0, len(enriched_rows), 1000):
            chunk = enriched_rows[i : i + 1000]
            update_payload = []
            for item in chunk:
                t_id = item["ticket_id"]
                m_json = json.dumps(item["_meta_json"], ensure_ascii=False)
                src_sys = item["source_system"]
                symptom = f"[{item['service_code']}] {item['resolution_note'][:60]}"
                tp_id = tp_map.get(item["touchpoint_code"])
                tp_status = "KNOWN" if tp_id else "NOT_APPLICABLE"
                
                update_payload.append({
                    "ticket_id": t_id,
                    "meta_json": m_json,
                    "src_sys": src_sys,
                    "symptom": symptom,
                    "tp_id": tp_id,
                    "tp_status": tp_status,
                    "cause_status": "DETERMINED" if item["root_cause"] != "SPAM_OR_TEST" else "NOT_ASSESSED",
                    "reason": f"Phân loại {item['service_code']} - {item['root_cause']}",
                })

            await session.execute(
                text("""
                    UPDATE feedback
                    SET source_metadata_json = CAST(:meta_json AS jsonb),
                        source_system = :src_sys
                    WHERE external_ticket_id = :ticket_id
                """),
                update_payload,
            )

            # Update feedback_item symptom
            await session.execute(
                text("""
                    UPDATE feedback_item fi
                    SET symptom_detail = :symptom
                    FROM feedback f
                    WHERE fi.feedback_id = f.feedback_id
                      AND f.external_ticket_id = :ticket_id
                """),
                update_payload,
            )

            # Update classification_current with touchpoint & cause
            await session.execute(
                text("""
                    UPDATE classification_current cc
                    SET touchpoint_id = CAST(:tp_id AS uuid),
                        touchpoint_value_status = :tp_status,
                        cause_determination_status = :cause_status
                    FROM feedback_item fi
                    JOIN feedback f ON fi.feedback_id = f.feedback_id
                    WHERE cc.feedback_item_id = fi.feedback_item_id
                      AND f.external_ticket_id = :ticket_id
                """),
                update_payload,
            )

        await session.commit()
        print("5. Database successfully enriched with all fields!")


asyncio.run(enrich_all())
