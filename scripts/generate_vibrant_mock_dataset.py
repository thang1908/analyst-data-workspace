"""Generate extensive, vibrant residential CX mock dataset (~2,500 items) covering all 10 services, 6 journey stages, touchpoints, locations, and channels."""
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
    {"code": "LOC-S1003", "name": "Tòa S10.03 - Vinhomes Grand Park"},
    {"code": "LOC-S801", "name": "Tòa S8.01 - Vinhomes Smart City"},
    {"code": "LOC-S802", "name": "Tòa S8.02 - Vinhomes Smart City"},
    {"code": "LOC-S803", "name": "Tòa S8.03 - Vinhomes Smart City"},
    {"code": "LOC-R1", "name": "Tòa R1 - Vinhomes Royal City"},
    {"code": "LOC-R2", "name": "Tòa R2 - Vinhomes Royal City"},
    {"code": "LOC-R6", "name": "Tòa R6 - Vinhomes Royal City"},
    {"code": "LOC-P1", "name": "Tòa Park 1 - Times City"},
    {"code": "LOC-P2", "name": "Tòa Park 2 - Times City"},
    {"code": "LOC-L81", "name": "Tòa Landmark 81 - Central Park"},
    {"code": "LOC-LPLUS", "name": "Tòa Landmark Plus - Central Park"},
    {"code": "LOC-AQUA1", "name": "Tòa Aqua 1 - Vinhomes Golden River"},
]

CHANNELS = [
    "CH-APP", "CH-HOTLINE", "CH-FRONTDESK", "CH-WEB", "CH-SOCIAL", "CH-EMAIL", "CH-INPERSON"
]

