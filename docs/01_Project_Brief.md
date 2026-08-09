# 01. Tóm tắt dự án

# Nền tảng dữ liệu và giao dịch bất động sản Việt Nam

**Tên dự án tạm thời: Chưa xác định**

---

# 1. Thông tin tài liệu

## 1.1 Thông tin chung

| Hạng mục         | Nội dung                                                      |
| ------------------ | -------------------------------------------------------------- |
| Tên tài liệu    | `01_Project_Brief.md`                                        |
| Tên dự án       | Nền tảng dữ liệu và giao dịch bất động sản Việt Nam |
| Tên thương mại | Chưa xác định                                              |
| Phiên bản        | v0.9 — Bản nháp để rà soát                              |
| Trạng thái       | Bản nháp — Chờ nhà sáng lập rà soát                   |

## 1.2 Nhóm tham gia dự kiến

Nhóm tham gia gồm: nhà sáng lập/đồng sáng lập, chủ sản phẩm, chuyên viên phân tích nghiệp vụ, nhà thiết kế sản phẩm, trưởng nhóm kỹ thuật, kỹ sư backend, kỹ sư frontend, kỹ sư dữ liệu/ML, kỹ sư QA, phụ trách phát triển kinh doanh và đối tác nguồn hàng, phụ trách tăng trưởng/tiếp thị, cố vấn pháp lý và tuân thủ.

## 1.3 Điều kiện phê duyệt

Tài liệu được chuyển sang trạng thái **Đã phê duyệt** khi nhà sáng lập thống nhất tầm nhìn sản phẩm, thị trường mục tiêu đầu tiên, chiến lược nguồn hàng, phạm vi MVP, ngân sách sơ bộ và Chỉ số Sao Bắc Đẩu; đồng thời hoàn thành ít nhất một vòng nghiên cứu người dùng và nguồn cung.

---

# 2. Tóm tắt điều hành

## 2.1 Tổng quan dự án

Dự án xây dựng một nền tảng công nghệ bất động sản phục vụ nhu cầu mua, bán, thuê và cho thuê nhà tại Việt Nam. Sản phẩm tham khảo các mô hình PropTech quốc tế như Zillow, Rightmove, PropertyGuru và 99.co, đồng thời nghiên cứu các nền tảng trong nước như Batdongsan.com.vn, Nhà Tốt, OneHousing và Vinhomes Market.

Mục tiêu không phải là xây thêm một website đăng tin bất động sản. Thị trường Việt Nam đã có các sàn đăng tin quy mô lớn; Batdongsan.com.vn công bố khả năng giúp người đăng tiếp cận hơn 7 triệu người dùng mỗi tháng và đã phát triển bản đồ, lịch sử giá cùng Tin xác thực. Cơ hội của dự án nằm ở lớp giá trị cao hơn: **nguồn hàng đáng tin cậy + dữ liệu chuyên sâu về bất động sản + khám phá thông minh**.

Nền tảng tập trung giải quyết ba vấn đề: nguồn hàng phân mảnh và thiếu tin cậy; một bất động sản xuất hiện dưới nhiều tin đăng; người dùng có nhiều thông tin nhưng thiếu công cụ hỗ trợ quyết định. Vì vậy, định vị đề xuất là **sàn giao dịch bất động sản dựa trên dữ liệu đã xác thực**, thay vì **sàn đăng tin bất động sản truyền thống**.

## 2.2 Ý tưởng sản phẩm

Sản phẩm xây dựng một **Đồ thị bất động sản (Property Graph)**, trong đó bất động sản là thực thể trung tâm:

```text
DỰ ÁN → TÒA NHÀ → BẤT ĐỘNG SẢN/CĂN → TIN ĐĂNG/CHÀO BÁN → CHỦ NHÀ/MÔI GIỚI
```

Một bất động sản có thể được chào bán bởi chủ nhà, nhiều môi giới hoặc từng xuất hiện trong các tin cũ. Thay vì hiển thị bốn tin như bốn bất động sản khác nhau, hệ thống dùng cơ chế phân giải thực thể để nhóm **4 tin đăng → 1 bất động sản → 3 chào bán đang hoạt động**.

Hành trình chính của người dùng là: **tìm kiếm → khám phá trên bản đồ → xem hồ sơ 360° → kiểm tra xác thực → xem giá và dữ liệu thị trường → so sánh → lưu → liên hệ → đặt lịch xem nhà**. Trong các giai đoạn sau, hành trình có thể mở rộng từ tìm kiếm sang dữ liệu chuyên sâu, trợ lý AI, tham quan, tài chính và giao dịch.

## 2.3 Giá trị chính

### Người mua/người thuê

Thông điệp giá trị: **Tìm đúng bất động sản, không phải xem thêm tin đăng.** Người dùng nhận được ít tin trùng và tin hết hiệu lực hơn; biết mức độ xác thực; xem giá, giá/m², lịch sử giá khi đủ dữ liệu, bản đồ và thông tin dự án; so sánh bất động sản tương tự; lưu nhu cầu; tìm kiếm bằng ngôn ngữ tự nhiên; nhận gợi ý phù hợp hơn.

### Người bán/môi giới

Nền tảng cung cấp kênh tiếp cận khách hàng, quản lý và xác thực tin đăng, quản lý khách hàng tiềm năng, hồ sơ môi giới, số liệu hiệu quả, quản lý nguồn hàng và phân phối tin đăng tốt hơn.

### Doanh nghiệp

Dự án tạo nền tảng để phát triển doanh thu từ sàn giao dịch, phần mềm dịch vụ cho môi giới, khách hàng tiềm năng chất lượng, giới thiệu dịch vụ tài chính, sản phẩm dữ liệu bất động sản và dữ liệu phân tích thị trường.

---

# 3. Bối cảnh

## 3.1 Bối cảnh thị trường

Người dùng Việt Nam đang tìm bất động sản qua nhiều kênh: cổng thông tin bất động sản, Facebook, Zalo, TikTok, Google, website môi giới, website chủ đầu tư, nhóm cư dân và mạng lưới môi giới ngoại tuyến. Họ phải tự tìm tin, loại tin trùng, hỏi tình trạng còn hàng, kiểm tra giá, tra cứu dự án và vị trí, kiểm tra pháp lý, so sánh rồi mới ra quyết định.

Các nền tảng lớn đã bắt đầu đầu tư vào độ tin cậy và dữ liệu thị trường. Ví dụ, Tin xác thực của Batdongsan.com.vn yêu cầu người đăng cung cấp tài liệu pháp lý phù hợp, thông tin/hình ảnh thực tế và dữ liệu vị trí, thời gian để xác minh. Việc nền tảng hiển thị lịch sử và biến động giá cũng cho thấy thị trường đang chuyển từ **chỉ có tin đăng** sang **tin đăng + dữ liệu + hỗ trợ quyết định**. Chất lượng dữ liệu và độ tin cậy đang trở thành một phần trực tiếp của sản phẩm, không còn chỉ là nghiệp vụ hậu trường.

## 3.2 Bối cảnh cạnh tranh

### A. Thị trường Việt Nam

