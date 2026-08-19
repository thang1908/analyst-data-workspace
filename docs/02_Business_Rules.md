# 02 — Quy tắc Nghiệp vụ (Business Rules)

# CX Intelligence & Operations Platform

**Phiên bản tài liệu:** 1.2 — cập nhật khớp implementation  
**Trạng thái:** ✅ Đồng bộ với codebase (Migration 020, API v1.1.0)  
**Dẫn xuất từ:** `docs/03_service_taxonomy.md` v3.1.0, `packages/domain/shared/enums.py`, migration 016–020  
**Phạm vi:** P0 đã triển khai đầy đủ; P1 đã implement một phần; P2 reserved  
**Mục đích:** Quy tắc nghiệp vụ domain được triển khai trong schema DB, API, `packages/domain/`, kiểm thử tự động.

> **Thay đổi từ v1.1:**
> - Thêm quy tắc Touchpoint (BR-TP-*) — migration 019
> - Thêm quy tắc Action Priority cho Hotspot — `packages/domain/hotspot/engine.py`
> - Cập nhật Hotspot status: thêm **REOPENED** và chuyển đổi ASSIGN → INVESTIGATING
> - Channel codes trong DB dùng chữ thường (ch-app, ch-hotline...) thay vì CH-APP
> - Import pipeline: thêm Direct CSV mode (đồng bộ, không cần worker)

---

## 1. Vai trò của Tài liệu

Tài liệu này là tầng quy tắc nghiệp vụ quy phạm nằm giữa PRD/taxonomy và việc triển khai (implementation).

```text
PRD
  ↓ định nghĩa hành vi và phạm vi sản phẩm
Taxonomy
  ↓ định nghĩa từ vựng chuẩn (canonical vocabulary) và ranh giới nhãn
Business Rules
  ↓ định nghĩa các bất biến (invariants) và các chuyển đổi trạng thái được phép
System Design
  ↓ ánh xạ các quy tắc đó vào kiến trúc/schema/API/job
Implementation
```

PRD giữ quyền quyết định cao nhất (authoritative) về phạm vi sản phẩm. `service_taxonomy.md` giữ quyền quyết định cao nhất về thuật ngữ chuẩn cho lifecycle/service/issue. Nếu tài liệu này có xung đột với một trong hai nguồn trên, xung đột phải được giải quyết bằng một quyết định được đánh phiên bản trước khi triển khai.

---

## 2. Ngôn ngữ Quy phạm

- **MUST / MUST NOT** — bất biến bắt buộc phải tuân thủ.
- **SHOULD / SHOULD NOT** — giá trị mặc định kỳ vọng; việc làm khác yêu cầu phải có lý do được ghi nhận bằng văn bản.
- **MAY** — hành vi tùy chọn.
- **P0** — bắt buộc cho bản thử nghiệm (pilot).
- **P1** — mở rộng vận hành.
- **P2** — trí tuệ nâng cao.

---

## 3. Mô hình Trạng thái Giá trị Cốt lõi

Các trường phân loại chưa biết (unknown) hoặc không áp dụng (inapplicable) MUST sử dụng một mô hình trạng thái giá trị (value-status model) rõ ràng.

```text
KNOWN
UNKNOWN
MISSING
NOT_APPLICABLE
```

Các quy tắc:

1. `KNOWN` MUST có một ID tham chiếu hợp lệ.
2. `UNKNOWN`, `MISSING`, và `NOT_APPLICABLE` MUST đặt ID tham chiếu thành `null`.
3. `UNKNOWN` có nghĩa là trường đã được đánh giá nhưng chưa thể xác định.
4. `MISSING` có nghĩa là nguồn/ngữ cảnh bắt buộc bị thiếu.
5. `NOT_APPLICABLE` có nghĩa là trường không áp dụng về mặt logic cho mục đó.
6. Hệ thống MUST NOT tự động chuyển đổi dữ liệu bị thiếu hoặc mơ hồ thành giá trị taxonomy.

---

# 4. Quy tắc về Feedback & Mục Nguyên tử (Atomic Item)

## BR-FB-001 — Raw Feedback Is Immutable

**Mức ưu tiên:** P0  
**Quy tắc:** `content_raw` MUST NOT được chỉnh sửa sau khi nạp dữ liệu (ingestion).

Các thành phần dẫn xuất như che mờ (masking), chuẩn hóa (normalization), tách mục (splitting), dự đoán (predictions), và quyết định (decisions) MUST được lưu trữ riêng biệt.

**Phương thức Thực thi**
- Chính sách cập nhật cơ sở dữ liệu/tầng dịch vụ (service layer).
- Kiểm toán truy cập đặc quyền vào nội dung thô.
- Các bài kiểm thử phải chứng minh rằng việc đính chính/tách mục không làm thay đổi envelope gốc.

---

## BR-FB-002 — Feedback Is an Envelope; Feedback Item Is the Analytic Unit

**Mức ưu tiên:** P0  
**Quy tắc:** Một bản ghi `Feedback` MUST chứa một hoặc nhiều bản ghi `Feedback Item`.

```text
Feedback 1 ─── N Feedback Item
```

Phân tích dữ liệu, xem xét phân loại và phát hiện điểm nóng (hotspot) MUST hoạt động dựa trên `feedback_item_id`, chứ không hoạt động trực tiếp trên vỏ bọc feedback (envelope).

---

## BR-FB-003 — One Item, One Atomic Intent or Observable Failure

**Mức ưu tiên:** P0  
**Quy tắc:** Một `Feedback Item` MUST đại diện cho một ý định của khách hàng hoặc một lỗi có thể quan sát được.

Nếu feedback nguồn chứa nhiều vấn đề độc lập, nó MUST được tách ra trước khi các vấn đề đó nhận các phân loại Primary Service/Issue khác nhau.

**Ví dụ**

```text
"Thang máy chậm và app cư dân không đăng nhập được."
```

phải trở thành tối thiểu:

```text
Item 1 → elevator problem
Item 2 → resident app problem
```

---

## BR-FB-004 — Split Must Preserve Provenance