# Comprehensive scenarios mapping to all 10 Services and 6 Stages
SERVICE_SCENARIOS = [
    # SV-01: Bán hàng, tư vấn & thông tin dự án (Stages A, C, TR)
    {
        "service_code": "SV-01", "issue_code": "IS-01-01", "stage_code": "C", "step_code": "C1",
        "touchpoint_code": "TP-C-01-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "templates": [
            "Tôi muốn tìm hiểu thông tin mở bán và bảng giá căn hộ 2 phòng ngủ toà {building}.",
            "Nhân viên tư vấn cung cấp thông tin về chính sách chiết khấu thanh toán sớm chưa được rõ ràng.",
            "Tôi đã đăng ký tham quan nhà mẫu vào cuối tuần nhưng chưa thấy chuyên viên liên hệ xác nhận.",
            "Chính sách hỗ trợ lãi suất ngân hàng 0% trong 24 tháng áp dụng cho những ngân hàng nào?",
            "Brochure giới thiệu dự án toà {building} có thể gửi bản mềm PDF qua email cho tôi được không?",
        ],
    },
    # SV-02: Bàn giao, nghiệm thu & bảo hành (Stage HO)
    {
        "service_code": "SV-02", "issue_code": "IS-02-02", "stage_code": "HO", "step_code": "HO-03",
        "touchpoint_code": "TP-HO-03-01", "sentiment": "NEGATIVE", "severity": "SEV-3", "valid": True,
        "templates": [
            "Khi kiểm tra nhận nhà tại {building}, phát hiện cửa chính bị xước và gạch lát sàn ban công bị ộp.",
            "Tồn đọng ghi trong biên bản nghiệm thu từ tháng trước đến nay vẫn chưa thấy đội bảo hành xuống sửa.",
            "Khóa cửa vân tay thông minh căn hộ {building} không nhận diện được dấu vân tay lúc nhận bàn giao.",
            "Tường phòng ngủ master có vệt ố vàng nghi bị rỉ nước từ căn hộ tầng trên xuống.",
            "Thủ tục nhận chìa khóa và bàn giao căn hộ toà {building} kéo dài hơn 2 tiếng do đông người.",
        ],
    },
    # SV-03: Hồ sơ, thủ tục, App Cư dân & CSKH (Stage RES)
    {
        "service_code": "SV-03", "issue_code": "IS-03-02", "stage_code": "RES", "step_code": "RES-02",
        "touchpoint_code": "TP-RES-02-01", "sentiment": "NEGATIVE", "severity": "SEV-4", "valid": True,
        "templates": [
            "Ứng dụng cư dân trên iOS toà {building} liên tục bị văng khi bấm vào mục gửi yêu cầu bảo trì.",
            "Tôi không nhận được mã OTP kích hoạt tài khoản cư dân dù đã đăng ký hồ sơ tại quầy lễ tân.",
            "Thông báo cắt điện bảo dưỡng định kỳ trên App gửi quá sát giờ làm gia đình không kịp chuẩn bị.",
            "Giao diện ứng dụng cư dân mới cập nhật khó sử dụng hơn bản cũ, tìm nút đặt tiện ích rất khó.",
            "Tôi muốn làm thủ tục đăng ký sổ hồng và cấp lại thẻ cư dân bị mất cho người nhà.",
        ],
    },
    # SV-04: Phí quản lý, hóa đơn & thanh toán (Stage RES)
    {
        "service_code": "SV-04", "issue_code": "IS-04-01", "stage_code": "RES", "step_code": "RES-06",
        "touchpoint_code": "TP-RES-06-01", "sentiment": "NEGATIVE", "severity": "SEV-4", "valid": True,
        "templates": [
            "Hóa đơn tiền nước sinh hoạt tháng này của căn hộ tại {building} tăng đột biến gấp đôi bình thường.",
            "Tôi đã chuyển khoản thanh toán phí dịch vụ quản lý 3 ngày trước nhưng hệ thống vẫn báo nợ.",
            "Bảng kê chi tiết phí gửi 2 xe máy và 1 ô tô tính sai số tiền so với quy định đã niêm yết.",
            "Đề nghị BQL làm rõ cách tính tiền điện chiếu sáng công cộng chia cho từng căn hộ.",
            "Cổng thanh toán trực tuyến trên ứng dụng bị lỗi giao dịch trừ tiền tài khoản nhưng không ghi nhận.",
        ],
    },
    # SV-05: Ra vào, kiểm soát sảnh, thẻ từ & bãi đỗ xe (Stage RES - Hotspot cluster)
    {
        "service_code": "SV-05", "issue_code": "IS-05-02", "stage_code": "RES", "step_code": "RES-03",
        "touchpoint_code": "TP-RES-03-02", "sentiment": "NEGATIVE", "severity": "SEV-3", "valid": True,
        "templates": [
            "Bãi đỗ xe tầng hầm B2 toà {building} lúc 19h tối hết sạch chỗ đỗ ô tô, xe phải đỗ tràn ra lối đi.",
            "Trạm sạc xe điện VinFast dưới hầm {building} bị nhiều xe xăng đỗ chiếm chỗ cả ngày không sạc được.",
            "Cổng barrier quẹt thẻ xe máy lối vào toà {building} bị lỗi nhận diện biển số gây ùn tắc kéo dài.",
            "Cửa kính tự động sảnh toà {building} không nhận diện thẻ từ cư dân, phải nhờ bảo vệ mở hộ.",
            "Bãi xe hầm B1 nhiều vị trí bị rò rỉ nước từ trần xuống làm bẩn xe cư dân đỗ bên dưới.",
            "Đường dẫn dốc xuống tầng hầm bãi đỗ xe trời mưa rất trơn trượt, đề nghị dán gờ giảm tốc chống trượt.",
        ],
    },
    # SV-06: Tiện ích nội khu (Hồ bơi, Gym, BBQ, Chuyển nhà) (Stage RES)
    {
        "service_code": "SV-06", "issue_code": "IS-06-01", "stage_code": "RES", "step_code": "RES-05",
        "touchpoint_code": "TP-RES-05-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "templates": [
            "Tôi muốn đặt 2 chòi nướng BBQ ngoài trời toà {building} vào tối thứ 7 tuần này qua app.",
            "Máy chạy bộ số 1 và máy tập xô tại phòng gym toà {building} bị hỏng chưa thấy kỹ thuật sửa.",
            "Nước hồ bơi người lớn toà {building} dạo này hơi đục và có nhiều mùi clo nồng gắt.",
            "Tôi muốn đăng ký sử dụng thang máy hàng để chuyển đồ đạc nội thất vào sáng chủ nhật.",
            "Khu vực sân chơi trẻ em có xích đu bị đứt xích nguy hiểm, đề nghị BQL thay mới ngay.",
        ],
    },
    # SV-07: Kỹ thuật hạ tầng, thang máy & tài sản chung (Stage RES & OPS - Hotspot cluster)
    {
        "service_code": "SV-07", "issue_code": "IS-07-01", "stage_code": "RES", "step_code": "RES-07",
        "touchpoint_code": "TP-RES-03-03", "sentiment": "NEGATIVE", "severity": "SEV-2", "valid": True,
        "templates": [
            "Thang máy số 3 toà {building} sáng nay bị kẹt ở tầng 15 khoảng 10 phút làm cư dân rất hoảng sợ.",
            "Thang máy toà {building} chạy rung lắc rất mạnh và kêu ken két bất thường khi qua tầng 8.",
            "Giờ cao điểm sáng nay toà {building} bị hỏng 2 trên 4 thang máy, cư dân phải xếp hàng 25 phút.",
            "Đường ống nước sinh hoạt hành lang tầng 9 toà {building} bị vỡ rò rỉ nước chảy tràn ra sảnh.",
            "Điều hòa sảnh tầng 1 toà {building} bị hỏng suốt 3 ngày nay, không khí ngột ngạt và nóng bức.",
            "Áp lực nước tại các tầng cao toà {building} rất yếu, vòi sen hầu như không chảy được nước nóng.",
            "Hành lang tầng 14 bị cháy 3 bóng đèn chiếu sáng từ tuần trước đến nay chưa thấy kỹ thuật thay.",
            "Cửa thoát hiểm tầng 5 toà {building} bị kẹt then cài không đóng kín được.",
        ],
    },
    # SV-08: An ninh trật tự, tiếng ồn & PCCC (Stage RES & OPS - SEV-1/SEV-2)
    {
        "service_code": "SV-08", "issue_code": "IS-08-01", "stage_code": "RES", "step_code": "RES-07",
        "touchpoint_code": "TP-RES-07-02", "sentiment": "NEGATIVE", "severity": "SEV-2", "valid": True,
        "templates": [
            "Căn hộ tầng 18 toà {building} hát karaoke gây tiếng ồn lớn sau 23h đêm, gọi bảo vệ không ai can thiệp.",
            "Hệ thống chuông báo cháy toà {building} reo báo động giả lúc 2h sáng làm cả toà nhà chạy tán loạn.",
            "Bảo vệ chốt cổng phụ toà {building} ngủ gật trong ca trực, để người lạ tự do đi vào sảnh toà nhà.",
            "Phát hiện có tàn thuốc lá vứt bừa bãi tại chiếu nghỉ cầu thang bộ thoát hiểm toà {building}.",
            "Có tình trạng người lạ bấm chuông quấy rối các căn hộ tầng 6 vào ban đêm, đề nghị trích xuất camera.",
            "Chập điện tủ kỹ thuật hành lang tầng 11 toà {building} bốc khói khét lẹt, đề nghị xử lý khẩn cấp!",
        ],
    },
    # SV-09: Vệ sinh môi trường, rác thải & cảnh quan (Stage RES & OPS)
    {
        "service_code": "SV-09", "issue_code": "IS-09-01", "stage_code": "RES", "step_code": "RES-07",
        "touchpoint_code": "TP-RES-07-03", "sentiment": "NEGATIVE", "severity": "SEV-3", "valid": True,
        "templates": [
            "Phòng rác hành lang tầng 12 toà {building} bốc mùi hôi thối nồng nặc do không được đóng kín cửa.",
            "Thùng rác công cộng khu vực sảnh chờ và lối đi dạo toà {building} đầy tràn từ sáng chưa dọn.",
            "Khu vực sân cỏ và vườn hoa công viên toà {building} xuất hiện rất nhiều muỗi, đề nghị phun thuốc.",
            "Nhân viên vệ sinh lau sàn sảnh toà {building} không đặt biển báo sàn trơn trượt.",
            "Hành lang tầng 8 toà {building} có vết nước rác rỉ bẩn kéo dài chưa được cọ rửa sạch.",
            "Cây xanh trang trí tại sảnh toà {building} bị héo úa rụng lá nhiều làm mất mỹ quan.",
        ],
    },
    # POSITIVE: Khen ngợi & Đánh giá tốt (Dịch vụ SV-03, SV-05, SV-07, SV-08, SV-09)
    {
        "service_code": "SV-05", "issue_code": "IS-05-01", "stage_code": "RES", "step_code": "RES-03",
        "touchpoint_code": "TP-RES-03-01", "sentiment": "POSITIVE", "severity": "SEV-4", "valid": True,
        "templates": [
            "Rất cảm ơn các bạn bảo vệ toà {building} đã nhiệt tình che ô và dắt xe cho cư dân lúc trời mưa bão to.",
            "Bạn lễ tân sảnh toà {building} xử lý thủ tục tiếp đón khách chu đáo, chuyên nghiệp và rất thân thiện.",
            "Đội ngũ kỹ thuật toà {building} hỗ trợ sửa chữa vòi nước rò rỉ trong căn hộ rất nhanh chóng, 10 điểm!",
            "Khuôn viên công viên và cây xanh toà {building} được chăm sóc rất đẹp, không gian sống tuyệt vời.",
            "Dịch vụ vệ sinh toà {building} luôn giữ sảnh thang máy sạch sẽ thơm tho, cảm ơn các cô lao công.",
            "BQL toà {building} lắng nghe và giải quyết kiến nghị tiếng ồn rất thỏa đáng và nhanh gọn.",
            "Ứng dụng cư dân đợt này nâng cấp thanh toán rất mượt và tiện lợi, tôi rất hài lòng.",
        ],
    },
    # OPS: Vận hành nội bộ toà nhà (Stage OPS)
    {
        "service_code": "SV-07", "issue_code": "IS-07-03", "stage_code": "OPS", "step_code": "OPS-04",
        "touchpoint_code": "TP-OPS-04-01", "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": True,
        "templates": [
            "Báo cáo kiểm tra định kỳ hệ thống máy bơm tăng áp và máy phát điện dự phòng toà {building} đạt chuẩn.",
            "Đã hoàn thành bảo trì bảo dưỡng 4 thang máy toà {building} theo đúng quy trình kiểm định an toàn.",
            "Đội kỹ thuật đã kiểm tra toàn bộ tủ điện phân phối và hệ thống chiếu sáng sự cố toà {building}.",
            "Nghiệm thu dịch vụ kiểm soát côn trùng và vệ sinh bể nước ngầm toà {building} quý này.",
        ],
    },
    # SPAM / RÁC / NON_FEEDBACK (EXCLUDED - SV-10)
    {
        "service_code": "SV-10", "issue_code": "IS-10-01", "stage_code": "RES", "step_code": "RES-07",
        "touchpoint_code": None, "sentiment": "NEUTRAL", "severity": "SEV-4", "valid": False,
        "templates": [
            "alo alo test 123 thử chức năng hệ thống",
            "chấm hóng xem có gì hot",
            "Cần bán gấp xe máy Honda SH chính chủ biển Hà Nội giá tốt liên hệ 0988776655",
            "Nhận làm hồ sơ bằng lái xe ô tô B2 bao đỗ trọn gói uy tín",
            "Cho thuê căn hộ 3 phòng ngủ đầy đủ nội thất toà {building} giá ưu đãi",
            "Hôm nay thời tiết đẹp quá cả nhà ơi chúc mọi người ngày mới tốt lành",
            "test test 123",
            "ok",
            "hi bql",
        ],
    },
]


