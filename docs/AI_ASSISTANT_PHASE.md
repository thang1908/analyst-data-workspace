# AI Data Assistant — Đặc tả giai đoạn tương lai

AI không thuộc phạm vi MVP. Tài liệu này xác định các ràng buộc để kiến trúc MVP vẫn tương thích với AI về sau.

## 1. Mục tiêu

Cho phép người dùng mô tả phép biến đổi bằng ngôn ngữ tự nhiên mà không làm giảm tính an toàn hoặc khả năng tái lập.

Ví dụ:

```text
Chuẩn hóa cột building, đổi N/A thành null, xóa các bản ghi không có ngày và tạo cột month.
```

## 2. AI được phép

- đọc schema và metadata profiling của bộ dữ liệu;
- đề xuất các thao tác nằm trong danh mục được hỗ trợ;
- xâu chuỗi nhiều thao tác được hỗ trợ;
- giải thích kế hoạch thao tác;
- yêu cầu làm rõ khi chỉ dẫn có điểm mơ hồ ảnh hưởng đáng kể đến kết quả;
- gọi chức năng xem trước;
- chỉ áp dụng sau khi đáp ứng chính sách phê duyệt.

## 3. AI không được phép

- sửa trực tiếp nguồn dữ liệu thô;
- thực thi shell code tùy ý;
- truy cập bộ dữ liệu không liên quan;
- bỏ qua phân quyền;
- tự đặt tên cột không tồn tại rồi tiếp tục thực thi;
- âm thầm áp dụng thao tác phá hủy dữ liệu;
- chạy SQL không giới hạn trên nguồn production có quyền ghi.

## 4. Ngữ cảnh cung cấp cho mô hình

Chỉ cung cấp ngữ cảnh tối thiểu cần thiết:

- tên bộ dữ liệu;
- tên và ID ổn định của cột;
- kiểu logic;
- gợi ý ngữ nghĩa;
- thống kê profiling theo cột;
- mẫu nhỏ, đại diện khi thực sự cần;
- danh mục thao tác được hỗ trợ;
- quyền hiện tại của người dùng và giới hạn phạm vi.

Không gửi toàn bộ bộ dữ liệu cho mô hình theo mặc định. Dữ liệu mẫu phải được giới hạn, ghi nhận và tuân thủ chính sách workspace.

## 5. Đầu ra của planner

Planner phải trả về JSON tuân thủ schema có phiên bản; không chấp nhận văn bản tự do làm lệnh thực thi.

```json
{
  "schema_version": "1.0",
  "intent": "clean_dataset",
  "operations": [
    {
      "operation_type": "REPLACE_VALUE",
      "parameters": {
        "column_id": "col_building",
        "from": "N/A",
        "to": null
      }
    }
  ]
}
```

## 6. Kiểm tra

Máy chủ phải tự kiểm tra mọi thao tác do AI tạo, gồm quyền truy cập, sự tồn tại của cột, kiểu dữ liệu, phạm vi, phiên bản cơ sở và tham số thao tác.

Không được tin đầu ra mô hình chỉ vì nó khớp JSON Schema.

## 7. Giao diện xem trước

```text
AI đề xuất 3 thao tác

1. Đổi N/A thành null trong building — 82 dòng
2. Xóa dòng có reported_date là null — 231 dòng
3. Tạo month từ reported_date — 18.315 dòng

Trước: 18.546 dòng
Sau:   18.315 dòng

[Xem dữ liệu bị ảnh hưởng]
[Hủy]
[Áp dụng 3 thao tác]
```

Giao diện phải chỉ rõ thao tác phá hủy, cảnh báo, lỗi kiểm tra, phạm vi và phiên bản sẽ được áp dụng.

## 8. Checkpoint và tính nguyên tử

Trước khi áp dụng kế hoạch AI nhiều bước, hệ thống tạo checkpoint. Toàn bộ kế hoạch nên được áp dụng theo kiểu nguyên tử; nếu một bước thất bại thì giữ nguyên phiên bản đã commit gần nhất và báo chính xác bước lỗi.

## 9. Kiểm toán

Lịch sử phải lưu cả:

- chỉ dẫn ngôn ngữ tự nhiên của người dùng;
- model/provider và phiên bản planner theo chính sách;
- kế hoạch thao tác chính xác đã được duyệt;
- người phê duyệt, thời gian và kết quả thực thi.

Prompt đơn lẻ không phải là nhật ký kiểm toán đầy đủ. Không lưu dữ liệu nhạy cảm trong log ngoài phạm vi chính sách.

## 10. Đánh giá

Xây dựng bộ prompt kiểm thử đi kèm kế hoạch thao tác mong đợi. Đo lường:

- tỷ lệ khớp chính xác thao tác;
- độ chính xác khi liên kết tên/ID cột;
- tỷ lệ từ chối thao tác không an toàn;
- tỷ lệ xem trước/áp dụng thành công;
- tỷ lệ người dùng phải sửa kế hoạch;
- tỷ lệ undo sau thao tác AI;
- tỷ lệ rò rỉ hoặc gửi ngữ cảnh vượt mức cho phép.

Các tình huống kiểm thử bắt buộc gồm cột không tồn tại, tên cột gần giống, prompt injection trong ô dữ liệu, yêu cầu vượt quyền, thao tác phá hủy diện rộng và xung đột phiên bản.

## 11. Tách biệt AI biến đổi và AI phân tích

AI Data Assistant thay đổi dữ liệu thông qua Operation Engine. AI Analyst phân tích thông qua công cụ truy vấn/metric chỉ đọc.

Không gộp hai mô hình quyền này: quyền phân tích không đồng nghĩa với quyền thay đổi dữ liệu.