**Mức ưu tiên:** P0  
**Quy tắc:** Việc tách mục (Splitting) MUST:
- bảo tồn `feedback_id` ban đầu;
- bảo tồn `content_raw`;
- tạo danh tính/chỉ mục mục mới (item identity/index);
- ghi nhận `split_source`, tác nhân (actor), nhãn thời gian (timestamp), và sự kiện kiểm toán (audit event);
- không bao giờ xóa lịch sử quyết định/dự đoán trước đó.

---

## BR-FB-005 — Location Cardinality

**Mức ưu tiên:** P0  
**Quy tắc:** Một Feedback Item MAY có không hoặc một `location_id` đã chuẩn hóa.

Hệ thống MUST NOT gắn nhiều địa điểm phân loại cho một mục nguyên tử (atomic item). Nếu một bản ghi thực sự mô tả các sự cố riêng biệt tại các địa điểm riêng biệt, hãy tách mục đó hoặc bảo tồn văn bản bổ sung dưới dạng bằng chứng/ngữ cảnh.

---

## BR-FB-006 — Affected Channel Cardinality

**Mức ưu tiên:** P0  
**Quy tắc:** Một Feedback Item MAY có từ không đến nhiều Kênh bị Ảnh hưởng (Affected Channels).

`intake_channel` và `affected_channel` là hai khái niệm khác nhau.

---

## BR-FB-007 — Source System Is Not a Channel

**Mức ưu tiên:** P0  
**Quy tắc:** CRM, ERP, BMS, CMMS, các nền tảng tổng đài/chăm sóc khách hàng (contact-center platforms), đường ống thu thập dữ liệu (crawler pipelines), và nguồn cấp dữ liệu cảm biến (sensor feeds) MUST được biểu diễn dưới dạng `source_system`, không phải dưới dạng các kênh `CH-*` chuẩn (canonical).

---

## BR-FB-008 — Symptom Detail Is Free Text

**Mức ưu tiên:** P0  
**Quy tắc:** `symptom_detail` là văn bản mô tả và MUST NOT được thăng cấp thành một Service/Issue mới chỉ vì mục đích chia nhỏ mức độ chi tiết (granularity) trên dashboard.

---

# 5. Quy tắc Vòng đời (Lifecycle Rules)

## BR-LIFE-001 — Two Independent Lifecycle Dimensions

**Mức ưu tiên:** P0  
**Quy tắc:** Vòng đời Khách hàng (Customer Lifecycle) và Vòng đời Yêu cầu Dịch vụ (Service Request Lifecycle) MUST được lưu trữ và truy vấn dưới dạng hai chiều độc lập.

```text
CUSTOMER_LIFECYCLE
SERVICE_REQUEST_LIFECYCLE
```

Mã `SRV-*` MUST NOT được lưu trữ dưới dạng một giai đoạn/bước (stage/step) của Customer Lifecycle.

---

## BR-LIFE-002 — Customer Lifecycle Cardinality

**Mức ưu tiên:** P0  
**Quy tắc:** Một Feedback Item MAY có tối đa một Step Vòng đời Khách hàng hiện tại.

Stage Vòng đời Khách hàng MUST được dẫn xuất từ Step đã chọn trong cùng một bản phát hành taxonomy.

Hệ thống SHOULD NOT yêu cầu mô hình AI hoặc người xem xét tự chọn độc lập cả stage và step khi step đã được xác định.

---

## BR-LIFE-003 — Service Request Lifecycle Cardinality

**Mức ưu tiên:** P0  
**Quy tắc:** Một Feedback Item MAY có tối đa một Service Request Step hiện tại.

Trường này MAY là `NOT_APPLICABLE` khi mục đó không mô tả luồng yêu cầu dịch vụ.

---

## BR-LIFE-004 — Lifecycle-to-Service Is N:N

**Mức ưu tiên:** P0  
**Quy tắc:** Một Lifecycle Step có thể ánh xạ tới nhiều Service, và một Service có thể ánh xạ tới nhiều Lifecycle Step.

Ánh xạ MUST bao gồm:
- loại vòng đời (lifecycle type);
- các ID cố định (stable IDs);
- ngày có hiệu lực (effective date);
- phiên bản/bản phát hành (version/release);
- trạng thái hoạt động/đã xuất bản (active/published state).

---

## BR-LIFE-005 — Lifecycle Mapping Does Not Auto-Classify

**Mức ưu tiên:** P0  
**Quy tắc:** Ánh xạ Lifecycle-Service là một không gian giới hạn/gợi ý, không phải là bằng chứng cho thấy một Service là chính xác.

Hệ thống MAY sử dụng ánh xạ để thu hẹp các giá trị ứng viên nhưng MUST NOT tự động tạo một phân loại được chấp nhận chỉ vì tồn tại một ánh xạ.

---

# 6. Quy tắc Phân loại (Taxonomy Rules)

## BR-TAX-001 — Canonical Release Shape

**Mức ưu tiên:** P0  
**Quy tắc:** Một bản phát hành taxonomy có thể xuất bản (publishable) MUST chứa:

- 6 Customer Lifecycle Stages;
- 36 Customer Journey Steps;
- 8 Service Request Steps;
- 10 active Services;
- 28 active Issues.

Ngoài ra:
- `SV-01` đến `SV-09` MUST mỗi Service chứa chính xác 3 Issues.
- `SV-10` MUST chứa chính xác 1 Issue: `IS-10-01`.

---

## BR-TAX-002 — Issue Belongs to Exactly One Service

**Mức ưu tiên:** P0  
**Quy tắc:** Mỗi Issue chuẩn MUST thuộc về chính xác một Service chuẩn trong một bản phát hành taxonomy.

---

## BR-TAX-003 — Stable Codes Are Never Reused

**Mức ưu tiên:** P0  
**Quy tắc:** Các mã/ID taxonomy đã xuất bản MUST NOT được gán lại cho một ý nghĩa ngữ nghĩa (semantic meaning) khác.

Các giá trị đã ngưng sử dụng (retired) vẫn giữ khả năng truy xuất lịch sử.