| Nền tảng        | Mô hình chính                      | Điểm mạnh                                                                                   | Khoảng trống/cơ hội quan sát                                                                                                               |
| ----------------- | ------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Batdongsan.com.vn | Cổng thông tin/sàn đăng tin      | Lượng truy cập, nguồn hàng, SEO, dữ liệu dự án, bản đồ, lịch sử giá, xác thực | Vẫn lấy tin đăng làm trung tâm; còn cơ hội nâng cao nhận diện bất động sản, hỗ trợ quyết định và hành trình đầu cuối |
| Nhà Tốt         | Sàn đăng tin phân loại           | Nguồn tin rộng, trải nghiệm đơn giản, giá tham khảo                                   | Bất động sản chỉ là một ngành hàng trong hệ sinh thái rao vặt rộng hơn                                                            |
| OneHousing        | Dữ liệu, định giá và giao dịch | Định giá, dữ liệu lớn, phân tích thị trường                                         | Phạm vi nguồn hàng và tình huống sử dụng khác cổng thông tin đại trà                                                              |
| Vinhomes Market   | Sàn thuộc chủ đầu tư            | Nguồn hàng trực tiếp, quy trình giao dịch                                                | Nguồn hàng tập trung trong hệ sinh thái Vinhomes                                                                                           |
| Rever             | Môi giới ứng dụng công nghệ     | Kết hợp môi giới và trải nghiệm số                                                     | Vận hành nặng hơn mô hình nền tảng                                                                                                      |

Batdongsan.com.vn đã triển khai xác thực và dữ liệu giá lịch sử; Nhà Tốt duy trì nguồn tin mua bán lớn tại nhiều địa bàn. OneHousing công bố sử dụng dữ liệu lớn và AI cho công cụ định giá, từng dựa trên hơn một triệu dữ liệu bất động sản được xác minh trong hệ sinh thái. Vinhomes Market đại diện cho mô hình nguồn hàng trực tiếp từ chủ đầu tư, hỗ trợ tìm kiếm và nhiều bước giao dịch trực tuyến.

### B. Đối chuẩn quốc tế

**Zillow** đại diện cho mô hình kết hợp sàn giao dịch, cơ sở dữ liệu bất động sản, định giá, AI, hệ sinh thái môi giới, thế chấp, dịch vụ cho thuê và công cụ giao dịch. Theo số liệu công bố đến quý II/2026, Zillow Group có khoảng 173 triệu căn nhà trong Living Database, 239 triệu người dùng riêng trung bình mỗi tháng, 2,5 tỷ lượt truy cập trong quý và 772 triệu USD doanh thu quý. Zestimate được cung cấp cho hơn 110 triệu căn nhà, sử dụng mô hình thống kê/máy học kết hợp hồ sơ công, MLS và nhiều tín hiệu bất động sản. Zillow AI Mode, công bố tháng 3/2026, cho phép tìm kiếm bằng hội thoại, so sánh, hỏi khả năng chi trả, hiểu việc giảm giá, xem đánh đổi, đặt lịch tham quan và kết nối môi giới.

**Rightmove** đại diện cho mô hình cổng thông tin bất động sản: thu hút lượng lớn người dùng tìm kiếm, tạo độ phủ cho môi giới/chủ đầu tư và thu doanh thu thành viên chuyên nghiệp. Nền tảng cung cấp tìm kiếm, lịch sử giá bán, định giá trực tuyến, công cụ tính khả năng chi trả/thế chấp và khám phá môi giới.

**PropertyGuru** là đối chuẩn quan trọng tại Đông Nam Á. Năm 2026, doanh nghiệp công bố phục vụ hơn 30 triệu người tìm bất động sản mỗi tháng và có gần 2 triệu tin đăng. Mô hình kết hợp sàn giao dịch, hệ sinh thái môi giới, giải pháp cho chủ đầu tư, dữ liệu và phân tích thị trường.

**99 Group** vận hành 99.co, SRX và Rumah123 tại Singapore và Indonesia, tập trung vào quảng cáo bất động sản số, vị trí hiển thị cao cấp và tin xác thực cho môi giới.

### C. Các nhóm mô hình cạnh tranh

| Nhóm mô hình                    | Ví dụ                                 | Tài sản cốt lõi                      |
| ---------------------------------- | --------------------------------------- | ---------------------------------------- |
| Sàn đăng tin/cổng thông tin   | Batdongsan.com.vn, Nhà Tốt, Rightmove | Lượng truy cập + nguồn hàng         |
| Dữ liệu chuyên sâu             | Zillow, OneHousing                      | Dữ liệu + định giá                  |
| PropTech khu vực                  | PropertyGuru, 99.co                     | Mạng lưới + hệ sinh thái môi giới |
| Nguồn hàng kiểm soát           | Vinhomes Market                         | Nguồn cung trực tiếp                  |
| Môi giới công nghệ             | Rever                                   | Năng lực vận hành giao dịch         |
| Mua bán nhà trực tiếp (iBuyer) | Opendoor                                | Vốn + định giá                       |

Dự án đề xuất mô hình lai: **sàn giao dịch + nguồn hàng xác thực + Đồ thị bất động sản + dữ liệu giá + khám phá có AI hỗ trợ**.

## 3.3 Bối cảnh doanh nghiệp

Dự án là một sáng kiến khởi nghiệp mới hoàn toàn. Các yếu tố chưa chốt gồm pháp nhân, thương hiệu, quyền sở hữu của nhà sáng lập, cấu trúc vốn, nhà đầu tư, đối tác nguồn hàng chiến lược và mô hình doanh thu cuối cùng. Vì vậy, cách tiếp cận là **kiểm chứng → xây dựng → đo lường → quyết định**, thay vì huy động vốn lớn, xây toàn bộ hệ sinh thái rồi mới tìm người dùng.

## 3.4 Lý do thực hiện

1. **Chất lượng thông tin:** Người dùng không thiếu tin đăng mà thiếu tin đủ đáng tin để ra quyết định.
2. **Nhận diện bất động sản:** Một căn có thể xuất hiện trong nhiều tin khác nhau; phân biệt được **tin đăng ≠ bất động sản** sẽ tạo trải nghiệm tốt hơn cổng thông tin truyền thống.
3. **Hỗ trợ quyết định:** Người dùng cần tìm kiếm, bối cảnh giá, so sánh và độ tin cậy, không chỉ cần số điện thoại.
4. **Vòng lặp dữ liệu:** Nguồn hàng, hành vi, giá và tín hiệu giao dịch có thể dần tạo ra dữ liệu chuyên sâu, gợi ý, định giá và phân tích thị trường.

---

# 4. Tuyên bố vấn đề

## 4.1 Vấn đề của người dùng

### P01 — Tin đăng trùng lặp

Một bất động sản có thể được đăng bởi nhiều môi giới hoặc tài khoản, khiến người dùng tưởng nguồn hàng nhiều hơn thực tế, khó so sánh, phải gọi nhiều người và gặp các mức giá không nhất quán.

### P02 — Nguồn hàng hết hiệu lực

Tin vẫn tồn tại dù bất động sản đã bán/cho thuê, giá đã đổi hoặc người đăng không còn quyền phân phối.

### P03 — Độ tin cậy của thông tin

Người dùng khó biết người đăng là chính chủ hay môi giới, ảnh có đúng căn, bất động sản còn giao dịch, giá có thực và hồ sơ pháp lý có đầy đủ hay không. Việc thị trường đã phát triển Tin xác thực cho thấy xác minh và độ tin cậy là nhu cầu thật.

### P04 — Dữ liệu phân mảnh

