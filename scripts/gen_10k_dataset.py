"""Generate 10,000 realistic Vietnamese CX resident feedback records and ingest directly into PostgreSQL."""
import asyncio
import collections
import csv
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import text
from packages.infrastructure.db.session import AsyncSessionLocal

random.seed(42)

PROJECT_ID = UUID("00000000-0000-0000-0000-000000000001")
OUT_CSV = Path("/Users/thangnguyen/Documents/analyst-data-workspace/data/cx_resident_feedback_10000.csv")

BUILDINGS = [
    "Tòa S10.01 - Vinhomes Grand Park",
    "Tòa S10.02 - Vinhomes Grand Park",
    "Tòa S8.01 - Vinhomes Smart City",
    "Tòa S8.02 - Vinhomes Smart City",
    "Tòa R6 - Vinhomes Royal City",
    "Tòa Landmark 81 - Central Park",
    "Tòa Park 1 - Times City",
]

CHANNELS = ["App Cư dân", "Hotline", "Quầy lễ tân", "Web Portal", "Zalo CSKH", "Email"]
CHANNEL_CODE_MAP = {
    "App Cư dân": "CH-APP",
    "Hotline": "CH-HOTLINE",
    "Quầy lễ tân": "CH-FRONTDESK",
    "Web Portal": "CH-WEB",
    "Zalo CSKH": "CH-SOCIAL",
    "Email": "CH-EMAIL",
}