---

## BR-TAX-004 — No Hard Delete After Historical Use

**Mức ưu tiên:** P0  
**Quy tắc:** Các bản ghi và ánh xạ taxonomy được tham chiếu bởi dữ liệu lịch sử MUST NOT bị xóa cứng (hard-deleted).

Sử dụng ngữ nghĩa `RETIRED`/ngày có hiệu lực.

---

## BR-TAX-005 — Publish State Controls New Decisions

**Mức ưu tiên:** P0  
**Quy tắc:** Trạng thái Taxonomy MUST hỗ trợ:

```text
DRAFT → APPROVED → PUBLISHED → RETIRED
```

Chỉ các giá trị/bản phát hành ở trạng thái `PUBLISHED` mới được phép sử dụng cho các quyết định phân loại sản xuất (production) mới.

---

## BR-TAX-006 — Taxonomy Must Be Versioned

**Mức ưu tiên:** P0  
**Quy tắc:** Các quyết định feedback, dự đoán, ánh xạ, chỉ số (metrics), và quy tắc hotspot MUST giữ lại phiên bản taxonomy/quy tắc tương ứng để có thể tái tạo hành vi lịch sử.

---

## BR-TAX-007 — Application Must Not Hard-Code Labels

**Mức ưu tiên:** P0  
**Quy tắc:** UI/API/business logic MUST sử dụng các ID/mã cố định từ dữ liệu tham chiếu đã xuất bản thay vì nhúng trực tiếp từ ngữ chuẩn vào mã nguồn ứng dụng.

---

## BR-TAX-008 — Do Not Create Taxonomy From Operational Metadata

**Mức ưu tiên:** P0  
**Quy tắc:** Một Service hoặc Issue mới MUST NOT được tạo ra chỉ vì có sự khác biệt về:
- địa điểm (location);
- kênh (channel);
- hệ thống nguồn (source system);
- nhà cung cấp (vendor);
- nhà thầu (contractor);
- đơn vị giải quyết (resolver);
- đơn vị xử lý (handling unit);
- tài sản (asset);
- tòa nhà (building).

---

## BR-TAX-009 — SV-10 Is Controlled Fallback, Not Unknown

**Mức ưu tiên:** P0  
**Quy tắc:** `SV-10 / IS-10-01` MUST chỉ được sử dụng khi mục đó có thể hiểu được nhưng nằm ngoài phạm vi `SV-01..SV-09`.

Nó MUST NOT được sử dụng cho các bản ghi bị thiếu hoặc mơ hồ.

Khi được sử dụng:
- `other_reason` là bắt buộc;
- xem xét thủ công (human review) là bắt buộc;
- tỷ lệ sử dụng SHOULD được giám sát.

---

# 7. Quy tắc Quyết định Phân loại

## BR-CLS-001 — One Current Primary Service

**Mức ưu tiên:** P0  
**Quy tắc:** Nếu `primary_service_value_status=KNOWN`, projection hiện tại MUST chứa chính xác một `primary_service_id`.

Không có Secondary Service trong P0.

---

## BR-CLS-002 — Issue Must Match Primary Service

**Mức ưu tiên:** P0  
**Quy tắc:** Nếu `issue_value_status=KNOWN`, Issue MUST thuộc về Primary Service đã chọn trong cùng bản phát hành taxonomy.

Nếu Primary Service thay đổi và làm cho Issue hiện tại không hợp lệ, thao tác ghi MUST:
1. yêu cầu một Issue mới hợp lệ, hoặc
2. đặt trạng thái Issue thành `UNKNOWN` với `issue_id=null`.

---

## BR-CLS-003 — Decision Snapshot Is Atomic

**Mức ưu tiên:** P0  
**Quy tắc:** Một quyết định phân loại MUST đại diện cho một ảnh chụp (snapshot) hoàn chỉnh được đánh phiên bản về trạng thái phân loại đã được chấp nhận của mục đó.

Việc đính chính MUST tạo một `decision_version` mới; các quyết định trước đó MUST giữ nguyên tính bất biến.

---

## BR-CLS-004 — Current Projection Is Derived State

**Mức ưu tiên:** P0  
**Quy tắc:** `classification_current` là một read projection có thể tái tạo (rebuildable), không phải là nguồn sự thật (source of truth) cho kiểm toán.

Nguồn sự thật là lịch sử quyết định/xem xét theo cơ chế chỉ ghi thêm (append-only).

---

## BR-CLS-005 — Prediction Is Not an Accepted Decision

**Mức ưu tiên:** P0  
**Quy tắc:** Dự đoán của AI MUST NOT cập nhật trực tiếp phân loại hiện tại hoặc dữ liệu phân tích.

P0 chỉ áp dụng cơ chế gợi ý (suggest-only) đối với tất cả các giá trị độ tin cậy (confidence values).

---

## BR-CLS-006 — Accepted Sources

**Mức ưu tiên:** P0  
**Quy tắc:** `decision_source` MUST sử dụng chính xác enum chuẩn này trên toàn bộ các quy tắc, cơ sở dữ liệu, API và UI:

```text
MANUAL
SOURCE_TRUSTED
HUMAN_ACCEPTED_AI
HUMAN_CORRECTED_AI
POLICY_AUTO_APPLIED
SYSTEM_MIGRATION
```

Đối với P0, `POLICY_AUTO_APPLIED` MUST duy trì ở trạng thái vô hiệu hóa trừ khi được phê duyệt rõ ràng cho một trường rủi ro thấp cụ thể.

---

## BR-CLS-007 — Canonical Human Review Actions

**Mức ưu tiên:** P0  
**Quy tắc:** Việc xem xét kết quả AI MUST sử dụng chính xác:

```text
ACCEPT
CORRECT
MARK_UNKNOWN
MARK_MISSING
MARK_NOT_APPLICABLE
SPLIT_REQUIRED
SKIP
```

