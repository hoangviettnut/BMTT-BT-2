# BMTT-BT-2
# SINH VIÊN: LƯƠNG HOÀNG VIỆT - K225480106073
## 1.Cấu trúc PDF liên quan chữ ký (đã trình bày trong PDF
## 2. Vị trí lưu thời gian ký (đã trình bày trong PDF)
## 3. Các bước tạo và lưu chữ ký số trong PDF
### a) Cài đặt các thư viện cần thiết để chạy code Python
Trong bài này ngôn ngữ sử dụng là Python, với yêu cầu mà đề bài đặt ra các thư viện ta cần phải cài là: pyHanko, pyPDF, pyPDF2, pyHanko image support (PIL).<br>
Dưới đây là câu lệnh sử dụng để cài các thư viện cần thiết, dược chạy trên cmd
<img width="1483" height="762" alt="image" src="https://github.com/user-attachments/assets/8930567d-5bd9-48ea-980f-aef2df9d2a9d" /><br>
### b) Tạo các file .pem bằng OPENSSL
Tạo certificate.pem và private.pem
<img width="1483" height="762" alt="image" src="https://github.com/user-attachments/assets/d6b3e336-954d-4fda-9b16-eb52e56ee6e0" /> <br>
### c) Viết chương trình để ký vào file PDF (source code đính kèm theo file)
### d) Tạo môi trường ảo để cài thư viện do môi trường cũ bị lỗi:<img width="508" height="94" alt="image" src="https://github.com/user-attachments/assets/a0a2fc43-9938-4024-94ec-0a4d51148ca7" /><br>
### e) Kết quả chạy scripts thành công: <img width="839" height="139" alt="image" src="https://github.com/user-attachments/assets/9596f41b-f57f-42fe-a0cf-40cdbcddcf22" />
### f) File PDF được xuất với chữ ký số: <img width="1920" height="1200" alt="image" src="https://github.com/user-attachments/assets/9d26338e-286a-4b56-83a4-18772fab9400" /><br>
Sử dụng Microsoft Edge Browser để kiểm tra.
## 4) Xác thực chữ ký trên PDF đã ký:
### a) Dựa vào yêu cầu bài đưa ra, sử dụng file verify.py để thiêt kế kiểm tra xác thực chữ ký. Sau khi kiểm tra PDF sẽ trả về kết quả vào file kiemtra.txt<br>
<img width="1444" height="370" alt="image" src="https://github.com/user-attachments/assets/f9c047bc-619c-49d9-b044-3772ea5de4fd" /><br>
### b) Script giả lập việc “can thiệp” (tampering) vào file PDF đã ký (chạy file tampered.py):<img width="872" height="65" alt="image" src="https://github.com/user-attachments/assets/830ea70b-cf4b-4934-9172-fa1511959ae6" /><br>
Toàn bộ PDF thu được sau cả quá trình
<img width="1900" height="1119" alt="image" src="https://github.com/user-attachments/assets/b47e7cd7-5c15-48d5-98eb-43c965bec295" /><br>
### Toàn bộ log đã được lưu trong file kiemtra.txt với đầy đủ các bước kiểm tra mà bài yêu cầu.
## NOTE: CODE chứa đầy đủ các thuật toán, yêu cầu mà bài toán đề ra.
## CODE & PDF được upload kèm theo file README.md