Thông tin nằm rải rác trên cổng đăng tin, Google, website chủ đầu tư, Facebook, bản đồ, công cụ tính khoản vay, môi giới và nhóm cư dân; người dùng phải tự tổng hợp.

### P05 — Hỗ trợ quyết định còn yếu

Tìm kiếm truyền thống chủ yếu dựa trên vị trí, giá, diện tích, số phòng ngủ và loại hình. Trong khi đó, nhu cầu thực có thể là: “Gia đình bốn người, ngân sách 4 tỷ đồng, làm việc tại Cầu Giấy, cần trường mầm non gần nhà và thời gian đi làm dưới 30 phút.”

### P06 — Thiếu so sánh minh bạch

Người dùng khó xác định căn nào tốt hơn, mức giá có cao không, dự án nào phù hợp, bất động sản tương tự có giá bao nhiêu và chênh lệch có hợp lý không.

## 4.2 Vấn đề của phía cung và doanh nghiệp

- **B01:** Chi phí quảng cáo/đăng tin tăng nhưng chất lượng khách hàng tiềm năng không bảo đảm.
- **B02:** Khách hàng tiềm năng thiếu ý định rõ ràng.
- **B03:** Nguồn hàng bị phân mảnh giữa Excel, CRM, Zalo, Facebook, nhóm môi giới nội bộ và tài khoản trên các cổng đăng tin.
- **B04:** Môi giới khó xây dựng uy tín số độc lập.
- **B05:** Sàn mất khả năng quan sát sau khi người dùng và môi giới trao đổi bên ngoài nền tảng.

## 4.3 Hạn chế của giải pháp hiện tại

Các cổng thông tin hiện giải quyết tốt việc phân phối tin, tìm kiếm và tạo khách hàng tiềm năng, nhưng còn cơ hội cải thiện mạnh ở phân giải thực thể bất động sản, độ mới của nguồn hàng, dữ liệu hỗ trợ quyết định, cá nhân hóa, tìm kiếm có AI hỗ trợ và so sánh giữa các tin cùng một căn. Dự án không giả định đối thủ chưa có các năng lực này; giả thuyết cần kiểm chứng là các năng lực hiện tại chưa phục vụ đủ tốt một số phân khúc người dùng cụ thể.

## 4.4 Hậu quả nếu không giải quyết

Người dùng sẽ mất thời gian, giảm niềm tin, quá tải thông tin, ra quyết định trên dữ liệu thiếu, phụ thuộc nhiều vào môi giới và có thể bỏ dở hành trình tìm nhà. Với một sàn mới, nếu chỉ có cùng loại tin nhưng ít nguồn hàng và lượt truy cập hơn, người dùng sẽ không có lý do chuyển đổi và dự án sẽ thất bại trước hiệu ứng mạng lưới của các nền tảng hiện hữu.

---

# 5. Tầm nhìn sản phẩm

## 5.1 Tuyên bố tầm nhìn

> **Trở thành nền tảng giúp người Việt tìm kiếm, hiểu và lựa chọn bất động sản một cách minh bạch, thông minh và đáng tin cậy nhất.**

Tầm nhìn dài hạn: **Xây dựng lớp hỗ trợ quyết định bất động sản cho Việt Nam.**

## 5.2 Sứ mệnh

> **Biến dữ liệu bất động sản phân mảnh thành thông tin có cấu trúc, có thể kiểm chứng và sử dụng trực tiếp để hỗ trợ quyết định mua, bán và thuê nhà.**

Chuỗi năng lực của sản phẩm: **tổng hợp → chuẩn hóa → xác minh → loại trùng → làm giàu → xếp hạng → giải thích → kết nối**.

## 5.3 Đề xuất giá trị cốt lõi

- **Người tìm nhà:** Không cần xem nhiều tin hơn; hãy tìm đúng nhà hơn.
- **Chủ nhà:** Đăng bất động sản một lần và tiếp cận người mua/người thuê chất lượng.
- **Môi giới:** Quản lý nguồn hàng, xây dựng uy tín và tiếp cận khách hàng có nhu cầu cao.
- **Doanh nghiệp:** Biến nguồn hàng và hành vi người dùng thành dữ liệu chuyên sâu về bất động sản.

## 5.4 Định vị sản phẩm

**Danh mục:** Sàn giao dịch bất động sản dựa trên dữ liệu. **Đối tượng:** Người tìm mua hoặc thuê căn hộ tại các đô thị lớn của Việt Nam. **Giải pháp thay thế:** Batdongsan.com.vn, Nhà Tốt, Facebook, Zalo, mạng lưới môi giới và website chủ đầu tư.

> **Dành cho người Việt đang quá tải bởi thông tin bất động sản trùng lặp, phân mảnh và thiếu tin cậy, [Tên sản phẩm] là sàn giao dịch dựa trên dữ liệu, kết hợp nguồn hàng đã xác thực, hồ sơ ở cấp bất động sản, bối cảnh giá và tìm kiếm thông minh để giúp họ tìm và đánh giá đúng ngôi nhà nhanh hơn. Khác với cổng đăng tin truyền thống, sản phẩm được tổ chức quanh chính bất động sản thay vì từng tin đăng riêng lẻ.**

---

# 6. Người dùng mục tiêu

## 6.1 Người dùng chính

### Chân dung P1 — Người mua để ở

Nhu cầu: tìm và lọc căn, xem bản đồ, kiểm tra giá và thông tin bất động sản, so sánh, lưu, liên hệ và đặt lịch.

### Chân dung P2 — Người thuê

Nhu cầu: giá thuê, vị trí, thời gian di chuyển, nội thất, tiện ích, tiền cọc, ngày nhận nhà, quy định về thú cưng và tình trạng còn trống.

## 6.2 Người dùng thứ cấp

- **S1 — Chủ nhà cá nhân:** Cần giá tham khảo, đăng và xác thực tin, nhận khách hàng tiềm năng, quản lý tin.
- **S2 — Môi giới:** Cần nguồn hàng, độ phủ, khách hàng tiềm năng, hồ sơ uy tín, CRM và số liệu hiệu quả.
- **S3 — Nhà đầu tư:** Cần xu hướng giá, bất động sản so sánh, lợi suất cho thuê, tín hiệu thanh khoản và phân tích dự án.

## 6.3 Người dùng nội bộ

- **Quản trị viên:** Quản lý người dùng, quyền và cấu hình.
- **Kiểm duyệt viên:** Kiểm duyệt nội dung, tin trùng và gian lận.
- **Nhân sự xác minh:** Xác minh bất động sản, hồ sơ và tình trạng còn hàng.
- **Vận hành nguồn cung:** Tiếp nhận môi giới, nhập nguồn hàng và kiểm soát chất lượng.
- **Chăm sóc khách hàng:** Xử lý sự cố và báo cáo.
- **Vận hành dữ liệu:** Rà soát ghép thực thể và giám sát chất lượng dữ liệu.
- **Phát triển kinh doanh:** Quản lý đối tác và phát triển nguồn hàng.

## 6.4 Các bên liên quan