- `ACCEPT`, `CORRECT`, `MARK_UNKNOWN`, `MARK_MISSING`, `MARK_NOT_APPLICABLE` MUST tạo một `ClassificationDecision` bất biến và một `ReviewEvent`.
- `SPLIT_REQUIRED` và `SKIP` MUST chỉ tạo một `ReviewEvent`.
- Việc tách thực tế MUST sử dụng một mutation tách riêng biệt; nó tạo các Feedback Item con và MUST NOT tạo một quyết định cho item cha bị tách (split-parent).
- Các nhãn API/UI MAY được bản địa hóa, nhưng giá trị truyền nhận trên mạng (wire values) MUST giữ nguyên enum chuẩn ở trên.

---

## BR-CLS-008 — Stale Concurrent Decision Writes Are Rejected

**Mức ưu tiên:** P0  
**Quy tắc:** Một mutation quyết định MUST bao gồm/xác thực phiên bản quyết định hoặc projection trước đó kỳ vọng.

Nếu một tác nhân khác đã thay đổi mục đó trước, thao tác ghi bị lạc hậu (stale write) MUST thất bại với phản hồi xung đột (conflict response) thay vì ghi đè lên quyết định mới nhất.

---

## BR-CLS-009 — Manual Override Requires Audit

**Mức ưu tiên:** P0  
**Quy tắc:** Bất kỳ đính chính hoặc ghi đè thủ công nào MUST bao gồm:
- tác nhân (actor);
- nhãn thời gian (timestamp);
- lý do (reason);
- tham chiếu quyết định trước đó;
- tham chiếu quyết định kết quả.

---

# 8. Quy tắc Nguyên nhân & Nguyên nhân Gốc rễ

## BR-CAUSE-001 — Issue Is Not Cause

**Mức ưu tiên:** P0  
**Quy tắc:** Issue đại diện cho lỗi/triệu chứng quan sát được. Cause đại diện cho một giả thuyết điều tra.

Dữ liệu về Cause MUST NOT được mã hóa vào danh mục Issue.

---

## BR-CAUSE-002 — Candidate Cause Is 0:N

**Mức ưu tiên:** P0  
**Quy tắc:** Một quyết định/điều tra MAY chứa từ không đến nhiều Candidate Causes.

Mỗi nguyên nhân được gợi ý SHOULD giữ lại:
- ID nguyên nhân;
- thứ hạng (rank);
- độ tin cậy (confidence);
- nguồn (source);
- phiên bản mô hình/quy tắc khi có liên quan.

---

## BR-CAUSE-003 — UNKNOWN Cannot Coexist With Specific Candidate Causes

**Mức ưu tiên:** P0  
**Quy tắc:** Nếu xác định nguyên nhân là `UNKNOWN`, tập hợp quyết định đó MUST NOT chứa nguyên nhân ứng viên cụ thể nào.

---

## BR-CAUSE-004 — Canonical Cause Determination Status

**Mức ưu tiên:** P0  
**Quy tắc:** `cause_determination_status` MUST sử dụng chính xác:

```text
NOT_ASSESSED
UNKNOWN
SUGGESTED
UNDER_INVESTIGATION
CONFIRMED
NOT_APPLICABLE
```

- Phân loại/xem xét trong P0 MAY chỉ ghi `NOT_ASSESSED`, `UNKNOWN`, `SUGGESTED`, `NOT_APPLICABLE`.
- `SUGGESTED` yêu cầu ít nhất một Candidate Cause; `UNKNOWN` MUST NOT cùng tồn tại với một Candidate Cause cụ thể.
- `UNDER_INVESTIGATION` và `CONFIRMED` là các trạng thái P1 chỉ được ghi bởi luồng công việc Điều tra/RCA.
- Bộ phân loại (Classifier)/AI MUST NOT ghi `UNDER_INVESTIGATION` hoặc `CONFIRMED`.

---

## BR-CAUSE-005 — AI Cannot Confirm Root Cause

**Mức ưu tiên:** P0/P1  
**Quy tắc:** Không một mô hình AI, prompt, điểm bất thường (anomaly score) hay độ tin cậy của bộ phân loại nào có thể độc lập tạo ra một nguyên nhân gốc rễ đã xác nhận (confirmed root cause).

---

## BR-CAUSE-006 — Confirmed Root Cause Requires Evidence

**Mức ưu tiên:** P1  
**Quy tắc:** Một nguyên nhân gốc rễ đã xác nhận MUST có:
- `confirmed_by`;
- `confirmed_at`;
- bằng chứng (evidence);
- tham chiếu điều tra/RCA;
- người xác nhận có thẩm quyền.

---

## BR-CAUSE-007 — Asset and Work Order Are Investigation References

**Mức ưu tiên:** P1  
**Quy tắc:** Asset ID, đối tượng BMS, đơn công việc (work order) CMMS, và các mã định danh hệ thống kỹ thuật MAY được liên kết với điều tra nhưng MUST NOT trở thành các chiều phân loại Service/Issue cốt lõi.

---

## BR-CAUSE-008 — P0/P1 RCA Boundary

**Mức ưu tiên:** P0/P1  
**Quy tắc:** P0 giới hạn ở Hotspot, các Feedback Item làm bằng chứng, người phụ trách (owner), trạng thái hotspot và Candidate Cause cơ bản. P1 sở hữu Investigation, Confirmed Root Cause, Corrective Action (Hành động Khắc phục), Preventive Action (Hành động Phòng ngừa) và toàn bộ luồng công việc/lưu trữ/API/UI của RCA.

P0 MUST NOT mở ra mutation cho phép bắt đầu một Investigation, xác nhận Root Cause hoặc quản lý Corrective/Preventive Actions.

---

# 9. Quy tắc Nhập & Nạp Dữ liệu (Import & Ingestion Rules)

## BR-IMP-001 — Import Is Asynchronous

**Mức ưu tiên:** P0  
**Quy tắc:** Việc nhập CSV/XLSX MUST chạy dưới dạng một job bất đồng bộ.

Vòng đời chuẩn:

```text
UPLOADED
  → MAPPED
  → VALIDATING
  → VALIDATED
  → QUEUED
  → PROCESSING
      ├── COMPLETED
      ├── PARTIAL
      ├── FAILED
      └── CANCELLED
```