# ================= COMPLAINTS 55% =================
COMPLAINTS = [
    # SV-07 kỹ thuật thang máy
    ("NEGATIVE","SEV-2","SV-07","IS-07-01","RES","RES-07","INCLUDED",[
        "Thang máy tòa {b} bị kẹt ở tầng {f}, cư dân kẹt bên trong gần {t} phút rồi, không có ai xử lý. Đề nghị khẩn cấp!",
        "Thang máy số {n} tòa {b} lại hỏng rồi, sáng nay bấm nút không lên được tầng. Đây là lần thứ {cnt} trong tháng này.",
        "Thang máy tầng {f} tòa {b} cửa đóng mở liên tục không dừng, tôi không dám bước vào. Ban kỹ thuật ơi xử lý giúp!",
        "Bị kẹt trong thang máy {t} phút mới được ra, không ai nghe chuông khẩn cấp. Quá nguy hiểm!",
        "Thang máy tòa {b} tầng B1 bị ngập nước sau mưa, chúng tôi không thể lên tầng được.",
        "Thang máy tòa {b} rung lắc mạnh lúc di chuyển, người cao tuổi rất sợ. Cần kiểm tra ngay!",
        "Màn hình hiển thị tầng thang máy tòa {b} bị hỏng từ hôm qua đến nay chưa sửa.",
        "Thang máy tòa {b} mùi điện khét rất khó chịu, không biết có an toàn không? Lo lắm.",
    ]),
    # SV-07 điện nước chung
    ("NEGATIVE","SEV-2","SV-07","IS-07-02","RES","RES-07","INCLUDED",[
        "Mất điện tầng {f} tòa {b} từ sáng đến giờ chưa có điện, thức ăn trong tủ lạnh hỏng hết rồi!",
        "Ống nước tầng {f} tòa {b} bị vỡ, nước chảy xuống tầng dưới, nhà tôi bị thấm nặng rồi.",
        "Hành lang tầng {f} tòa {b} bị mất đèn từ 3 ngày nay, tối om rất nguy hiểm cho cư dân đi lại.",
        "Nước sinh hoạt tòa {b} buổi sáng yếu tí tẹo, mấy tầng trên gần như không có nước để dùng.",
        "Điện tòa {b} bị ngắt đột ngột lúc {h} giờ tối không báo trước, thiết bị điện tử của tôi bị hỏng.",
        "Hệ thống bơm nước tòa {b} gây tiếng ồn cực lớn suốt đêm, không ngủ được.",
        "Bóng đèn hành lang tầng {f} cháy hết {cnt} bóng liên tiếp, tối quá không an toàn.",
        "Nước máy tòa {b} có màu vàng đục sáng nay, không biết có dùng được không?",
    ]),
    # SV-08 an ninh tiếng ồn
    ("NEGATIVE","SEV-2","SV-08","IS-08-01","RES","RES-07","INCLUDED",[
        "Căn hộ tầng {f} tòa {b} mở nhạc to thâu đêm đến {h} giờ sáng, phản ánh nhiều lần bảo vệ vẫn không xử lý.",
        "Người lạ tự do vào thang máy tòa {b} mà không bị kiểm tra, an ninh ở đâu vậy?",
        "Đêm qua có tiếng cãi nhau và đập phá ở tầng {f} tòa {b}, gọi bảo vệ mãi mới có người lên.",
        "Camera tầng hầm tòa {b} khu vực bãi xe bị hỏng, xe của tôi bị trầy xước mà không có hình ảnh gì.",
        "Xe máy bị mất trong bãi đỗ tòa {b}, bảo vệ nói camera không ghi được. Trách nhiệm thế nào?",
        "Hàng xóm tầng {f} tòa {b} đang sửa nhà từ 7 giờ sáng, tiếng khoan đục ồn kinh khủng.",
        "Có người lạ mặt lảng vảng khu vực thang bộ tòa {b} tối qua, bảo vệ cần kiểm soát tốt hơn.",
        "Chuông báo cháy tòa {b} kêu liên tục {t} phút lúc {h} giờ đêm rồi tự tắt, không ai giải thích gì cả.",
    ]),
    # SV-08 PCCC SEV-1
    ("NEGATIVE","SEV-1","SV-08","IS-08-02","RES","RES-07","INCLUDED",[
        "Chuông báo cháy đang kêu tại tầng {f} tòa {b}! Có khói nhẹ ở hành lang. Cần xử lý ngay lập tức!",
        "Phát hiện mùi khói từ phòng kỹ thuật tầng {f} tòa {b}, cần đội PCCC kiểm tra khẩn cấp!",
        "Bình chữa cháy hành lang tầng {f} tòa {b} bị tháo mất, ai làm vậy? Nguy hiểm lắm!",
        "Lối thoát hiểm tầng {f} tòa {b} bị khóa, không thể mở từ bên trong. Vi phạm PCCC nghiêm trọng!",
    ]),
    # SV-09 vệ sinh rác thải
    ("NEGATIVE","SEV-3","SV-09","IS-09-01","RES","RES-07","INCLUDED",[
        "Khu tập kết rác tầng hầm tòa {b} bốc mùi hôi thối rất khó chịu, mấy ngày chưa thấy xe đến thu gom.",
        "Hành lang tầng {f} tòa {b} có người vứt rác bừa bãi, đề nghị xem camera và nhắc nhở.",
        "Cây xanh khu vực sảnh tòa {b} chết khô không ai tưới, nhìn xấu xí lắm.",
        "Bể bơi tòa {b} nước xanh lè không biết lần cuối thay nước khi nào, mùi không dễ chịu chút nào.",
        "Rác thải xây dựng đổ bừa ở tầng {f} tòa {b}, mấy tuần rồi không ai dọn.",
        "Mùi hôi từ ống thoát nước hành lang tầng {f} tòa {b} rất nặng, chịu không nổi.",
        "Gián xuất hiện ở hành lang tầng {f} tòa {b}, cần phun thuốc khử trùng.",
        "Thùng rác khu BBQ tòa {b} đầy tràn, ruồi nhặng bay khắp nơi rất mất vệ sinh.",
    ]),
    # SV-05 bãi đỗ xe
    ("NEGATIVE","SEV-3","SV-05","IS-05-02","RES","RES-03","INCLUDED",[
        "Bãi xe tầng hầm B{n} tòa {b} hết chỗ từ chiều, xe tôi phải gửi ngoài đường mất tiền oan.",
        "Cột sạc xe điện tầng hầm tòa {b} số {n} bị hỏng {cnt} ngày nay rồi chưa sửa.",
        "Có xe ô tô đậu chắn lối đi bãi xe tòa {b} từ tối đến sáng, không rõ xe của ai.",
        "Thẻ từ xe máy của tôi không vào được cổng tòa {b} từ hôm qua, đã ra quầy lễ tân nhưng vẫn chưa khắc phục.",
        "Đèn chiếu sáng tầng hầm B{n} tòa {b} tối mờ, rất khó nhìn khi lái xe.",
        "Barrier bãi xe tòa {b} hỏng rồi, xe cộ ra vào không kiểm soát được.",
    ]),
    # SV-04 phí hóa đơn
    ("NEGATIVE","SEV-3","SV-04","IS-04-01","RES","RES-06","INCLUDED",[
        "Hóa đơn điện tháng này của căn hộ {apt} tòa {b} tăng đột biến gấp đôi tháng trước dù dùng như cũ. Sai sót ở đâu?",
        "Phí quản lý tháng {m} tòa {b} bị tính hai lần, tôi đã thanh toán rồi mà vẫn bị thông báo nợ.",
        "App cư dân hiển thị số tiền điện nước tháng này của tôi khác với hóa đơn giấy nhận được.",
        "Chuyển khoản phí quản lý từ 3 ngày trước nhưng hệ thống vẫn chưa cập nhật, bị nhắc nợ mãi.",
        "Chỉ số nước tháng này bị ghi sai, cao hơn thực tế rất nhiều. Yêu cầu đọc lại đồng hồ!",
        "Tôi đã nộp phí đủ nhưng thẻ ra vào bị khóa vì nợ phí, lỗi hệ thống hay sao?",
    ]),
    # SV-02 bàn giao bảo hành
    ("NEGATIVE","SEV-3","SV-02","IS-02-01","HO","HO-03","INCLUDED",[
        "Đã đăng ký bảo hành vết nứt trần nhà căn hộ tầng {f} tòa {b} từ {cnt} tuần trước nhưng chưa có ai đến kiểm tra.",
        "Cửa sổ căn hộ {apt} tòa {b} bị hở gió và thấm nước mưa vào, yêu cầu sửa chữa theo bảo hành.",
        "Sàn gỗ căn hộ {apt} tòa {b} bị phồng rộp sau {cnt} tháng bàn giao, đây là lỗi vật liệu chứ không phải do sử dụng.",
        "Đặt lịch bàn giao căn hộ tòa {b} đã {cnt} lần nhưng bị hoãn liên tục không có lý do.",
        "Sau bàn giao {cnt} tháng phát hiện hệ thống điện căn hộ {apt} bị đấu sai, cần thợ kỹ thuật đến kiểm tra.",
        "Vòi nước nhà bếp căn hộ tòa {b} bị rỉ nước từ khi nhận nhà, yêu cầu bảo hành.",
    ]),
    # SV-06 tiện ích
    ("NEGATIVE","SEV-3","SV-06","IS-06-01","RES","RES-05","INCLUDED",[
        "Hồ bơi tòa {b} đóng cửa đột ngột không thông báo trước, tôi đã dẫn con đến rồi mới biết.",
        "Máy tập gym tòa {b} số {n} bị hỏng {cnt} tuần rồi chưa sửa, dán giấy đề nghị vẫn không ai xử lý.",
        "Đặt lịch BBQ khu vực sân thượng tòa {b} qua app nhưng lên đến nơi đã có người khác dùng, hệ thống lỗi.",
        "Phòng sinh hoạt cộng đồng tòa {b} bẩn và bàn ghế hỏng nhiều, không đảm bảo cho tổ chức sự kiện.",
        "Wifi khu vực hồ bơi tòa {b} không kết nối được từ tuần trước.",
    ]),
    # SV-03 app
    ("NEGATIVE","SEV-3","SV-03","IS-03-01","RES","RES-02","INCLUDED",[
        "App cư dân tòa {b} bị lỗi không đăng nhập được từ sáng đến giờ, không thể gửi phản ánh.",
        "Gửi yêu cầu kỹ thuật qua app {cnt} ngày trước không thấy phản hồi, trạng thái vẫn 'đang xử lý'.",
        "Thông báo trên app cư dân tòa {b} bị delay, nhận được tin nhắn cúp nước lúc đã mất nước 2 tiếng rồi.",
        "Không nhận được mã OTP khi đăng nhập app, cần hỗ trợ kỹ thuật gấp.",
    ]),
]