| Bên liên quan                                | Mối quan tâm chính                                   |
| ---------------------------------------------- | ------------------------------------------------------- |
| Nhà sáng lập                                | Thành công kinh doanh                                 |
| Sản phẩm                                     | Giá trị người dùng                                 |
| Kỹ thuật                                     | Độ tin cậy của sản phẩm                           |
| Dữ liệu/ML                                   | Chất lượng dữ liệu và năng lực phân tích      |
| Đối tác nguồn hàng, môi giới, chủ nhà | Khách hàng tiềm năng và độ phủ bất động sản |
| Người mua/người thuê                      | Khám phá bất động sản đáng tin cậy             |
| Nhà đầu tư                                 | Tăng trưởng và lợi thế phòng thủ                |
| Pháp lý                                      | Tuân thủ quy định                                   |
| Nhà cung cấp hạ tầng, bản đồ, xác minh | Dịch vụ kỹ thuật và xác minh                      |

---

# 7. Mục tiêu dự án

## 7.1 Mục tiêu kinh doanh

- **BO-01:** Kiểm chứng mức độ sẵn sàng sử dụng/chuyển sang một nền tảng khám phá bất động sản thay thế.
- **BO-02:** Xây dựng mạng lưới nguồn cung chất lượng ban đầu, giả thuyết mục tiêu là 5.000–10.000 bất động sản/chào bán đang hoạt động trong khu vực ra mắt.
- **BO-03:** Tạo thanh khoản cho sàn trong phân khúc đầu tiên.
- **BO-04:** Kiểm chứng ít nhất một hướng doanh thu khả thi: gói thuê bao môi giới, tin cao cấp hoặc khách hàng tiềm năng chất lượng.
- **BO-05:** Tạo nền tảng cho giới thiệu vay thế chấp, giải pháp chủ đầu tư, dữ liệu thị trường, dữ liệu B2B và phần mềm cho môi giới.

## 7.2 Mục tiêu sản phẩm

- **PO-01:** Cung cấp trải nghiệm khám phá nhanh qua từ khóa, bộ lọc, bản đồ và tìm theo dự án/tòa nhà.
- **PO-02:** Xây dựng mô hình thực thể bất động sản chuẩn.
- **PO-03:** Phát hiện và nhóm tin đăng trùng.
- **PO-04:** Quản lý độ mới và tình trạng còn hiệu lực của tin.
- **PO-05:** Triển khai xác minh nhiều cấp.
- **PO-06:** Cung cấp bối cảnh giá.
- **PO-07:** Hỗ trợ lưu, so sánh và liên hệ.
- **PO-08:** Cung cấp cổng quản lý nguồn hàng cho môi giới/người bán.
- **PO-09:** Thử nghiệm tìm kiếm bằng ngôn ngữ tự nhiên sau khi tìm kiếm có cấu trúc ổn định.

## 7.3 Mục tiêu người dùng

Người dùng phải có thể nhanh chóng tìm bất động sản phù hợp, hiểu lý do phù hợp, biết trạng thái xác thực, nhận biết tình trạng còn hoạt động gần đây, so sánh các lựa chọn, đánh giá giá chào trong bối cảnh thị trường và liên hệ người bán/môi giới với ít trở ngại.

## 7.4 Mục tiêu kỹ thuật

- **TO-01 — Kiến trúc sẵn sàng vận hành:** Hệ thống theo mô-đun, có khả năng quan sát, mở rộng, kiểm thử và bảo mật.
- **TO-02 — Mô hình bất động sản chuẩn:** Cơ sở dữ liệu phải phân biệt rõ bất động sản với tin đăng.
- **TO-03 — Không gian địa lý:** Hỗ trợ tọa độ, bán kính, khung nhìn bản đồ và tìm kiếm lân cận.
- **TO-04 — Tìm kiếm:** Hỗ trợ toàn văn, bộ lọc, xếp hạng, dung sai lỗi chính tả và địa lý.
- **TO-05 — Luồng dữ liệu:** Nguồn → tiếp nhận → kiểm tra → chuẩn hóa → phân giải thực thể → làm giàu → lập chỉ mục.
- **TO-06 — Khả năng quan sát:** Có nhật ký tập trung, chỉ số, truy vết, theo dõi lỗi và cảnh báo.
- **TO-07 — Bảo mật và quyền riêng tư:** Thiết kế phù hợp yêu cầu bảo vệ dữ liệu cá nhân; Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 có hiệu lực từ 01/01/2026 cùng Nghị định 356/2025/NĐ-CP quy định chi tiết thi hành.
- **TO-08 — An toàn AI:** AI không được tự tạo tin, giá hoặc thông tin pháp lý không có nguồn; không biến suy luận thành sự thật. Kết quả phải dựa trên dữ liệu bất động sản có cấu trúc.

---

# 8. Chỉ số thành công

Các mục tiêu dưới đây là giả định lập kế hoạch ban đầu và cần điều chỉnh sau giai đoạn Beta.

## 8.1 Chỉ số Sao Bắc Đẩu

### Số lượt ghép bất động sản chất lượng mỗi tháng (MQPM)

Một lượt ghép chất lượng được ghi nhận khi người dùng hợp lệ tương tác với bất động sản đang hoạt động, bất động sản đạt yêu cầu về độ mới và người dùng thực hiện hành động có ý định cao như liên hệ môi giới/chủ nhà hoặc yêu cầu xem nhà.

```text
MQPM = Số cặp người dùng–bất động sản duy nhất có hành động chất lượng cao trong tháng
```

MQPM phản ánh đồng thời chất lượng nguồn hàng, chất lượng tìm kiếm, ý định người dùng và giá trị của sàn.

## 8.2 KPI kinh doanh

| Nhóm       | KPI                                                      |                     Mục tiêu Beta |
| ----------- | -------------------------------------------------------- | ----------------------------------: |
| Nguồn cung | Bất động sản đang hoạt động                      |                            ≥ 5.000 |
| Nguồn cung | Chào bán/tin đăng đang hoạt động                 |                            ≥ 8.000 |
| Nguồn cung | Nguồn hàng xác thực hoặc đáng tin từ đối tác  |                              ≥ 70% |
| Nguồn cung | Đối tác nguồn hàng hoạt động mỗi tháng         |                               ≥ 20 |
| Nguồn cung | Môi giới hoạt động                                  |                              ≥ 100 |
| Sàn        | Lượt ghép chất lượng/tháng                        | ≥ 500 sau giai đoạn kiểm chứng |
| Sàn        | Tỷ lệ liên hệ từ trang tin/bất động sản         |                               ≥ 5% |
| Sàn        | Tỷ lệ duy trì đối tác nguồn hàng                 |                       ≥ 60%/tháng |
| Sàn        | Chi phí cho mỗi khách hàng tiềm năng chất lượng |        Đo đường cơ sở trước |

Doanh thu không phải điều kiện ra mắt chính trong giai đoạn kiểm chứng.

## 8.3 KPI sản phẩm và tương tác

| KPI                                                                    | Mục tiêu |
| ---------------------------------------------------------------------- | ---------: |
| Tìm kiếm → Chi tiết bất động sản                               |     ≥ 30% |
| Chi tiết → Lưu                                                      |      ≥ 5% |
| Chi tiết → Liên hệ                                                 |   ≥ 3–5% |
| Người tìm kiếm có dùng so sánh                                  |      ≥ 5% |
| Tìm kiếm không có kết quả                                        |      < 10% |
| Tin trùng hiển thị cho người dùng                                |       < 5% |
| Nguồn hàng hết hiệu lực bị báo cáo                             |       < 5% |
| Người dùng hoạt động hằng tháng trong giai đoạn kiểm chứng |   ≥ 5.000 |
| Người dùng quay lại trong 30 ngày                                 |     ≥ 20% |
| Lượt tìm kiếm/phiên                                               |       ≥ 2 |
| Trang chi tiết/phiên                                                 |       ≥ 5 |
| Bất động sản đã lưu/người có lưu                            |       ≥ 2 |
| Người tìm kiếm có dùng lưu bộ lọc                             |     ≥ 10% |