---

## BR-IMP-002 — Preview/Validation Does Not Commit Production Feedback

**Mức ưu tiên:** P0  
**Quy tắc:** Việc xem trước (preview) và xác thực (validation) MUST NOT tạo các bản ghi Feedback sản xuất (production).

---

## BR-IMP-003 — Execute Only From VALIDATED

**Mức ưu tiên:** P0  
**Quy tắc:** Việc thực thi nhập dữ liệu MUST bị từ chối trừ khi job đang ở trạng thái `VALIDATED`.

---

## BR-IMP-004 — File/Schema Failure Versus Row Failure

**Mức ưu tiên:** P0  
**Quy tắc:**
- lỗi chặn ở cấp file/schema → job chuyển thành `FAILED`;
- các lỗi xác thực ở cấp dòng MAY vẫn cho phép chuyển thành `VALIDATED` nếu được cấu hình để commit các dòng hợp lệ.

---

## BR-IMP-005 — Every Row Has Lineage and Outcome

**Mức ưu tiên:** P0  
**Quy tắc:** Mỗi dòng nguồn MUST giữ lại:
- `import_job_id`;
- `source_row_number`;
- danh tính checksum/tính lặp lại không đổi (idempotency identity);
- kết quả xử lý (processing outcome);
- mã/thông điệp lỗi khi không thành công.

Không một dòng nào được phép bị bỏ qua một cách âm thầm.

---

## BR-IMP-006 — Retry Is Idempotent

**Mức ưu tiên:** P0  
**Quy tắc:** Việc thử lại MUST chỉ xử lý các dòng chưa được commit thành công trước đó và MUST NOT tạo các bản ghi Feedback trùng lặp.

---

## BR-IMP-007 — Event Time Semantics

**Mức ưu tiên:** P0  
**Quy tắc:** `reported_at` bảo tồn thời gian/múi giờ nguồn khi có sẵn.

Nếu không có sẵn:
- sử dụng `ingested_at`;
- đặt `event_time_inferred=true`.

Các nhãn thời gian lưu trữ SHOULD là UTC. Việc gom nhóm (bucketing) hiển thị cho người dùng MUST tuân thủ chính sách múi giờ nguồn/địa điểm.

---

## BR-IMP-008 — Mask Before AI

**Mức ưu tiên:** P0  
**Quy tắc:** Khi nội dung thô chứa dữ liệu cá nhân được bảo vệ không cần thiết cho suy luận mô hình, `content_masked`/`item_text_masked` MUST được tạo ra trước khi xử lý AI.

---

# 10. Quy tắc Phân tích Dữ liệu (Analytics Rules)

## BR-ANA-001 — Feedback Item Is Default Metric Grain

**Mức ưu tiên:** P0  
**Quy tắc:** Trừ khi được dán nhãn rõ ràng khác, phân tích sản phẩm MUST đếm số lượng `feedback_item_id` hợp lệ duy nhất (distinct eligible).

---

## BR-ANA-002 — Analytics Requires Eligible Current Decision

**Mức ưu tiên:** P0  
**Quy tắc:** Một mục chỉ có thể đưa vào phân tích tiêu chuẩn khi:
- mục đang hoạt động (active);
- `analytic_eligibility=INCLUDED`;
- không trùng lặp/bị loại trừ;
- projection hiện tại đến từ quyết định được chấp nhận của con người/nguồn tin cậy (source-trusted);
- các giá trị taxonomy được tham chiếu hợp lệ đối với bản phát hành được ghi nhận.

Chỉ riêng dự đoán chưa qua xem xét là không đủ điều kiện.

---

## BR-ANA-003 — Unknown Is Not Silently Dropped

**Mức ưu tiên:** P0  
**Quy tắc:** Tỷ lệ unknown/missing MUST đo lường được một cách riêng biệt.

Đối với sắc thái (sentiment):
- mẫu số của `negative_rate` sử dụng các mục hợp lệ có sắc thái đã biết (known sentiment);
- sắc thái chưa biết MUST được hiển thị thông qua `sentiment_unknown_rate`.

---

## BR-ANA-004 — Metric Definition Is Versioned

**Mức ưu tiên:** P0  
**Quy tắc:** KPI, biểu đồ (chart), xem chi tiết (drill-down), và xuất dữ liệu (export) phải dùng chung:
- ngữ cảnh bộ lọc (filter context);
- logic tính hợp lệ (eligibility logic);
- ngữ nghĩa thời gian sự kiện;
- `metric_definition_version`.

---

## BR-ANA-005 — No Dead-End Chart

**Mức ưu tiên:** P0  
**Quy tắc:** Mỗi phân đoạn biểu đồ tiêu chuẩn trên dashboard MUST cho phép drill-down đến danh sách Feedback Item tương ứng đã được lọc, và từ đó xem chi tiết từng mục.

---

## BR-ANA-006 — Four Basic P0 Dashboards

**Mức ưu tiên:** P0  
**Quy tắc:** P0 MUST cung cấp bốn dashboard cơ bản: CX Overview, Customer Journey, Service & Pain Points, và Hotspot & Root Cause.

Dashboard thứ tư bị giới hạn trong P0 ở hotspot, evidence, owner/status và Candidate Cause. Investigation, confirmed Root Cause và các hành động (actions) vẫn thuộc phạm vi P1.

---

## BR-ANA-007 — Multi-metric Breakdown Contract

**Mức ưu tiên:** P0  
**Quy tắc:** Phân tích chi tiết (breakdown) theo `journey_stage`, `journey_step`, `service`, `issue`, `location`, `intake_channel` hoặc `affected_channel` MUST hỗ trợ:

```text
item_volume
negative_rate
active_hotspots
trend
```

Tất cả chỉ số và các thao tác drill-down MUST dùng chung ngữ cảnh bộ lọc, logic tính hợp lệ và phiên bản định nghĩa chỉ số.

---

## BR-ANA-008 — Persona Is Not a P0 Analytics Dimension

