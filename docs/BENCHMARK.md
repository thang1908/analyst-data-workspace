# Đối chuẩn thị trường

Mục đích của tài liệu là rút ra mẫu thiết kế sản phẩm, không sao chép đối thủ theo từng tính năng. Các nhận định dưới đây là suy luận sản phẩm từ tài liệu chính thức, được kiểm tra truy cập ngày **2026-08-08**; khả năng thực tế còn phụ thuộc gói dịch vụ và phiên bản của từng sản phẩm.

## 1. Microsoft Excel + Power Query + Copilot

### Mẫu nên học hỏi từ Microsoft

- tương tác grid quen thuộc;
- nguồn không đổi và một biểu diễn truy vấn đã biến đổi;
- Applied Steps/lịch sử;
- xem trước phép biến đổi;
- AI thao tác thông qua khả năng gốc của workbook;
- tách lập kế hoạch và chỉnh sửa đối với tác vụ AI phức tạp.

### Không nên sao chép trong MVP

- engine định dạng đầy đủ;
- ngôn ngữ công thức đầy đủ;
- macro/VBA;
- tính năng bố cục tài liệu văn phòng.

Nguồn chính thức:

- [Giới thiệu Power Query trong Excel](https://support.microsoft.com/en-US/Excel/about-power-query-in-excel)
- [Xem lại Applied Steps](https://support.microsoft.com/en-us/excel/get-started/review-the-applied-steps)
- [Bắt đầu với Copilot trong Excel](https://support.microsoft.com/en-US/Excel/copilot/get-started-with-copilot-in-excel)

## 2. Grist

### Mẫu nên học hỏi từ Grist

- UX bảng tính xây trên mô hình bản ghi/bảng;
- cột có kiểu;
- xem trước và ánh xạ khi nhập;
- mô hình dữ liệu có cấu trúc, được thể hiện rõ;
- công thức là một lớp phía trên bản ghi có cấu trúc.

Nguồn chính thức:

- [Nhập dữ liệu vào Grist](https://support.getgrist.com/imports/)
- [Công thức trong Grist](https://support.getgrist.com/formulas/)

## 3. Quadratic

### Mẫu nên học hỏi từ Quadratic

- một không gian bảng tính hợp nhất;
- SQL, Python và công thức có thể cùng tồn tại ở giai đoạn sau;
- lịch sử phiên bản;
- kết nối dữ liệu;
- AI tạo logic có thể kiểm tra thay vì chỉ trả kết quả “hộp đen”;
- phân tích có thể lặp lại.

Nguồn chính thức:

- [Tài liệu Quadratic](https://docs.quadratichq.com/)
- [Kết hợp dữ liệu](https://www.quadratichq.com/solutions/combining-data)
- [Phân tích dữ liệu từ database](https://www.quadratichq.com/solutions/database-analytics)

## 4. Rows

### Mẫu nên học hỏi từ Rows

- panel AI cạnh bảng tính;
- checkpoint quanh thao tác AI nhiều bước;
- cho AI gọi khả năng biến đổi đã có;
- hành động dọn dẹp/find-replace rõ ràng.

Nguồn chính thức:

- [Sử dụng AI Analyst](https://rows.com/docs/using-the-rows-ai-analyst?category=ai)
- [Dùng Rows AI để làm sạch dữ liệu](https://rows.com/docs/using-rowsai-to-clean-up-data)

## 5. Sourcetable

### Mẫu nên học hỏi từ Sourcetable

- bảng tính là bề mặt tương tác trung tâm;
- connector, biến đổi và phân tích trong một workspace;
- AI là lớp điều khiển bằng ngôn ngữ tự nhiên.

Nguồn chính thức: [Tài liệu Sourcetable](https://sourcetable.com/docs)

## 6. Sigma

### Mẫu nên học hỏi từ Sigma cho giai đoạn sau

- UX bảng tính trên dữ liệu warehouse đang hoạt động;
- đẩy phép lọc/group by/pivot/công thức xuống warehouse;
- kiểm toán thay đổi;
- writeback được quản trị tách biệt khỏi dữ liệu nguồn;
- quyền trên warehouse vẫn là nguồn thẩm quyền.

Nguồn chính thức:

- [Spreadsheet trên dữ liệu warehouse](https://www.sigmacomputing.com/product/spreadsheets)
- [Kiến trúc Sigma](https://www.sigmacomputing.com/product/architecture)
- [Tổng quan Input Tables](https://help.sigmacomputing.com/docs/intro-to-input-tables)

## 7. Khoảng trống sản phẩm nên theo đuổi

Sản phẩm nên tập trung chặt vào **chuẩn bị dữ liệu sẵn sàng cho phân tích**, thay vì tự định vị là một bảng tính đa dụng.

Luồng mục tiêu:

```text
Tệp thô
  ↓
Profiling
  ↓
Sửa / Biến đổi
  ↓
Xem trước
  ↓
Lịch sử / Undo
  ↓
Bộ dữ liệu sạch có thể tái sử dụng
```

Các lớp bổ sung về sau:

```text
Dashboard
  ↓
Trợ lý AI biến đổi dữ liệu
  ↓
AI Analyst
```

## 8. Kết luận áp dụng

Đối chuẩn củng cố bốn quyết định nền tảng:

1. giữ nguồn thô bất biến và lưu các bước biến đổi;
2. dùng ngữ nghĩa bảng/bản ghi bên dưới UX giống spreadsheet;
3. thực thi ở nơi dữ liệu nằm khi chuyển sang quy mô warehouse;
4. AI chỉ điều phối các công cụ đã được kiểm tra, không có đường ghi dữ liệu riêng.

Đây là định hướng kiến trúc, không phải bằng chứng rằng một cách triển khai cụ thể sẽ đạt hiệu năng hoặc mức độ an toàn mong muốn; các quyết định kỹ thuật vẫn phải qua benchmark và security review nội bộ.