# ================= INQUIRIES 20% =================
INQUIRIES = [
    # SV-04 hỏi phí
    ("NEUTRAL","SEV-4","SV-04","IS-04-02","RES","RES-06","INCLUDED",[
        "Cho tôi hỏi phí quản lý tháng {m} tòa {b} phải đóng trước ngày mấy? Đóng qua app hay phải ra quầy?",
        "Tôi muốn biết chi tiết cách tính phí điện nước tòa {b}, giá điện áp dụng là bao nhiêu/kWh?",
        "Có thể thanh toán phí quản lý tòa {b} bằng thẻ tín dụng không hay chỉ chuyển khoản?",
        "Tôi chưa nhận được hóa đơn điện nước tháng {m} tòa {b}, làm sao lấy lại?",
        "Phí gửi xe ô tô tháng tòa {b} hiện tại là bao nhiêu? Có chính sách ưu đãi không?",
        "Cho hỏi phòng {apt} tòa {b} đang có số dư cọc bao nhiêu và có thể rút lại không?",
    ]),
    # SV-06 hỏi tiện ích
    ("NEUTRAL","SEV-4","SV-06","IS-06-02","RES","RES-05","INCLUDED",[
        "Hồ bơi tòa {b} mở cửa từ mấy giờ đến mấy giờ? Có cần đặt trước qua app không?",
        "Khu BBQ sân thượng tòa {b} cho tối đa bao nhiêu người? Giá thuê bao nhiêu một buổi?",
        "Tôi muốn đặt xe tải hỗ trợ chuyển đồ vào tòa {b}, cần đăng ký trước mấy ngày?",
        "Phòng gym tòa {b} có huấn luyện viên cá nhân không? Giá dịch vụ PT là bao nhiêu?",
        "Sân tennis tòa {b} đặt lịch qua đâu? Có giờ miễn phí cho cư dân không?",
        "Trẻ em dưới {cnt} tuổi có được vào hồ bơi tòa {b} không? Cần phụ huynh đi kèm không?",
    ]),
    # SV-03 hỏi thủ tục
    ("NEUTRAL","SEV-4","SV-03","IS-03-02","RES","RES-02","INCLUDED",[
        "Tôi cần làm thủ tục đổi thẻ cư dân tòa {b} vì mất, cần mang giấy tờ gì?",
        "Muốn đăng ký thêm thẻ từ xe máy cho người thân vào tòa {b}, làm thủ tục thế nào?",
        "Cho thuê căn hộ tòa {b} cần đăng ký với ban quản lý không? Thủ tục ra sao?",
        "Tôi muốn cập nhật thông tin thành viên gia đình trong hệ thống cư dân tòa {b}, cần làm gì?",
        "Xin hỏi quy trình đăng ký người giúp việc thường trú tại tòa {b}?",
        "Muốn đặt lịch sửa chữa nội thất căn hộ tòa {b}, cần thông báo trước bao lâu?",
    ]),
    # SV-05 hỏi bãi xe
    ("NEUTRAL","SEV-4","SV-05","IS-05-03","RES","RES-03","INCLUDED",[
        "Khách đến thăm tòa {b} gửi xe như thế nào? Miễn phí bao nhiêu giờ?",
        "Cột sạc xe điện tầng hầm tòa {b} có hỗ trợ loại đầu cắm của xe VinFast không?",
        "Làm thế nào để đăng ký thêm một chỗ đậu xe ô tô tòa {b} theo tháng?",
    ]),
    # SV-01 hỏi dự án
    ("NEUTRAL","SEV-4","SV-01","IS-01-01","C","C1","INCLUDED",[
        "Cho tôi hỏi tiến độ bàn giao căn hộ tòa {b} đợt tới dự kiến tháng mấy?",
        "Chính sách thanh toán mua căn hộ tòa {b} hiện tại có ưu đãi gì không?",
        "Diện tích căn hộ {f} phòng ngủ tòa {b} trung bình là bao nhiêu m2?",
        "Có căn hộ tầng cao view hướng sông tòa {b} còn hàng không? Giá khoảng bao nhiêu?",
    ]),
]