async def seed_vibrant_dataset(target_count: int = 2600) -> None:
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
                print(f"  Skip {t}: {e}")
        await session.commit()

        # Taxonomy references
        tax = await session.execute(text("SELECT taxonomy_release_id FROM taxonomy_release WHERE status = 'PUBLISHED' LIMIT 1"))
        tax_id = tax.scalar_one_or_none() or UUID("00000000-0000-0000-0000-000000000010")

        services_res = await session.execute(text("SELECT service_id, service_code FROM service"))
        service_map = {r["service_code"]: r["service_id"] for r in services_res.mappings().all()}

        issues_res = await session.execute(text("SELECT issue_id, issue_code FROM issue"))
        issue_map = {r["issue_code"]: r["issue_id"] for r in issues_res.mappings().all()}

        steps_res = await session.execute(text("SELECT customer_lifecycle_step_id, customer_lifecycle_stage_id, step_code FROM customer_lifecycle_step"))
        step_map = {r["step_code"]: (r["customer_lifecycle_step_id"], r["customer_lifecycle_stage_id"]) for r in steps_res.mappings().all()}

        stages_res = await session.execute(text("SELECT customer_lifecycle_stage_id, stage_code FROM customer_lifecycle_stage"))
        stage_map = {r["stage_code"]: r["customer_lifecycle_stage_id"] for r in stages_res.mappings().all()}

        channels_res = await session.execute(text("SELECT interaction_channel_id, channel_code FROM interaction_channel"))
        channel_map = {r["channel_code"]: r["interaction_channel_id"] for r in channels_res.mappings().all()}

        # Ensure all locations exist
        print("2. Ensuring 14 locations exist in database...")
        loc_objs = []
        for loc in LOCATIONS:
            lid = uuid4()
            await session.execute(
                text("""
                    INSERT INTO location (location_id, project_id, location_code, name, location_type, active)
                    VALUES (:id, :project_id, :code, :name, 'BUILDING', true)
                    ON CONFLICT (project_id, location_code) DO UPDATE SET name = EXCLUDED.name
                """),
                {"id": lid, "project_id": PROJECT_ID, "code": loc["code"], "name": loc["name"]},
            )
            cur = await session.execute(
                text("SELECT location_id FROM location WHERE project_id = :project_id AND location_code = :code"),
                {"project_id": PROJECT_ID, "code": loc["code"]},
            )
            loc_objs.append((cur.scalar_one(), loc["code"], loc["name"]))
        await session.commit()

        # Build ~2,600 realistic items across 60 days
        print(f"3. Synthesizing {target_count} realistic feedback items...")
        now = datetime.now(timezone.utc)
        feedback_batch = []
        item_batch = []
        decision_batch = []
        current_batch = []

        scenario_weights = [
            8,   # SV-01 Tư vấn
            10,  # SV-02 Bàn giao
            12,  # SV-03 Thủ tục/App
            10,  # SV-04 Phí
            18,  # SV-05 Bãi xe (High)
            10,  # SV-06 Tiện ích
            22,  # SV-07 Kỹ thuật thang máy (Highest)
            12,  # SV-08 An ninh PCCC
            15,  # SV-09 Vệ sinh
            15,  # POSITIVE Khen ngợi
            6,   # OPS Vận hành
            8,   # SPAM/EXCLUDED
        ]

        for i in range(target_count):
            scenario = random.choices(SERVICE_SCENARIOS, weights=scenario_weights, k=1)[0]

            # Choose location with deliberate clustering for hotspots
            if scenario["service_code"] == "SV-07" and random.random() < 0.45:
                loc_tuple = next(l for l in loc_objs if l[1] == "LOC-S1002")
            elif scenario["service_code"] == "SV-05" and random.random() < 0.45:
                loc_tuple = next(l for l in loc_objs if l[1] == "LOC-S801")
            elif scenario["service_code"] == "SV-09" and random.random() < 0.4:
                loc_tuple = next(l for l in loc_objs if l[1] == "LOC-R6")
            elif scenario["service_code"] == "SV-08" and random.random() < 0.4:
                loc_tuple = next(l for l in loc_objs if l[1] == "LOC-L81")
            else:
                loc_tuple = random.choice(loc_objs)

            loc_id, loc_code, loc_name = loc_tuple
            raw_template = random.choice(scenario["templates"])
            text_content = raw_template.format(building=loc_name)

            ch_code = random.choice(CHANNELS)
            ch_id = channel_map.get(ch_code)

            # Time distribution across 60 days (more recent days have higher volume)
            decay = random.betavariate(2.0, 1.0)  # skewed towards recent days
            days_ago = (1.0 - decay) * 60.0
            reported_at = now - timedelta(days=days_ago, hours=random.uniform(0, 23), minutes=random.uniform(0, 59))

            ticket_id = f"TC-{810000 + i}"
            checksum = hashlib.sha256(text_content.encode()).hexdigest()

            f_id = uuid4()
            fi_id = uuid4()
            dec_id = uuid4()

            svc_id = service_map.get(scenario["service_code"])
            iss_id = issue_map.get(scenario["issue_code"])
            step_info = step_map.get(scenario["step_code"])
            step_id = step_info[0] if step_info else None
            stage_id = step_info[1] if step_info else stage_map.get(scenario["stage_code"])

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
                    "taxonomy_release_id": tax_id,
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
                    "taxonomy_release_id": tax_id,
                    "stage_id": stage_id,
                    "step_id": step_id,
                    "service_id": svc_id,
                    "issue_status": issue_status,
                    "issue_id": iss_id,
                    "sentiment": scenario["sentiment"],
                    "severity": scenario["severity"],
                    "reported_at": reported_at,
                })

        print("4. Bulk inserting batches into PostgreSQL...")
        # Batch insert chunks of 1000
        for idx in range(0, len(feedback_batch), 1000):
            fb_chunk = feedback_batch[idx : idx + 1000]
            ib_chunk = item_batch[idx : idx + 1000]
            db_chunk = decision_batch[idx : idx + 1000]
            cb_chunk = current_batch[idx : idx + 1000]

            await session.execute(
                text("""
                    INSERT INTO feedback (
                        feedback_id, project_id, source_system, source_record_key,
                        intake_channel_id, external_ticket_id,
                        reported_at, ingested_at, content_raw, content_masked,
                        source_metadata_json, raw_content_checksum, created_at
                    ) VALUES (
                        :feedback_id, :project_id, 'vibrant-mock', :source_record_key,
                        :intake_channel_id, :external_ticket_id,
                        :reported_at, :now, :content_raw, :content_masked,
                        CAST(:source_metadata_json AS jsonb), :checksum, :now
                    )
                """),
                fb_chunk,
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
                ib_chunk,
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
                        'SOURCE_TRUSTED', 'Vibrant Synthetic Seeder', UUID('00000000-0000-0000-0000-000000000002'), :reported_at
                    )
                """),
                db_chunk,
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
                cb_chunk,
            )

        await session.commit()
        print(f"5. Seeding completed successfully! Total items inserted: {len(feedback_batch)}")


asyncio.run(seed_vibrant_dataset(2600))
