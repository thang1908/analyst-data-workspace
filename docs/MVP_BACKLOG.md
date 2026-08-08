# Backlog MVP

Quy ước ưu tiên: **P0** bắt buộc để pilot; **P1** quan trọng nhưng có thể hoãn nếu release gate vẫn đạt; **P2** nên có. Mỗi mục chỉ được xem là hoàn tất khi có kiểm thử tương ứng, observability tối thiểu và tài liệu API/UX liên quan.

## Epic 1 — Nền tảng

- P0 khung dự án frontend/backend;
- P0 xác thực;
- P0 bảng metadata workspace/dataset/version;
- P0 tích hợp object storage;
- P0 request ID và lỗi có cấu trúc;
- P0 migration và quy trình rollback;
- P0 phân quyền server-side theo role.

## Epic 2 — Nhập dữ liệu

- P0 parser và preview CSV;
- P0 parser XLSX và chọn sheet;
- P0 suy luận schema;
- P0 ID nội bộ ổn định cho dòng/cột;
- P0 giữ nguyên tệp thô cùng checksum;
- P0 không thực thi macro và xác thực content type;
- P1 ghi đè encoding/delimiter;
- P1 chính sách công thức XLSX và cảnh báo giá trị cached.

## Epic 3 — Grid

- P0 grid ảo hóa chỉ đọc;
- P0 cửa sổ dòng phía server;
- P0 sửa ô;
- P0 thêm/xóa dòng;
- P0 thêm/xóa/đổi tên cột;
- P0 dán clipboard nguyên tử;
- P0 điều hướng bàn phím;
- P1 cố định cột;
- P1 lưu thứ tự/độ rộng cột trong view.

## Epic 4 — Thao tác view

- P0 filter có kiểu và filter chip;
- P0 sắp xếp đơn/đa cột;
- P0 tìm kiếm toàn cục;
- P1 saved view.

## Epic 5 — Operation Engine

- P0 operation schema có phiên bản;
- P0 validator quyền/schema/tham số;
- P0 dry run và preview token;
- P0 apply nguyên tử;
- P0 idempotency và phát hiện dùng lại key với payload khác;
- P0 phát hiện xung đột base version;
- P0 hợp đồng kết quả operation;
- P0 compare-and-swap/locking khi commit version.

## Epic 6 — Lịch sử và versioning

- P0 timeline và chi tiết operation;
- P0 undo/redo tuyến tính;
- P0 chiến lược checkpoint/compaction;
- P0 kiểm thử khôi phục sau lỗi worker/storage;
- P1 cấu hình retention.

Checkpoint có tên và khôi phục phiên bản tùy ý thuộc **Giai đoạn 1.1**, không phải MVP.

## Epic 7 — Phép biến đổi

- P0 replace value;
- P0 chuyển kiểu dữ liệu;
- P0 trim và đổi hoa/thường;
- P0 điền null bằng hằng số;
- P0 xóa dòng null;
- P0 loại trùng với thứ tự xác định;
- P0 tách/gộp cột;
- P0 trích xuất phần ngày;
- P0 xóa dòng khớp điều kiện;
- P0 chọn phạm vi all/filtered/selected rõ ràng.

## Epic 8 — Profiling

- P0 tổng quan dataset;
- P0 profile text/numeric/date;
- P0 profile gắn với version và có trạng thái freshness;
- P1 biểu đồ phân phối thu nhỏ.

## Epic 9 — Xuất dữ liệu

- P0 CSV và XLSX;
- P0 phạm vi all/filtered có thể tái lập;
- P0 audit export;
- P0 signed URL có thời hạn;
- P0 giảm thiểu CSV formula injection;
- P0 kiểm thử Unicode/ngày/null và đối soát số dòng.

## Epic 10 — Tác vụ nền và observability

- P0 API trạng thái job và tiến độ;
- P0 retry an toàn/idempotent;
- P0 xử lý job treo và object mồ côi;
- P0 metric latency/import/operation/export/queue;
- P0 log có request/job ID và không chứa giá trị ô theo mặc định.

## Epic 11 — Hardening

- P0 benchmark tải grid 100.000 dòng;
- P0 benchmark filter và bulk transform;
- P0 kiểm thử kiểm soát truy cập;
- P0 bảo mật upload;
- P0 trường hợp biên Unicode/CSV/XLSX;
- P0 kiểm thử recovery và version conflict;
- P0 kiểm thử tính nguyên tử khi paste/transform;
- P1 accessibility review.

## Không thuộc MVP

- dashboard;
- AI;
- SQL editor;
- Python notebook;
- kết nối database trực tiếp;
- cộng tác thời gian thực;
- công thức đầy đủ;
- VBA/macro;
- pipeline tái sử dụng;
- checkpoint có tên và khôi phục phiên bản tùy ý.