## 8.4 KPI kỹ thuật

- **Tính sẵn sàng:** ≥ 99,9% cho các dịch vụ lõi trên môi trường vận hành.
- **API:** p95 < 500 ms đối với API đọc lõi.
- **Tìm kiếm:** p95 < 1,5 giây.
- **Tỷ lệ lỗi:** < 1% yêu cầu lỗi phía máy chủ.
- **Độ mới dữ liệu:** < 15 phút với đối tác tin cậy có API/webhook; ≤ 24 giờ với nguồn xử lý theo lô.
- **Sao lưu:** RPO ≤ 24 giờ và RTO ≤ 4 giờ cho giai đoạn Beta.
- **Bảo mật:** Mã hóa khi truyền và lưu, quản lý bí mật, RBAC, nhật ký kiểm toán cho thao tác đặc quyền, quét lỗ hổng và xác minh bản sao lưu.

---

# 9. Phạm vi dự án

## 9.1 Trong phạm vi

### Địa bàn và phân khúc giai đoạn 1

Tập trung tại **Hà Nội và các cụm đô thị liên quan được chọn trong giai đoạn khám phá**, ưu tiên căn hộ thay vì bao phủ mọi loại hình bất động sản.

### Nền tảng người dùng

- **Tài khoản:** Đăng nhập email/số điện thoại, OTP và hồ sơ.
- **Tìm kiếm:** Vị trí, dự án, tòa nhà, giá, diện tích, phòng ngủ, phòng tắm, loại hình, loại giao dịch và trạng thái xác thực.
- **Bản đồ:** Ghim bất động sản, tìm theo khung nhìn, đồng bộ danh sách và bản đồ.
- **Hồ sơ 360°:** Ảnh, video, giá, giá/m², dự án, tòa nhà, tầng, diện tích, phòng ngủ, phòng tắm, nội thất, mô tả, bản đồ, tiện ích, xác thực, độ mới và các chào bán đang hoạt động.
- **Bối cảnh giá:** Dùng tin so sánh, tin lịch sử và thống kê khu vực; chưa tuyên bố là định giá chuyên nghiệp.
- **Lưu và so sánh:** Lưu bất động sản/bộ lọc; so sánh 2–4 bất động sản.
- **Liên hệ:** Liên hệ môi giới, chủ nhà và gửi yêu cầu tư vấn.

### Nền tảng nguồn cung

Hỗ trợ tiếp nhận và hồ sơ môi giới; tạo, sửa và quản lý vòng đời tin; nhập CSV, nhập hàng loạt và nhận luồng API đối tác khi có; hộp thư khách hàng tiềm năng; số liệu hiệu quả tin đăng. Vòng đời tin gồm: **Bản nháp → Chờ duyệt → Đang hoạt động → Tạm dừng → Đã bán/cho thuê → Hết hạn hoặc Bị từ chối**.

### Xác minh

| Cấp | Ý nghĩa                                               |
| ---- | ------------------------------------------------------- |
| V0   | Chưa xác minh                                         |
| V1   | Đã xác minh danh tính                               |
| V2   | Đã xác minh thông tin bất động sản              |
| V3   | Đã xác minh bằng chứng sở hữu/quyền phân phối |

Thời điểm xác nhận tình trạng còn hàng gần nhất được hiển thị riêng với cấp xác minh.

### Nền tảng dữ liệu và quản trị nội bộ

Nền tảng dữ liệu gồm chuẩn hóa, chuẩn hóa địa chỉ, mã hóa địa lý, ghép dự án/tòa nhà, phát hiện trùng, phân giải thực thể và chấm điểm chất lượng. Hệ thống quản trị gồm quản lý người dùng, kiểm duyệt tin, xác minh, xử lý báo cáo, gộp/tách bất động sản, quản lý môi giới/đối tác và nhật ký kiểm toán.

### AI — Beta có kiểm soát

Nếu dữ liệu có cấu trúc đủ ổn định, triển khai tìm kiếm bằng ngôn ngữ tự nhiên, ví dụ: “Căn hai phòng ngủ dưới 4 tỷ đồng ở phía Tây Hà Nội, gần trường học.” Luồng xử lý là **ngôn ngữ tự nhiên → trích xuất ý định → truy vấn có cấu trúc → công cụ tìm kiếm**. AI không trực tiếp tạo nguồn hàng.

## 9.2 Ngoài phạm vi Beta

- **Giao dịch:** Đặt cọc trực tuyến, ký quỹ, ký hợp đồng đầy đủ và sang tên.
- **Ngân hàng:** Khởi tạo khoản vay thế chấp, cho vay và chấm điểm tín dụng.
- **AVM toàn diện:** Chưa xây mô hình định giá tự động toàn quốc tương tự Zillow do chưa có lợi thế dữ liệu tương đương.
- **Quản lý bất động sản:** Ứng dụng cư dân, hóa đơn tiện ích, khiếu nại và vận hành tiện ích.
- **Ra mắt toàn quốc:** Không triển khai trong giai đoạn 1.
- **Phân khúc khác:** Chưa ưu tiên bất động sản công nghiệp, nghỉ dưỡng, đất nông nghiệp, văn phòng thương mại, kho và khách sạn.
- **Ứng dụng di động native:** Không bắt buộc trong bản kiểm chứng nếu web đáp ứng/PWA đủ dùng.

## 9.3 Phạm vi tương lai

- **Giai đoạn 2:** Gợi ý nâng cao, dữ liệu giá, tìm kiếm ngôn ngữ tự nhiên, cảnh báo nhu cầu đã lưu và CRM môi giới.
- **Giai đoạn 3:** Trợ lý AI bất động sản, định giá nâng cao, đặt lịch tham quan, tính khả năng chi trả và giới thiệu vay thế chấp.
- **Giai đoạn 4:** Quản lý đề nghị mua, theo dõi giao dịch, dịch vụ pháp lý và kiểm định.
- **Giai đoạn 5:** Đồ thị bất động sản toàn quốc, dữ liệu thị trường, bảng điều khiển chủ đầu tư, API dữ liệu và API định giá.

Hành trình dài hạn: **tìm kiếm → hiểu → so sánh → tài chính → xem nhà → đề nghị mua → giao dịch → chuyển vào ở**.

---

# 10. Ước tính ngân sách và nguồn lực

## 10.1 Ngân sách sơ bộ

Các con số là ước tính để lập kế hoạch, không phải báo giá. Đường cơ sở: sáu tháng, bản Beta vận hành thực tế, thị trường căn hộ Hà Nội, ưu tiên web và nhóm khởi nghiệp nhỏ.

### Nhân sự

| Hạng mục                     |   Ước tính 6 tháng |
| ------------------------------ | ---------------------: |
| Sản phẩm/BA                  | 180–300 triệu đồng |
| UX/UI                          | 120–220 triệu đồng |
| Kỹ sư frontend               | 300–500 triệu đồng |
| Kỹ sư backend                | 400–700 triệu đồng |
| Dữ liệu/ML                   | 220–400 triệu đồng |
| QA                             | 120–220 triệu đồng |
| DevOps/đám mây              | 120–240 triệu đồng |
| Vận hành dữ liệu/xác minh | 150–300 triệu đồng |