# ================= PRAISE 15% =================
PRAISES = [
    ("POSITIVE","SEV-4","SV-08","IS-08-03","RES","RES-07","INCLUDED",[
        "Bảo vệ tòa {b} ca đêm rất nhiệt tình, luôn chào hỏi và hỗ trợ cư dân. Cảm ơn các bạn!",
        "Đội bảo vệ tòa {b} xử lý rất nhanh khi tôi báo có người lạ, chuyên nghiệp lắm.",
        "Bảo vệ tòa {b} nhắc nhở người đậu xe sai chỗ rất lịch sự và hiệu quả. Khen ngợi!",
        "Ca trực đêm tòa {b} rất tích cực, tuần tra thường xuyên tôi thấy rất yên tâm.",
    ]),
    ("POSITIVE","SEV-4","SV-07","IS-07-03","RES","RES-07","INCLUDED",[
        "Đội kỹ thuật tòa {b} sửa điện cho căn hộ tôi rất nhanh, chỉ {t} phút là xong. Tuyệt vời!",
        "Nhân viên kỹ thuật tòa {b} xử lý tắc cống rất chuyên nghiệp, không để lại vết bẩn. Cảm ơn!",
        "Thang máy tòa {b} vừa được bảo dưỡng xong, chạy êm và nhanh hơn nhiều. Hài lòng!",
        "Kỹ thuật viên đến sửa điều hoà căn hộ rất đúng giờ và làm việc gọn gàng. Khen anh ấy!",
        "Sự cố điện tòa {b} tối qua được khắc phục trong {t} phút, nhanh hơn tôi mong đợi.",
    ]),
    ("POSITIVE","SEV-4","SV-03","IS-03-03","RES","RES-02","INCLUDED",[
        "Lễ tân tòa {b} hỗ trợ tôi làm thủ tục rất nhanh và thân thiện. Dịch vụ 5 sao!",
        "Nhân viên CSKH tòa {b} giải đáp thắc mắc phí quản lý rất rõ ràng và kiên nhẫn.",
        "App cư dân tòa {b} cập nhật tính năng mới rất tiện lợi, đặt dịch vụ chỉ {t} bước!",
        "Bộ phận hỗ trợ kỹ thuật app cư dân xử lý lỗi đăng nhập của tôi rất nhanh.",
    ]),
    ("POSITIVE","SEV-4","SV-09","IS-09-02","RES","RES-07","INCLUDED",[
        "Cảnh quan khu nội khu tòa {b} được chăm sóc rất đẹp, hoa nở quanh năm. Tuyệt quá!",
        "Đội vệ sinh tòa {b} làm việc rất siêng năng, hành lang lúc nào cũng sạch bóng.",
        "Khu vực hồ bơi tòa {b} được vệ sinh sạch sẽ, nước trong xanh. Rất hài lòng!",
        "Tòa {b} ngày càng xanh sạch đẹp hơn, ban quản lý làm tốt lắm. Trân trọng!",
    ]),
    ("POSITIVE","SEV-4","SV-06","IS-06-03","RES","RES-05","INCLUDED",[
        "Hồ bơi tòa {b} sạch và rộng rãi, nhân viên cứu hộ chuyên nghiệp. Con tôi rất thích!",
        "Phòng gym tòa {b} được nâng cấp máy mới rất xịn, cảm ơn ban quản lý đã lắng nghe ý kiến.",
        "Buổi tiệc BBQ khu sân thượng tòa {b} được hỗ trợ rất chu đáo. Cư dân ai cũng khen.",
        "Dịch vụ chuyển nhà tòa {b} hỗ trợ tận tình, nhân viên khênh đồ cẩn thận không trầy xước gì.",
    ]),
    ("POSITIVE","SEV-4","SV-05","IS-05-04","RES","RES-03","INCLUDED",[
        "Cột sạc xe điện tòa {b} vừa được lắp thêm, rất tiện cho cư dân dùng xe điện. Cảm ơn!",
        "Bãi xe tòa {b} được sắp xếp lại gọn gàng hơn, dễ tìm chỗ đỗ hơn nhiều.",
    ]),
    ("POSITIVE","SEV-4","SV-02","IS-02-02","HO","HO-03","INCLUDED",[
        "Đội bảo hành tòa {b} đến đúng hẹn và sửa xong trong ngày. Chuyên nghiệp tuyệt vời!",
        "Quá trình bàn giao căn hộ tòa {b} rất suôn sẻ, nhân viên hướng dẫn tận tình từng chi tiết.",
    ]),
]