**Mức ưu tiên:** P0  
**Quy tắc:** P0 API/UI MUST NOT hiển thị bộ lọc hoặc phân đoạn Persona. Chân dung người dùng (product personas) là các vai trò ủy quyền/người dùng (authorization/user roles), không phải là dữ liệu phân tích khách hàng.

---

## BR-ANA-009 — Affected Channel Is Supported in P0 Analytics

**Mức ưu tiên:** P0  
**Quy tắc:** `affected_channel` MUST có sẵn dưới dạng bộ lọc và chiều phân tích chi tiết trong P0, phân biệt rõ ràng với `intake_channel`.

---

## BR-ANA-010 — Household Count Is Conditional

**Mức ưu tiên:** P0  
**Quy tắc:** Số lượng hộ gia đình duy nhất chỉ có thể được hiển thị khi một khóa hộ gia đình ẩn danh (pseudonymous household key) hợp lệ tồn tại và vượt qua cổng kiểm định chất lượng dữ liệu (data-quality gate).

Nếu không, hiển thị `N/A`; không tự suy luận số hộ gia đình từ số lượng feedback.

---

# 11. Quy tắc Điểm nóng (Hotspot Rules)

## BR-HOT-001 — Deterministic P0 Detection Key

**Mức ưu tiên:** P0  
**Quy tắc:** Việc phát hiện hotspot trong P0 MUST dựa trên:

```text
primary_service_id
+ issue_id
+ normalized location at configured level
+ rolling time window
+ rule_version
```

---

## BR-HOT-002 — Only Accepted Eligible Items Count

**Mức ưu tiên:** P0  
**Quy tắc:** Đầu vào hotspot MUST loại trừ:
- các dự đoán AI chưa qua xem xét;
- các mục trùng lặp;
- các mục bị loại trừ/không hợp lệ;
- các bản ghi thiếu chiều phát hiện bắt buộc.

---

## BR-HOT-003 — P0 Rule Is Threshold-Based

**Mức ưu tiên:** P0  
**Quy tắc:** Trong một cửa sổ thời gian trượt (rolling window) `W` được cấu hình, nếu có ít nhất `N` mục hợp lệ đã khử trùng lặp có chung khóa phát hiện được cấu hình, hệ thống MUST upsert một ứng viên hotspot.

Mặc định lát cắt dọc thử nghiệm (pilot vertical-slice):

```text
W = 2 hours
N = 3
Service = SV-07
Issue = IS-07-01
Location level = Building/Zone
```

Đây là mặc định cho thử nghiệm/kiểm thử, không phải ngưỡng áp dụng cho toàn hệ thống sản xuất.

---

## BR-HOT-004 — Hotspot Upsert Is Idempotent

**Mức ưu tiên:** P0  
**Quy tắc:** Cùng một tập hợp `dimension_key + rule_version + active window` MUST NOT tạo ra các ứng viên hoạt động trùng lặp khi job thực hiện thử lại (retry).

---

## BR-HOT-005 — Evidence Must Be Reproducible

**Mức ưu tiên:** P0  
**Quy tắc:** Mỗi ứng viên hotspot MUST lưu giữ tập hợp các Feedback Item bằng chứng được sử dụng để tạo/tính toán lại hotspot đó.

---

## BR-HOT-006 — Default Owner Comes From Service Configuration

**Mức ưu tiên:** P0  
**Quy tắc:** Người phụ trách (owner) của ứng viên mới SHOULD được xác định từ cấu hình quyền sở hữu vận hành Service được đánh phiên bản.

Nếu không có owner:
- ứng viên chuyển vào hàng đợi chưa gán (unassigned queue);
- điều kiện này được ghi nhận như một lỗi chất lượng dữ liệu/cấu hình vận hành.

`SV-10` không có owner mặc định ngầm định.

---

## BR-HOT-007 — Hotspot Lifecycle Is Controlled

**Mức ưu tiên:** P0  
**Quy tắc:** Vòng đời được phép:

```text
CANDIDATE → ACKNOWLEDGED → INVESTIGATING → RESOLVED
      └──────────────────────────────→ DISMISSED

RESOLVED/DISMISSED → REOPENED → INVESTIGATING
```

Các chuyển đổi không hợp lệ MUST bị từ chối.

`INVESTIGATING` ở đây chỉ là một trạng thái vận hành của Hotspot; trong P0 nó MUST NOT tạo ra một thực thể Investigation/RCA hoặc thay đổi trạng thái nguyên nhân thành `UNDER_INVESTIGATION`.

---

## BR-HOT-008 — State/Ownership Changes Are Audited

**Mức ưu tiên:** P0  
**Quy tắc:** Các thao tác Acknowledge, assign, reassign, dismiss, resolve, và reopen MUST ghi nhận tác nhân (actor), nhãn thời gian (timestamp), và lý do (reason).

---

## BR-HOT-009 — Safety Hard Trigger Is Independent of Sentiment/Classifier

**Mức ưu tiên:** P1 sau khi phê duyệt (sign-off)  
**Quy tắc:** Các kích hoạt cứng an toàn (safety hard triggers) đã được phê duyệt MUST NOT phụ thuộc vào sắc thái (sentiment) hoặc việc chờ hoàn thành xử lý khối lượng/bộ phân loại (volume/classifier completion).

P0 MUST duy trì việc thực thi hard-trigger tự động ở trạng thái tắt cờ tính năng (feature-flagged off) cho đến khi nhận được sự phê duyệt của Safety/Legal/BQL.

---

# 12. Quy tắc Mức độ Ưu tiên & Mức độ Nghiêm trọng

## BR-SEV-001 — Delivery Priority Is Not Operational Severity

**Mức ưu tiên:** P0  
**Quy tắc:** Đây là hai chiều tách biệt:

```text
delivery_priority = P0 | P1 | P2
operational_severity = SEV-1 | SEV-2 | SEV-3 | SEV-4
```

Chúng MUST NOT dùng chung:
- cùng một trường cơ sở dữ liệu;
- cùng một ý nghĩa API;
- cùng một bộ lọc UI;
- cùng một ngữ nghĩa hiển thị.