**Tổng nhân sự ước tính: 1,6–2,9 tỷ đồng.**

### Công nghệ và chi phí khác

| Nhóm                          | Hạng mục                                                                                                         |            Ước tính |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------ | ---------------------: |
| Công nghệ                    | Điện toán đám mây/cơ sở dữ liệu                                                                          |  50–120 triệu đồng |
| Công nghệ                    | Hạ tầng tìm kiếm                                                                                               |   20–60 triệu đồng |
| Công nghệ                    | Lưu trữ đối tượng/CDN                                                                                        |   10–30 triệu đồng |
| Công nghệ                    | Bản đồ/mã hóa địa lý                                                                                       |   20–80 triệu đồng |
| Công nghệ                    | Giám sát/khả năng quan sát                                                                                    |   10–30 triệu đồng |
| Công nghệ                    | OTP/email/thông báo                                                                                              |   10–30 triệu đồng |
| Công nghệ                    | Thử nghiệm AI/API                                                                                                |   20–80 triệu đồng |
| Pháp lý/tuân thủ/bảo mật | Tư vấn, điều khoản, quyền riêng tư, hợp đồng dữ liệu/nguồn hàng, kiểm thử bảo mật               | 120–300 triệu đồng |
| Phát triển nguồn cung/GTM   | Tiếp nhận đối tác, khuyến khích môi giới, nội dung, SEO, quảng cáo, cộng đồng, công cụ bán hàng | 300–800 triệu đồng |

Tổng công nghệ khoảng **140–430 triệu đồng**; dự phòng **10–15%**. Ngân sách cơ sở cho Beta là **2,5–5 tỷ đồng/6 tháng**. Có thể giảm còn khoảng **1–2 tỷ đồng** nếu nhà sáng lập trực tiếp lập trình, chưa tuyển đủ đội ngũ, chưa chi mạnh cho quảng cáo, chủ yếu xác minh thủ công, chưa làm ứng dụng native và tận dụng tín dụng đám mây. Mức này chỉ phù hợp với **kiểm chứng tinh gọn**, không phải một tổ chức vận hành đầy đủ.

## 10.2 Nguồn lực

Đội ngũ tối thiểu đề xuất: 1 Chủ sản phẩm/BA, 1 UX/UI, 1 frontend, 2 backend, 1 dữ liệu/ML, 1 QA, 1 DevOps bán thời gian, 1 nguồn cung/phát triển kinh doanh và 1 vận hành dữ liệu/xác minh; tổng cộng khoảng 8–10 người.

### Nền tảng công nghệ dự kiến

| Lớp                     | Công nghệ dự kiến                                                         |
| ------------------------ | ----------------------------------------------------------------------------- |
| Frontend                 | Next.js/React                                                                 |
| Backend                  | FastAPI hoặc NestJS                                                          |
| Cơ sở dữ liệu chính | PostgreSQL + PostGIS                                                          |
| Tìm kiếm               | OpenSearch hoặc Elasticsearch                                                |
| Bộ nhớ đệm           | Redis                                                                         |
| Lưu trữ                | Kho đối tượng tương thích S3                                           |
| Nhắn tin hệ thống     | Hàng đợi/luồng sự kiện                                                  |
| Phân tích              | Phân tích sản phẩm; kho dữ liệu khi cần                                |
| Giám sát               | Nhật ký, chỉ số, truy vết, theo dõi lỗi                                |
| AI                       | API LLM/mô hình quản lý sẵn + truy xuất có cấu trúc + gọi công cụ |

---

# 11. Giả định

- **A01:** Giai đoạn đầu tập trung căn hộ thay vì mọi loại hình bất động sản.
- **A02:** Hà Nội có đủ nhu cầu và nguồn cung để kiểm chứng.
- **A03:** Có thể thiết lập quan hệ đối tác nguồn cung trước khi ra mắt công khai.
- **A04:** Một phần nguồn hàng có thể đến từ luồng đối tác được phép, chủ nhà hoặc môi giới.
- **A05:** Người mua/người thuê được sử dụng miễn phí trong giai đoạn đầu.
- **A06:** Doanh thu từ phía cung khả thi hơn trong thời gian đầu.
- **A07:** Mức độ sẵn sàng chuyển đổi phụ thuộc vào chất lượng nhiều hơn số lượng nguồn hàng đơn thuần.
- **A08:** Có thể loại trùng tin căn hộ với độ chính xác hữu ích.
- **A09:** Giai đoạn xác minh đầu vẫn cần con người rà soát.
- **A10:** Nhận diện căn hộ/dự án có cấu trúc dễ hơn nhà đất riêng lẻ.
- **A11:** Không cần giao dịch đầu cuối để kiểm chứng nhu cầu sàn.
- **A12:** AI không phải điều kiện bắt buộc để đạt PMF mà là lớp tăng cường cho sản phẩm dữ liệu hữu ích.
- **A13:** Dữ liệu giá ban đầu có thể dựa trên bất động sản so sánh và thống kê tin đăng trước khi có AVM.
- **A14:** Hợp đồng đối tác dữ liệu phải quy định rõ quyền sở hữu, phạm vi sử dụng, thời hạn lưu và quyền phân phối lại.

---

# 12. Ràng buộc

- **C01 — Không có hạ tầng MLS thống nhất:** Việt Nam chưa có hạ tầng danh sách bất động sản toàn quốc tương đương nguồn cấp MLS tại Mỹ, khiến tích hợp nguồn hàng khó hơn.
- **C02 — Dữ liệu phân mảnh:** Địa chỉ và thuộc tính khác nhau giữa các nguồn; “Vinhomes Ocean Park”, “Ocean Park”, “VHOP” và “Vinhomes OCP” có thể cùng chỉ một dự án.
- **C03 — Nhận diện bất động sản:** Không phải bất động sản nào cũng có mã căn được phép công khai.
- **C04 — Pháp lý và quyền riêng tư:** Dự án phải tuân thủ quy định bảo vệ dữ liệu cá nhân hiện hành, bao gồm Luật số 91/2025/QH15 có hiệu lực từ 01/01/2026.
- **C05 — Môi trường pháp lý bất động sản:** Luật Kinh doanh bất động sản 2023 và văn bản hướng dẫn điều chỉnh hoạt động kinh doanh; trong năm 2026 các đề xuất sửa đổi vẫn được thảo luận. Rà soát pháp lý phải diễn ra liên tục.
- **C06 — Bài toán khởi đầu:** Không có người mua thì môi giới không đăng tin; không có nguồn hàng thì người mua không truy cập.
- **C07 — Ngân sách:** Giai đoạn đầu không thể cạnh tranh với nền tảng hiện hữu bằng chi tiêu quảng cáo.
- **C08 — Chi phí xác minh:** Xác minh càng sâu thì độ tin cậy càng cao nhưng chi phí vận hành cũng tăng.

---

# 13. Phụ thuộc