# ================= SPAM/TEST 10% =================
SPAM = [
    ("NEUTRAL","SEV-4","SV-10","IS-10-01","RES","RES-07","EXCLUDED",[
        "alo alo test 123 thử chức năng",
        "hello",
        "test",
        "1234567890",
        "alo",
        "aaa bbb ccc",
        "...",
        "test test test",
        "thử gửi tin nhắn xem có được không",
        "oke",
        "ok",
        ".",
        "abc xyz",
        "đây là tin nhắn thử nghiệm",
        "test gửi thử",
        "1",
        "vào để test thôi",
    ]),
    ("NEUTRAL","SEV-4","SV-10","IS-10-02","RES","RES-07","EXCLUDED",[
        "Bán xe máy Honda Wave cũ {cnt} triệu, còn mới 90%, liên hệ: 09xx.xxx.xxx",
        "Cho thuê căn hộ {f} PN tòa {b} giá {cnt} triệu/tháng, nội thất đầy đủ. LH: 09xx.xxx.xxx",
        "Mua bán căn hộ tòa {b}, giá tốt nhất thị trường, LH ngay để được tư vấn",
        "Dịch vụ dọn nhà, vệ sinh công nghiệp giá rẻ, call: 09xx.xxx.xxx",
        "Cho thuê xe tự lái, ô tô 4-7 chỗ, giá chỉ từ {cnt}k/ngày",
        "Bán chó Poodle thuần chủng giá {cnt} triệu, gia đình nuôi. Liên hệ zalo",
        "Nhận sửa điều hoà, tủ lạnh tại nhà, giá sinh viên, gọi ngay 09xx",
        "Dịch vụ thiết kế nội thất, báo giá miễn phí, ib ngay",
        "Mua bán ký gửi căn hộ chung cư nhanh chóng, hoa hồng hấp dẫn",
        "Free ship đơn từ 99k - giảm 50% hôm nay thôi, order ngay!",
    ]),
    ("POSITIVE","SEV-4","SV-10","IS-10-03","RES","RES-07","EXCLUDED",[
        "chào mọi người",
        "Chào buổi sáng!",
        "Hi hi",
        "cảm ơn bạn nhiều lắm",
        "haha okie",
        "ok cảm ơn nhé",
    ]),
]