---

## BR-SEV-002 — Legacy Priority Mapping

**Mức ưu tiên:** Chuyển đổi P0 (P0 migration)  
**Quy tắc:** Priority vận hành cũ `P1..P4` ánh xạ thành:

```text
P1 → SEV-1
P2 → SEV-2
P3 → SEV-3
P4 → SEV-4
```

Quá trình chuyển đổi phải thể hiện rõ ràng sự chuyển đổi ngữ nghĩa này.

---

# 13. Quy tắc Bảo mật & Kiểm toán

## BR-SEC-001 — Server-Side Authorization

**Mức ưu tiên:** P0  
**Quy tắc:** Kiểm tra quyền hạn MUST được thực thi bởi tầng API/dịch vụ. Việc ẩn các nút điều khiển trên UI không phải là ủy quyền (authorization).

---

## BR-SEC-002 — Minimum Pilot Roles

**Mức ưu tiên:** P0  
**Quy tắc:** Bản thử nghiệm MUST hỗ trợ tối thiểu:

```text
PILOT_ADMIN
ANALYST
REVIEWER
VIEWER
```

Tất cả người dùng MUST bị giới hạn trong phạm vi dự án thử nghiệm đã được phê duyệt.

---

## BR-SEC-003 — Raw PII Is Privileged

**Mức ưu tiên:** P0  
**Quy tắc:** Việc xem/xuất `content_raw` hoặc các thông tin định danh khách hàng yêu cầu phải có một đặc quyền rõ ràng.

Người dùng không có đặc quyền phải nhận nội dung đã được che mờ (masked content).

---

## BR-SEC-004 — Privileged Actions Are Audited

**Mức ưu tiên:** P0  
**Quy tắc:** Kiểm toán (Audit) MUST bao quát tối thiểu:
- các hành động đăng nhập/quản trị (login/admin);
- thực thi nhập dữ liệu (import);
- xem/xuất dữ liệu PII thô;
- xuất bản taxonomy;
- tách Feedback Item;
- quyết định phân loại;
- thay đổi người phụ trách/trạng thái hotspot;
- thay đổi quy tắc hotspot.

---

## BR-SEC-005 — Audit Records Are Append-Only

**Mức ưu tiên:** P0  
**Quy tắc:** Các sự kiện kiểm toán MUST NOT bị ghi đè bởi luồng công việc ứng dụng thông thường.

---

# 14. Quy tắc Độ tin cậy & Chất lượng Dữ liệu

## BR-DQ-001 — No Silent Fallback

**Mức ưu tiên:** P0  
**Quy tắc:** Trường hợp thiếu taxonomy, địa điểm, thời gian sự kiện, người phụ trách, hoặc ánh xạ không hợp lệ MUST tạo ra:
- một trạng thái giá trị (value status) rõ ràng, hoặc
- một lỗi chất lượng dữ liệu có thể quan sát được.

Nền tảng MUST NOT tự động đoán giá trị thay thế một cách âm thầm.

---

## BR-DQ-002 — Projection Must Be Rebuildable

**Mức ưu tiên:** P0  
**Quy tắc:** Projection phân loại hiện tại MUST có thể tái tạo lại được từ các quyết định/sự kiện xem xét bất biến.

---

## BR-DQ-003 — Async Work Must Be Retryable and Observable

**Mức ưu tiên:** P0  
**Quy tắc:** Các job nhập dữ liệu, dự đoán AI, và đánh giá hotspot MUST hiển thị rõ:
- trạng thái job;
- hành vi thử lại (retry);
- mã tương quan (correlation ID);
- chi tiết lỗi;
- cơ chế bảo vệ tính lặp lại không đổi (idempotency protection).

---

## BR-DQ-004 — Versioned Configuration Must Be Reproducible

**Mức ưu tiên:** P0  
**Quy tắc:** Hành vi lịch sử MUST có thể tái tạo lại từ các phiên bản taxonomy/mapping/metric/rule được lưu trữ.

---

# 15. Ma trận Quy tắc và Phương thức Thực thi

| Nhóm quy tắc | DB constraint | API/service validation | Async worker | UI validation | Audit | Automated test |
|---|---:|---:|---:|---:|---:|---:|
| Tính bất biến của Feedback | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| Mục nguyên tử/Tách mục |  | ✓ |  | ✓ | ✓ | ✓ |
| Phân tách vòng đời | ✓ | ✓ |  | ✓ |  | ✓ |
| Tính nhất quán Issue↔Service | ✓/logical | ✓ |  | ✓ | ✓ | ✓ |
| Quyết định chỉ ghi thêm (append-only) | ✓ | ✓ |  | ✓ | ✓ | ✓ |
| Dự đoán chỉ gợi ý (suggest-only) | ✓/logical | ✓ | ✓ | ✓ | ✓ | ✓ |
| Tính lặp lại không đổi của Import | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Điều kiện hợp lệ của phân tích |  | ✓ | ✓/query | ✓ |  | ✓ |
| Tính lặp lại không đổi của Hotspot | ✓ | ✓ | ✓ |  | ✓ | ✓ |
| Đặc quyền PII |  | ✓ |  | ✓ | ✓ | ✓ |
| Các bất biến xuất bản Taxonomy | ✓/validator | ✓ | ✓ | ✓ | ✓ | ✓ |

---

# 16. Các Bất biến Nghiệm thu Tối thiểu cho P0

Trước khi P0 được coi là hợp lệ về mặt kỹ thuật, các bài kiểm thử tự động MUST chứng minh được tối thiểu các điều sau:

1. Việc thử lại cùng một vụ nhập dữ liệu (import) không làm trùng lặp các feedback đã thành công.
2. Một feedback có nhiều ý định có thể được tách ra mà không làm thay đổi `content_raw`.
3. `SRV-*` không thể được lưu trữ dưới dạng một bước (step) Vòng đời Khách hàng.
4. Một Issue đã biết không thể được lưu dưới một Primary Service sai.
5. Một dự đoán không thể đi vào projection hiện tại mà không có quyết định được chấp nhận.
6. Một đính chính thủ công tạo ra một phiên bản quyết định mới thay vì ghi đè lên lịch sử.
7. Projection hiện tại có thể được tái tạo lại từ lịch sử quyết định.
8. `SV-10/IS-10-01` không có `other_reason` sẽ bị từ chối.
9. Một taxonomy ID đã biết thuộc bản phát hành đã ngưng sử dụng/chưa xuất bản không thể được sử dụng cho một quyết định mới.
10. Dữ liệu phân tích loại trừ các dự đoán chưa qua xem xét và các mục không hợp lệ.
11. Lát cắt dọc (vertical slice) được cấu hình tạo ra chính xác một ứng viên hotspot khi đạt ngưỡng.
12. Việc thử lại đánh giá hotspot không làm trùng lặp ứng viên đó.
13. Tập hợp bằng chứng hotspot có thể truy xuất ngược lại chính xác các Feedback Item tương ứng.
14. PII thô bị từ chối truy cập đối với vai trò không có đặc quyền xem dữ liệu thô (raw-view privilege).
15. Mọi mutation thay đổi đặc quyền/quyết định/trạng thái hotspot đều tạo ra một bản ghi kiểm toán (audit record).

---

# 17. Các Quyết định Nghiệp vụ Mở Chặn hoặc Định hình P0

Những điều sau đây phải duy trì dưới dạng các bản ghi cấu hình/quyết định rõ ràng thay vì các giả định được hard-code:

- dự án thử nghiệm/tòa nhà/nguồn/khoảng thời gian/nhóm người dùng (user cohort);
- chính sách tin cậy nguồn (source-trust policy);
- hướng dẫn tách nhiều ý định (multi-intent split guideline);
- các trường UNKNOWN bắt buộc so với tùy chọn;
- phân cấp địa điểm và cấp độ gom nhóm;
- cấu hình người phụ trách (owner) của Service;
- sự phê duyệt cuối cùng cho ánh xạ mức độ nghiêm trọng cũ (legacy severity mapping);
- chính sách che mờ/lưu giữ/xuất dữ liệu PII;
- các tham số hotspot `N`, `W`, thời gian chờ (cooldown), owner và playbook;
- quy mô thử nghiệm và giới hạn dung lượng file;
- quy tắc lấy mẫu bộ dữ liệu chuẩn (gold-set sampling) và phân xử (adjudication rules);
- cơ sở chỉ số vận hành (operational metric baseline).

---

# 18. Nguồn Sự thật (Source of Truth)

Tài liệu này được dẫn xuất từ:

1. `docs/PRD.md` — yêu cầu sản phẩm, mô hình tên miền (domain model), yêu cầu chức năng, quy tắc nghiệp vụ, phác thảo API baseline, các NFR, và nghiệm thu MVP.
2. `docs/service_taxonomy.md` — định nghĩa chuẩn về vòng đời/service/issue và các bất biến khi xuất bản taxonomy.

Bất kỳ quy tắc mới nào làm thay đổi ý nghĩa taxonomy chuẩn đều phải được phản ánh trước trong `service_taxonomy.md`.  
Bất kỳ quy tắc mới nào làm thay đổi phạm vi/hành vi sản phẩm đều phải được phản ánh trước trong `PRD.md` hoặc một Decision Record được liên kết.


---

## Phụ lục — Quy tắc mới triển khai (v1.2)

### BR-TP-001 — Touchpoint là chiều phân loại tùy chọn

**Mức ưu tiên:** P0 (implemented migration 019)  
**Quy tắc:** Mỗi `feedback_item` MAY có 0 hoặc 1 `touchpoint_id`. Touchpoint phải thuộc cùng lifecycle_step với `customer_lifecycle_step_id` của item trong cùng taxonomy release.  
**Thực thi:** `classification_current.touchpoint_value_status` ∈ {KNOWN, UNKNOWN, MISSING, NOT_APPLICABLE}.

### BR-TP-002 — Touchpoint-Service mapping

**Quy tắc:** Mỗi touchpoint có 1 `primary_service` và 0..N `secondary_service` theo bảng `touchpoint_service_map`. Mapping type: PRIMARY | SECONDARY.

### BR-HS-005 — Hotspot Action Priority

**Quy tắc** (implemented `packages/domain/hotspot/engine.py::calculate_action_priority`):
- `IMMEDIATE`: max_severity=SEV-1 AND issue.safety_critical=true AND safety_playbook_approved=true
- `URGENT`: max_severity ∈ {SEV-1, SEV-2} OR evidence_count ≥ 10
- `PLANNED`: max_severity ∈ {SEV-3, SEV-4} AND evidence_count ≥ 2
- `MONITOR`: còn lại

### BR-HS-006 — Hotspot REOPENED Status

**Quy tắc:** Hotspot ở trạng thái RESOLVED hoặc DISMISSED MAY được REOPEN qua `POST /hotspots/{id}/reopen`. Khi reopen, status chuyển về INVESTIGATING (không phải CANDIDATE). Audit log ghi nhận `from_status` và `to_status`.

### BR-HS-007 — Hotspot ASSIGN

**Quy tắc:** `POST /hotspots/{id}/assign` chuyển trạng thái sang INVESTIGATING, đồng thời ghi nhận `assigned_user_id` và `assigned_team_key`. Bắt buộc có `expected_version` cho optimistic locking.

### BR-IMP-003 — Direct CSV Import

**Quy tắc:** `POST /api/v1/feedback-items/direct-import-csv` là mode import đồng bộ không qua worker. Toàn bộ raw CSV fields được lưu vào `feedback.source_metadata_json` (JSONB). Không overwrite dữ liệu hiện có (insert only).

### BR-CHANNEL-001 — Channel Code Format

**Quy tắc:** Channel codes trong DB và API dùng chữ thường với prefix `ch-`. Ví dụ: `ch-app`, `ch-hotline`, `ch-frontdesk`. Filter param tên `intake_channel_code` và `affected_channel_code`.
