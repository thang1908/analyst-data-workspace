# Trusted CSV import fixtures

Các fixture này tuân theo `trusted-feedback-csv/v1` trong FEAT-000 và chỉ chứa dữ liệu synthetic/masked.

## Expected outcomes

| File | Total | Valid | Invalid | Duplicate |
| --- | ---: | ---: | ---: | ---: |
| `trusted-feedback.valid.csv` | 5 | 5 | 0 | 0 |
| `trusted-feedback.mixed.csv` | 5 | 1 | 3 | 1 |

Với file mixed, dòng đầu tiên của một `source_reference` lặp được coi là candidate hợp lệ và mọi occurrence sau là `DUPLICATE`. Nếu source key đã tồn tại trong database, tất cả occurrence tương ứng phải là `DUPLICATE` và expected assertion của test phải nêu rõ precondition đó.

Không thay fixture để làm test pass nếu contract chưa thay đổi. Mọi thay đổi header hoặc semantics phải cập nhật FEAT-000, contract version và expected assertions trong cùng change set.

## Deterministic generated fixtures

Chạy bằng Node.js 24:

```bash
node packages/test-fixtures/import/generate.mjs
```

Output mặc định nằm trong `generated/` và bị Git ignore. Có thể dùng thư mục tạm:

```bash
node packages/test-fixtures/import/generate.mjs --out /tmp/cx-pilot-fixtures
```

Generator tạo `happy-100.csv`, `mixed-80-10-10.csv`, `duplicate-existing.csv`, `boundary-10000.csv`, performance seed `analytics-100000.ndjson` và `manifest.generated.json` chứa SHA-256/bytes/expected counts. `duplicate-existing.csv` chỉ có expected duplicate bằng 5 sau khi `happy-100.csv` đã import thành công.

Source expectations và checksum của fixture nhỏ được khóa trong [`manifest.json`](./manifest.json). CI phải so sánh generated manifest thay vì commit các file lớn.