# Helpers
def rand_floor(): return random.randint(2, 35)
def rand_apt(): return f"{random.randint(2,35)}{random.choice(['01','02','03','04','05','06','07','08'])}"
def rand_count(): return random.randint(2, 10)
def rand_n(): return random.randint(1, 6)
def rand_h(): return random.randint(22, 23) if random.random() < 0.5 else random.randint(0, 3)
def rand_m(): return random.randint(1, 8)
def rand_minutes(): return random.randint(5, 45)

def fill_template(tmpl, building):
    b_short = building.split(" - ")[0]
    s = tmpl
    s = s.replace("{b}", b_short)
    s = s.replace("{f}", str(rand_floor()))
    s = s.replace("{apt}", rand_apt())
    s = s.replace("{t}", str(rand_minutes()))
    s = s.replace("{n}", str(rand_n()))
    s = s.replace("{cnt}", str(rand_count()))
    s = s.replace("{h}", str(rand_h()))
    s = s.replace("{m}", str(rand_m()))
    return s

def rand_date():
    start = datetime(2026, 4, 1)
    end = datetime(2026, 8, 18)
    delta = end - start
    rd = start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))
    return rd.replace(tzinfo=timezone.utc)

async def main():
    TOTAL = 10000
    N_COMPLAINT = int(TOTAL * 0.55)
    N_INQUIRY   = int(TOTAL * 0.20)
    N_PRAISE    = int(TOTAL * 0.15)
    N_SPAM      = TOTAL - N_COMPLAINT - N_INQUIRY - N_PRAISE

    def sample_from_bucket(bucket, n):
        records = []
        for _ in range(n):
            meta_templates = random.choice(bucket)
            meta = meta_templates[:7]
            templates = meta_templates[7]
            tmpl = random.choice(templates)
            building = random.choice(BUILDINGS)
            content = fill_template(tmpl, building)
            channel = random.choice(CHANNELS)
            dt = rand_date()
            records.append((meta, content, building, channel, dt))
        return records

    print("1. Generating 10,000 realistic records in-memory...")
    all_records = []
    all_records += sample_from_bucket(COMPLAINTS, N_COMPLAINT)
    all_records += sample_from_bucket(INQUIRIES, N_INQUIRY)
    all_records += sample_from_bucket(PRAISES, N_PRAISE)
    all_records += sample_from_bucket(SPAM, N_SPAM)
    random.shuffle(all_records)

    # Write CSV file
    print(f"2. Writing CSV to {OUT_CSV}...")
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([
            "ticket_id","content_masked","building","channel","reported_date",
            "sentiment","operational_severity","service_code","issue_code",
            "journey_stage","journey_step","analytic_eligibility"
        ])
        for idx, (meta, content, building, channel, dt) in enumerate(all_records, start=810001):
            sentiment, sev, svc, issue, stage, step, elig = meta
            writer.writerow([
                f"TC-{idx}",
                content,
                building,
                channel,
                dt.strftime("%Y-%m-%d %H:%M:%S"),
                sentiment,
                sev,
                svc,
                issue,
                stage,
                step,
                elig
            ])

    print("   CSV export completed!")

    # Ingest into DB
    print("3. Connecting to PostgreSQL and truncating old data...")
    async with AsyncSessionLocal() as session:
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

        # Register locations
        print("4. Ensuring all 7 buildings exist in location table...")
        loc_map = {}
        for b_name in BUILDINGS:
            lid = uuid4()
            b_code = "LOC-" + b_name.split(" - ")[0].replace("Tòa ", "").replace(".", "")
            await session.execute(
                text("""
                    INSERT INTO location (location_id, project_id, location_code, name, location_type, active)
                    VALUES (:id, :project_id, :code, :name, 'BUILDING', true)
                    ON CONFLICT (project_id, location_code) DO UPDATE SET name = EXCLUDED.name
                """),
                {"id": lid, "project_id": PROJECT_ID, "code": b_code, "name": b_name},
            )
            cur = await session.execute(
                text("SELECT location_id FROM location WHERE project_id = :project_id AND location_code = :code"),
                {"project_id": PROJECT_ID, "code": b_code},
            )
            loc_map[b_name] = cur.scalar_one()
        await session.commit()

        # Batch insert 10,000 items in chunks of 1,000
        print("5. Bulk inserting 10,000 records into PostgreSQL...")
        now = datetime.now(timezone.utc)
        feedback_batch = []
        item_batch = []
        decision_batch = []
        current_batch = []

        for idx, (meta, content, building, channel, dt) in enumerate(all_records, start=810001):
            sentiment, sev, svc, issue, stage, step, elig = meta
            ticket_id = f"TC-{idx}"
            f_id = uuid4()
            fi_id = uuid4()
            dec_id = uuid4()

            ch_code = CHANNEL_CODE_MAP.get(channel, "CH-APP")
            ch_id = channel_map.get(ch_code)
            loc_id = loc_map.get(building)

            svc_id = service_map.get(svc)
            iss_id = issue_map.get(issue)
            step_info = step_map.get(step)
            step_id = step_info[0] if step_info else None
            stage_id = step_info[1] if step_info else stage_map.get(stage)

            ex_reason = None if elig == "INCLUDED" else "NON_FEEDBACK"

            metadata = {
                "ticket_id": ticket_id,
                "building": building,
                "channel": channel,
                "reported_date": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "sentiment": sentiment,
                "service_code": svc,
                "issue_code": issue,
                "content_masked": content,
            }
            checksum = hashlib.sha256(content.encode()).hexdigest()

            feedback_batch.append({
                "feedback_id": f_id,
                "project_id": PROJECT_ID,
                "source_record_key": f"{ticket_id}_{f_id.hex[:6]}",
                "intake_channel_id": ch_id,
                "external_ticket_id": ticket_id,
                "reported_at": dt,
                "now": now,
                "content_raw": content,
                "content_masked": content,
                "source_metadata_json": json.dumps(metadata, ensure_ascii=False),
                "checksum": checksum,
            })

            item_batch.append({
                "feedback_item_id": fi_id,
                "feedback_id": f_id,
                "masked_content": content,
                "location_id": loc_id,
                "eligibility": elig,
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
                    "sentiment": sentiment,
                    "severity": sev,
                    "reported_at": dt,
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
                    "sentiment": sentiment,
                    "severity": sev,
                    "reported_at": dt,
                })

            if len(feedback_batch) >= 1000:
                await session.execute(
                    text("""
                        INSERT INTO feedback (
                            feedback_id, project_id, source_system, source_record_key,
                            intake_channel_id, external_ticket_id,
                            reported_at, ingested_at, content_raw, content_masked,
                            source_metadata_json, raw_content_checksum, created_at
                        ) VALUES (
                            :feedback_id, :project_id, 'direct-10k', :source_record_key,
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
                            'SOURCE_TRUSTED', 'Claude 10k Synthetic Seeder', UUID('00000000-0000-0000-0000-000000000002'), :reported_at
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
                feedback_batch.clear()
                item_batch.clear()
                decision_batch.clear()
                current_batch.clear()

        await session.commit()
        print("6. 10,000 records successfully committed to Database!")


asyncio.run(main())