- **D01 — Đối tác nguồn hàng:** Phụ thuộc quan trọng nhất; có thể gồm nhóm môi giới, đại lý, chủ đầu tư, đơn vị quản lý bất động sản và chủ nhà cá nhân.
- **D02 — Mô hình dữ liệu:** Tìm kiếm, loại trùng và dữ liệu giá phụ thuộc lược đồ chuẩn.
- **D03 — Nhà cung cấp vị trí/bản đồ:** Cần cho mã hóa địa lý, tuyến đường, bản đồ và tiện ích lân cận.
- **D04 — Dịch vụ danh tính/OTP:** Cần để xác thực tài khoản và môi giới.
- **D05 — Hạ tầng đám mây:** Điện toán, cơ sở dữ liệu, lưu trữ đối tượng, CDN và sao lưu.
- **D06 — Hạ tầng tìm kiếm:** Phải sẵn sàng trước khi có lưu lượng thực tế.
- **D07 — Pháp lý và tuân thủ:** Bắt buộc trước khi ra mắt công khai, nhập dữ liệu quy mô lớn, xác minh danh tính và thu phí.
- **D08 — Phân tích:** Không ra mắt Beta nếu chưa đo được tìm kiếm, xem chi tiết, lưu, so sánh, liên hệ và báo cáo.
- **D09 — Vận hành kiểm duyệt:** Phát hiện tự động không thay thế hoàn toàn việc con người rà soát.

---

# 14. Rủi ro

## 14.1 Rủi ro thị trường

| Rủi ro                                              | Khả năng  | Tác động    | Giảm thiểu                                                  |
| ---------------------------------------------------- | ----------- | -------------- | ------------------------------------------------------------- |
| Người dùng tiếp tục dùng nền tảng hiện hữu | Cao         | Nghiêm trọng | Chọn phân khúc hẹp và USP rõ ràng                      |
| Không đủ nguồn hàng                             | Cao         | Nghiêm trọng | Ưu tiên nguồn cung trước khi ra mắt                     |
| Nguồn hàng tập trung ở ít đối tác            | Trung bình | Cao            | Đa dạng hóa nguồn cung                                    |
| Người dùng không muốn chuyển đổi             | Cao         | Cao            | Kiểm chứng nguyên mẫu/người dùng trước khi mở rộng |
| Đối thủ sao chép tính năng                     | Trung bình | Cao            | Xây lợi thế dữ liệu thay vì chỉ lợi thế tính năng  |

Rủi ro thị trường lớn nhất là sản phẩm trở thành **“Batdongsan.com.vn nhưng có ít tin hơn”**. Đây là kịch bản phải tránh bằng khác biệt có thể đo lường.

## 14.2 Rủi ro kỹ thuật

- **T-R01 — Loại trùng sai:** Gộp nhầm hai bất động sản hoặc không gộp cùng một bất động sản. Giảm thiểu bằng điểm tin cậy, con người rà soát và công cụ gộp/tách trong trang quản trị.
- **T-R02 — Chất lượng dữ liệu thấp:** Dữ liệu đầu vào kém tạo kết quả phân tích kém. Giảm thiểu bằng kiểm tra, chuẩn hóa, điểm tin cậy nguồn và phát hiện bất thường.
- **T-R03 — Mức độ liên quan của tìm kiếm thấp:** Xếp hạng kém làm giảm trải nghiệm dù có đủ nguồn hàng. Cần chỉ số liên quan, phân tích truy vấn, hành vi nhấp và đánh giá ngoại tuyến.
- **T-R04 — AI bịa thông tin:** AI có thể tạo sai thông tin căn, tiện ích, pháp lý hoặc giá. Cần dùng AI gọi công cụ, dữ liệu có cấu trúc, trích dẫn/nguồn gốc và không cho phép tạo tin thiếu căn cứ. Kiến trúc Zillow năm 2026 cũng kết nối trải nghiệm AI với các hệ thống chuyên biệt về tìm kiếm, tài chính và định giá thay vì giao toàn bộ cho một mô hình tổng quát.
- **T-R05 — Khả năng mở rộng:** Bản đồ và tìm kiếm có thể tốn tài nguyên; giảm thiểu bằng bộ nhớ đệm, chỉ mục địa lý, cụm tìm kiếm và CDN.

## 14.3 Rủi ro vận hành

Các rủi ro chính gồm xác minh trở thành nút thắt, nguồn hàng hết hiệu lực nhanh hơn khả năng kiểm tra, môi giới đăng tin rác/trùng, tài khoản gian lận và lượng yêu cầu hỗ trợ tăng nhanh. Giảm thiểu bằng tự động hóa, uy tín nguồn, rà soát dựa trên rủi ro, chấm điểm môi giới và công cụ tự quản lý nguồn hàng.

## 14.4 Rủi ro kinh doanh

- **B-R01 — Thu phí quá sớm:** Có thể làm giảm nguồn hàng trước khi có nhu cầu; cần tạo thanh khoản trước rồi mới kiếm tiền.
- **B-R02 — Chi phí thu hút khách hàng cao:** Cạnh tranh quảng cáo tìm kiếm có thể không hiệu quả; ưu tiên SEO, trang dự án/giá, nội dung, giới thiệu và cộng đồng.
- **B-R03 — Rò rỉ khách hàng tiềm năng:** Người dùng có thể hoàn tất hành trình ngoài nền tảng; về dài hạn bổ sung nhắn tin, lịch xem, CRM và công cụ giao dịch, nhưng không chặn trao đổi ngoài nền tảng trong MVP.
- **B-R04 — Thiếu vốn:** Sàn có thể cần thời gian dài để đạt thanh khoản; giảm thiểu bằng thị trường hẹp, vốn theo cột mốc và kiểm chứng trước khi mở rộng đội ngũ.
- **B-R05 — Quyền lực nhà cung cấp:** Đối tác lớn có thể đòi độc quyền hoặc quyền kiểm soát quá mức; cần nhiều đối tác, thu hút chủ nhà và xây hệ sinh thái môi giới cá nhân.

---

# 15. Tiến độ cấp cao

Đường cơ sở: **24 tuần để ra mắt Beta vận hành thực tế**.

## Giai đoạn 0 — Khám phá, tuần 1–3

Thực hiện 20–30 cuộc phỏng vấn người mua/người thuê, 10–20 cuộc phỏng vấn môi giới, lập bản đồ nguồn cung, phân tích đối thủ, nghiên cứu lược đồ bất động sản và thử nghiệm nguyên mẫu. Đầu ra gồm nghiên cứu người dùng/thị trường, chiến lược nguồn cung, kiểm chứng vấn đề và định nghĩa MVP. Cổng quyết định: **Tiếp tục/Điều chỉnh/Dừng**; không xây nếu chưa kiểm chứng được nỗi đau.

## Giai đoạn 1 — Sản phẩm và kiến trúc, tuần 4–6

Thiết kế luồng UX, hệ thống thiết kế, kiến trúc, mô hình bất động sản chuẩn, hợp đồng API, đo sự kiện và hạ tầng. Đầu ra: PRD, SRS, mô hình dữ liệu, kiến trúc hệ thống, nguyên mẫu UI và kế hoạch phân tích.

## Giai đoạn 2 — Xây sàn lõi, tuần 7–14

Xây tài khoản, bất động sản, tin đăng, tìm kiếm, bản đồ, trang chi tiết, lưu, so sánh, liên hệ, cổng môi giới và trang quản trị.

## Giai đoạn 3 — Dữ liệu và độ tin cậy, tuần 10–17

Thực hiện song song việc tiếp nhận, chuẩn hóa, nhận diện dự án/tòa nhà, loại trùng, quy trình xác minh, quản lý độ mới và thống kê giá.

## Giai đoạn 4 — Hoàn thiện vận hành, tuần 18–20

