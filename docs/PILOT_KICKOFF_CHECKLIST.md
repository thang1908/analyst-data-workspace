# Pilot Kickoff Checklist — Trusted CSV to Dashboard

- **Status:** Blocking checklist
- **Applies to:** FEAT-00, FEAT-01, FEAT-02, FEAT-03, FEAT-04, FEAT-05
- **Rule:** Không đổi feature sang `Ready for build` khi còn ô bắt buộc là `TBD` hoặc chưa có evidence/link.

## 1. Named ownership

Điền tên/người liên hệ trước kickoff:

| Responsibility | Named owner | Backup | Due | Status |
| --- | --- | --- | --- | --- |
| Product/Data acceptance | `TBD` | `TBD` | Trước Day 1 | Open |
| Integration Lead / FEAT-00 | `TBD` | `TBD` | Trước Day 1 | Open |
| FEAT-01 Platform & Data Foundation | `TBD` | `TBD` | Trước Day 1 | Open |
| FEAT-02 CSV Import | `TBD` | `TBD` | Trước Day 1 | Open |
| FEAT-03 Analytics API | `TBD` | `TBD` | Trước Day 1 | Open |
| FEAT-04 Pilot Web UI | `TBD` | `TBD` | Trước Day 1 | Open |
| FEAT-05 Release/QA | `TBD` | `TBD` | Trước Day 1 | Open |
| Security/Auth approver | `TBD` | `TBD` | Trước staging data | Open |
| Staging/Infrastructure owner | `TBD` | `TBD` | Trước Day 1 | Open |

Một người có thể giữ nhiều vai trò khi team nhỏ, nhưng mỗi responsibility phải có đúng một accountable owner và thời gian phản hồi trong ngày.

## 2. Data and reference decisions

- [ ] Representative CSV đã mask được phép dùng; ghi path/checksum: `TBD`.
- [ ] Expected row/outcome counts được Data Owner ký: `TBD`.
- [ ] Contract giữ nguyên `trusted-feedback-csv/v1`, UTF-8, comma-delimited, tối đa 10 MiB/10.000 rows.
- [ ] `source_reference` là operational non-PII key và unique cùng `PILOT_CSV_V1`.
- [ ] Project code được duyệt: `PILOT_PROJECT` hoặc giá trị thay thế `TBD`.
- [ ] Location codes/hierarchy được duyệt: `S2` hoặc giá trị thay thế `TBD`.
- [ ] Taxonomy subset và checksum được duyệt: `SVC-17`, `SVC-18`, `ELV-01`, `ELV-02`, `ELV-06`, `PKG-01` hoặc change set `TBD`.
- [ ] Source-trust policy approver, effective period và checksum: `TBD`.
- [ ] Invalid/duplicate/partial policy giữ đúng FEAT-02 hoặc exception đã duyệt: `TBD`.

Fixture synthetic chuẩn nằm tại [`packages/test-fixtures/import`](../packages/test-fixtures/import). Dữ liệu thật không được dùng để thay fixture trong repository.

## 3. Metric decisions

- [ ] `metric_definition_version=feedback-dashboard-v1` được Product/Data Owner duyệt.
- [ ] Event time là `reported_at`, timezone pilot là `Asia/Ho_Chi_Minh` hoặc exception `TBD`.
- [ ] `item_volume`, `negative_rate`, `sentiment_unknown_rate` và severity semantics đúng FEAT-03.
- [ ] Data-quality dùng `import_job.completed_at` và chỉ gồm `COMPLETED|PARTIAL`.
- [ ] Filter, snapshot token và drill-down acceptance examples đã được ký: evidence `TBD`.
- [ ] Pilot performance shape 10k import/100k analytics và budget được Tech Lead chấp nhận: `TBD`.

## 4. Security and environment

- [ ] Staging PostgreSQL 16 endpoint/database owner sẵn sàng: `TBD`.
- [ ] Private source-file storage, retention và cleanup policy sẵn sàng: `TBD`.
- [ ] Authentication issuer/client và test identities sẵn sàng: `TBD`.
- [ ] Pilot authorization là project-only; fine-grained building/service scope không bị ngầm thêm vào tuần đầu.
- [ ] Secret store/CI environment được cấp; không dùng `.env` chia sẻ qua chat/email/repository.
- [ ] Staging chỉ nhận synthetic/masked data; quyền xem raw/export không tồn tại trong pilot UI.
- [ ] Hosting/deploy owner, staging URL/domain và access policy: `TBD`.

## 5. Repository and delivery readiness

- [x] `origin/dev` và năm feature branches tồn tại từ cùng coordination baseline; đã được tạo trong repository bootstrap của tài liệu này.
- [ ] Mỗi thành viên checkout đúng branch và xác nhận upstream/base `dev`.
- [ ] FEAT-01 merge đầu tiên trong Day 1; downstream rebase sau merge.
- [ ] Root scripts/lockfile/toolchain được FEAT-01 pin; CI dùng frozen lockfile.
- [ ] Required reviewers/path owners trong Team Build Playbook đã được gán người cụ thể.
- [ ] PR target là `dev`; không push trực tiếp `dev/main` trong implementation.
- [ ] Staging/release approval và rollback decision owner được ghi tên: `TBD`.

## 6. Go / no-go

Integration Lead chỉ chuyển feature sang `Ready for build` khi:

1. Named owner của feature và dependency đã có.
2. Mọi DoR riêng của feature đã pass hoặc exception có owner/expiry.
3. Contract/schema/fixture mà feature dùng đã freeze.
4. Branch đã rebase trên baseline dependency mới nhất.
5. Evidence/link được cập nhật trong checklist hoặc feature PR.

Nếu Data/Metric/Security sections chưa đóng trước Day 1, outcome tuần đó tự động giảm thành synthetic demo; không được dùng dữ liệu thật hoặc gọi là production pilot.

## 7. Sign-off record

| Gate | Approver | Date/SHA | Result | Evidence |
| --- | --- | --- | --- | --- |
| Contract/Data | `TBD` | `TBD` | Open | `TBD` |
| Architecture/Schema | `TBD` | `TBD` | Open | `TBD` |
| Security/Auth | `TBD` | `TBD` | Open | `TBD` |
| Staging readiness | `TBD` | `TBD` | Open | `TBD` |
| Release acceptance | `TBD` | `TBD` | Open | `TBD` |
