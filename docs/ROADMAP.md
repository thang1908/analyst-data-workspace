# Lộ trình sản phẩm

## Giai đoạn 0 — Thử nghiệm kỹ thuật và UX

Xác thực trước khi chốt kiến trúc:

1. so sánh AG Grid và Handsontable với 100.000 dòng;
2. chiến lược chỉnh sửa DuckDB/Parquet;
3. chi phí lưu undo/version;
4. các trường hợp biên khi đọc CSV/XLSX.

**Điều kiện kết thúc:** lựa chọn grid và chiến lược versioning được đo lường, lập biên bản quyết định và có prototype đáp ứng luồng chuẩn.

## Giai đoạn 1 — MVP Data Workspace

**Kết quả:** tệp thô → bộ dữ liệu sạch, sẵn sàng phân tích mà không cần viết mã.

Hạng mục:

- nhập dữ liệu;
- CRUD trên grid;
- lọc/sắp xếp/tìm kiếm;
- schema có kiểu;
- Operation Engine;
- phép biến đổi;
- profiling;
- lịch sử;
- undo/redo;
- xuất dữ liệu.

## Giai đoạn 1.1 — Không gian biến đổi có thể tái sử dụng

Hạng mục:

- cột tính toán;
- group by;
- pivot;
- join;
- append;
- pipeline đã lưu;
- checkpoint có tên và khôi phục phiên bản.

## Giai đoạn 1.2 — Phân tích

Hạng mục:

- vai trò ngữ nghĩa của trường;
- trình tạo metric;
- trình tạo biểu đồ;
- dashboard;
- bộ lọc toàn cục.

## Giai đoạn 1.3 — Dữ liệu kết nối

Hạng mục:

- PostgreSQL/MySQL;
- Snowflake/BigQuery/Redshift;
- quản lý kết nối và secrets;
- ưu tiên truy vấn chỉ đọc;
- SQL pushdown;
- làm mới theo lịch.

## Giai đoạn 2 — AI Data Assistant

Hạng mục:

- lập kế hoạch thao tác từ ngôn ngữ tự nhiên;
- dịch vụ ngữ cảnh bộ dữ liệu;
- operation DSL;
- kiểm tra;
- xem trước;
- phê duyệt;
- checkpoint;
- bộ đánh giá.

## Giai đoạn 3 — AI Analyst

Hạng mục:

- hỏi đáp trên dữ liệu;
- lập kế hoạch truy vấn bằng ngôn ngữ tự nhiên;
- tạo biểu đồ;
- phát hiện insight và bất thường;
- giải thích kèm truy vấn/thao tác có thể truy vết.

## Giai đoạn 4 — Enterprise

Khả năng dự kiến:

- SSO/SAML;
- RBAC nâng cao;
- chính sách theo hàng/cột;
- writeback vào warehouse;
- xuất nhật ký kiểm toán;
- cộng tác;
- công cụ quản trị;
- lineage;
- chính sách nhà cung cấp AI cấp doanh nghiệp.

Mỗi giai đoạn chỉ bắt đầu sau khi đạt release gate của giai đoạn trước; không dùng tính năng giai đoạn sau để bù cho thiếu sót về tính toàn vẹn dữ liệu của MVP.