Kiểm thử tích hợp/tải, rà soát bảo mật, xác minh phân tích, sao lưu, thử khôi phục thảm họa, giám sát và UAT. Chỉ sẵn sàng vận hành khi không có lỗi P0, không có lỗ hổng nghiêm trọng đã biết, sao lưu đã thử, giám sát hoạt động, phân tích đã xác minh và đội kiểm duyệt sẵn sàng.

## Giai đoạn 5 — Beta có kiểm soát, tuần 21–24

Ra mắt tại địa bàn chọn lọc với nhóm môi giới và người dùng được mời; đo tìm kiếm, nguồn cung, tin trùng, tin hết hiệu lực, liên hệ, quay lại và phản hồi.

## Sau Beta, tháng 7–9

Dựa trên dữ liệu để **mở rộng, lặp cải tiến, chuyển hướng hoặc dừng**. Nếu chỉ số tốt, triển khai tìm kiếm AI, cảnh báo nhu cầu đã lưu, dữ liệu giá nâng cao, CRM môi giới và địa bàn thứ hai.

---

# 16. Các bên liên quan và quyền sở hữu

## 16.1 Vai trò và trách nhiệm

- **Nhà sáng lập/Nhà tài trợ dự án:** Tầm nhìn, huy động vốn, quyết định chiến lược, quan hệ đối tác và phê duyệt phạm vi cuối.
- **Chủ sản phẩm:** Chiến lược, lộ trình, ưu tiên và KPI sản phẩm.
- **Chuyên viên phân tích nghiệp vụ:** Yêu cầu, quy trình, quy tắc nghiệp vụ, yêu cầu dữ liệu, tiêu chí chấp nhận và tài liệu.
- **Nhà thiết kế sản phẩm:** Hỗ trợ nghiên cứu, UX, UI và khả năng sử dụng.
- **Trưởng nhóm kỹ thuật:** Kiến trúc, quyết định kỹ thuật, chất lượng kỹ thuật và mức độ sẵn sàng vận hành.
- **Kỹ sư backend:** API, mô hình dữ liệu, logic nghiệp vụ và tích hợp.
- **Kỹ sư frontend:** Web người dùng, cổng nguồn cung và giao diện quản trị.
- **Kỹ sư dữ liệu/ML:** Tiếp nhận, chuẩn hóa, phân giải thực thể, loại trùng, xếp hạng, dữ liệu giá và dịch vụ AI.
- **Kỹ sư QA:** Chiến lược kiểm thử, hồi quy, tích hợp và chất lượng phát hành.
- **DevOps/Nền tảng:** CI/CD, hạ tầng, giám sát, bảo mật cơ sở và sao lưu.
- **Nguồn cung/Phát triển kinh doanh:** Thu hút đối tác, tiếp nhận môi giới, phối hợp hợp đồng và sản lượng nguồn hàng.
- **Vận hành xác minh:** Rà soát tin/hồ sơ/gian lận và độ mới nguồn hàng.
- **Tăng trưởng:** Thu hút, SEO, nội dung, kích hoạt và thử nghiệm duy trì.
- **Pháp lý/Tuân thủ:** Điều khoản, quyền riêng tư, xử lý dữ liệu, hợp đồng nguồn hàng và tuân thủ nền tảng.

## 16.2 Ma trận RACI

**R = Thực hiện; A = Chịu trách nhiệm cuối; C = Được tham vấn; I = Được thông báo.**

| Hoạt động                         | Nhà sáng lập | Sản phẩm | BA | Kỹ thuật | Dữ liệu/ML | UX | QA  | Nguồn cung/BD | Pháp lý |
| ------------------------------------ | --------------- | ---------- | -- | ---------- | ------------ | -- | --- | -------------- | --------- |
| Tầm nhìn sản phẩm                | A               | R          | C  | C          | I            | C  | I   | C              | I         |
| Kiểm chứng thị trường           | C               | A          | R  | I          | I            | R  | I   | R              | I         |
| Phạm vi sản phẩm                  | A               | R          | R  | C          | C            | C  | C   | C              | I         |
| PRD                                  | I               | A          | R  | C          | C            | C  | C   | I              | I         |
| Kiến trúc hệ thống               | I               | C          | C  | A/R        | C            | I  | C   | I              | C         |
| Mô hình dữ liệu bất động sản | I               | C          | R  | A          | R            | I  | C   | C              | I         |
| UX/UI                                | I               | A          | C  | C          | I            | R  | C   | I              | I         |
| Tìm kiếm                           | I               | A          | C  | R          | R            | C  | C   | I              | I         |
| Loại trùng                         | I               | C          | C  | C          | A/R          | I  | C   | C              | I         |
| Quy trình xác minh                 | I               | A          | R  | C          | C            | C  | C   | R              | C         |
| Phát triển nguồn cung             | C               | C          | I  | I          | I            | I  | I   | A/R            | C         |
| Đối tác dữ liệu                 | A               | C          | C  | C          | C            | I  | I   | R              | C         |
| Quyền riêng tư                    | I               | C          | C  | C          | C            | I  | I   | I              | A/R       |
| Bảo mật                            | I               | I          | C  | A/R        | C            | I  | C   | I              | C         |
| QA                                   | I               | C          | C  | C          | C            | C  | A/R | I              | I         |
| Phát hành thực tế                | A               | R          | C  | R          | C            | I  | R   | I              | C         |
| Theo dõi KPI                        | C               | A/R        | R  | C          | C            | C  | I   | C              | I         |
| Quyết định triển khai/dừng      | A               | R          | C  | C          | C            | C  | C   | C              | C         |

---

# Kết luận

Dự án không nên được định nghĩa là một “bản sao Zillow” hoặc một website đăng tin bất động sản mới. Định nghĩa chiến lược phù hợp hơn là: **sàn giao dịch bất động sản đáng tin cậy, dựa trên dữ liệu và được tổ chức quanh bất động sản thay vì từng tin đăng**.

Khác biệt cốt lõi gồm **nhận diện bất động sản + nguồn hàng xác thực + độ mới + loại trùng + bối cảnh giá + khám phá thông minh**. Thứ tự hình thành lợi thế phòng thủ là: **nguồn cung → dữ liệu sạch → Đồ thị bất động sản → tìm kiếm → người dùng → dữ liệu hành vi → xếp hạng tốt hơn → thêm nguồn cung → dữ liệu giá → AI → giao dịch**.

Ưu tiên chiến lược của giai đoạn 1 không phải “Có bao nhiêu tính năng?”, mà là: **“Có thể xây dựng một tập nguồn hàng đủ sạch, đủ mới và đủ hữu ích để một nhóm người tìm nhà thực sự chọn sản phẩm thay cho cách tìm hiện tại hay không?”**

Nếu câu trả lời được chứng minh bằng dữ liệu, dự án có nền tảng mở rộng theo lộ trình: **nền tảng tìm kiếm → nền tảng dữ liệu chuyên sâu → trợ lý AI bất động sản → nền tảng giao dịch → hệ sinh thái vận hành bất động sản**.

Tài liệu này là cơ sở cho chuỗi tài liệu tiếp theo:

```text
01_Project_Brief.md → 02_Market_Research.md → 03_User_Research.md → 04_Business_Model.md
→ 05_Product_Vision_Strategy.md → 06_PRD.md → 07_SRS.md → 08_Data_Model.md
→ 09_System_Architecture.md → 10_MVP_Roadmap.md
```
