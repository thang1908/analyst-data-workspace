# User story và tiêu chí chấp nhận

Mỗi tiêu chí dưới đây phải kiểm thử được. Trừ khi nêu khác, mọi mutation cần phân quyền, idempotency, ghi lịch sử và kiểm tra `base_version_id`.

## US-001 — Nhập CSV

**Là một** Data Analyst, **tôi muốn** tải dữ liệu CSV lên **để** bắt đầu làm sạch mà không cần viết mã.

Tiêu chí chấp nhận:

- có preview trước khi commit;
- UTF-8 tiếng Việt hiển thị đúng;
- delimiter và encoding được phát hiện, có thể ghi đè;
- kiểu cột suy luận được hiển thị;
- người dùng chọn được dòng header;
- import tạo dataset, phiên bản đầu tiên và sự kiện `IMPORT_SOURCE`;
- tệp gốc cùng checksum được giữ nguyên;
- lỗi parse nêu dòng/cột có vấn đề mà không lộ dữ liệu nhạy cảm trong log.

## US-002 — Nhập sheet XLSX

Tiêu chí chấp nhận:

- liệt kê mọi sheet đọc được;
- người dùng chọn một hoặc nhiều sheet, mặc định mỗi sheet tạo một dataset;
- xem trước 50 dòng đầu;
- không bao giờ thực thi macro;
- công thức được nhập theo chính sách đã công bố (giá trị cached hoặc cảnh báo nếu không có);
- tệp gốc có thể tải lại/khôi phục.

## US-003 — Sửa một ô

Tiêu chí chấp nhận:

- double-click, Enter hoặc gõ trực tiếp để sửa;
- giá trị sai kiểu bị từ chối với thông báo rõ ràng;
- UI hiển thị trạng thái Saving/Saved/Failed;
- chỉnh sửa thành công vẫn tồn tại sau refresh;
- thao tác xuất hiện trong lịch sử;
- undo khôi phục giá trị cũ;
- xung đột phiên bản không ghi đè thay đổi mới hơn.

## US-004 — Dán một vùng dữ liệu

Tiêu chí chấp nhận:

- dữ liệu clipboard phân tách bằng tab/xuống dòng được ánh xạ vào ô;
- kiểm tra toàn bộ vùng trước khi commit;
- MVP áp dụng nguyên tử: chỉ một ô lỗi thì không ô nào được ghi;
- nếu vượt số dòng hiện có, người dùng phải xác nhận tạo thêm dòng;
- một lần dán thành công là một nhóm thao tác có thể undo.

## US-005 — Lọc mà không xóa

Tiêu chí chấp nhận:

- filter thay đổi số dòng hiển thị;
- view đã lưu được giữ sau refresh;
- tổng số dòng của dataset không đổi;
- xóa filter khôi phục các dòng;
- UI phân biệt rõ “Lọc dòng” và “Xóa dòng khớp điều kiện”.

## US-006 — Xóa dòng theo quy tắc

Tiêu chí chấp nhận:

- người dùng chọn quy tắc và phạm vi;
- hệ thống hiển thị số dòng bị ảnh hưởng và mẫu trước/sau;
- phiên bản thay đổi sau preview làm apply bị từ chối;
- apply tạo phiên bản dataset mới;
- undo khôi phục các dòng.

## US-007 — Chuyển kiểu dữ liệu

Tiêu chí chấp nhận:

- hệ thống quét và thống kê giá trị không hợp lệ;
- ví dụ lỗi được hiển thị có giới hạn;
- chưa xác nhận thì không có thay đổi;
- chính sách xử lý giá trị lỗi và định dạng parse được lưu trong parameters;
- raw source không thay đổi.

## US-008 — Loại trùng

Tiêu chí chấp nhận:

- người dùng chọn một hoặc nhiều cột khóa;
- hiển thị số nhóm trùng và số dòng sẽ xóa;
- có tùy chọn giữ dòng đầu/cuối với thứ tự xác định;
- hiển thị số dòng kết quả;
- operation có thể hoàn tác.

## US-009 — Xem profiling cột

Tiêu chí chấp nhận:

- có số null và distinct;
- có metric theo kiểu dữ liệu;
- profile nêu `version_id` và thời điểm tính;
- profile phản ánh phiên bản biến đổi hiện tại hoặc được đánh dấu rõ là stale/computing.

## US-010 — Xem lịch sử

Tiêu chí chấp nhận:

- danh sách theo thời gian và có phân trang;
- hiển thị actor, thời gian, loại, trạng thái và số dòng ảnh hưởng;
- có chi tiết cho biến đổi hàng loạt;
- chỉ bước có thể hoàn tác mới nhất được undo trong MVP;
- redo bị vô hiệu khi có nhánh chỉnh sửa mới.

## US-011 — Xuất bộ dữ liệu sạch

Tiêu chí chấp nhận:

- hỗ trợ CSV và XLSX;
- phạm vi all/filtered được mô tả bằng filter tái lập được;
- export gắn với một `version_id` cụ thể;
- số dòng xuất khớp phạm vi;
- Unicode, ngày và null tuân theo hợp đồng đã công bố;
- áp dụng chính sách giảm thiểu CSV formula injection;
- URL tải xuống có thời hạn và được phân quyền.

## US-012 — Tái sử dụng pipeline (Giai đoạn 1.1)

Tiêu chí chấp nhận:

- lưu chuỗi operation có tên và version schema;
- áp dụng được lên dataset tương thích;
- kiểm tra trước cột, kiểu và quyền cần thiết;
- xem trước tác động kết hợp trước khi chạy;
- thất bại giữa chừng không để lại phiên bản commit một phần.

## US-013 — Biến đổi bằng ngôn ngữ tự nhiên (Giai đoạn 2)

Ví dụ prompt:

```text
Xóa các dòng không có ngày và trim cột building.
```

Tiêu chí chấp nhận:

- AI chỉ tạo kế hoạch operation tuân thủ schema;
- cột không tồn tại hoặc mơ hồ sẽ ngăn thực thi;
- người dùng thấy phạm vi, cảnh báo và số dòng ảnh hưởng;
- không mutation trước khi phê duyệt;
- checkpoint được tạo trước kế hoạch nhiều bước;
- lịch sử lưu người khởi tạo, chỉ dẫn, người phê duyệt và operation cụ thể;
- nội dung ô không thể điều khiển planner như chỉ dẫn hệ thống.
