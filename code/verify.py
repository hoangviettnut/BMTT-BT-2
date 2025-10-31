# ==========================================
# verify_sign.py
# Kiểm tra chữ ký số trong file PDF (theo yêu cầu bài tập AT&BMTT)
# Thực hiện: LUONG HOANG VIET
# ==========================================

import os
import re
import hashlib
import datetime
from datetime import timezone, timedelta
from typing import Any, Optional

from pyhanko.pdf_utils.reader import PdfFileReader
from pyhanko.sign import validation
from pyhanko.sign.diff_analysis import ModificationLevel
from pyhanko_certvalidator import ValidationContext
from pyhanko.keys import load_cert_from_pemder

# === Cấu hình đường dẫn (tùy chỉnh theo thư mục bạn) ===
PDF_PATH = r"D:\LHV_BMTT_BT2\PDF\signed.pdf"
CERT_PEM = r"D:\LHV_BMTT_BT2\key\certificate.pem"
LOG_FILE = r"D:\LHV_BMTT_BT2\kiemtra.txt"

# ================== HÀM PHỤ TRỢ ==================

def safe_print(msg: str):
    """In ra console không lỗi font."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="ignore").decode("utf-8"))

def log(msg: str):
    """In ra console và ghi vào file log."""
    safe_print(msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8", errors="ignore") as f:
        f.write(msg + "\n")

def format_fp(fp: Optional[Any]) -> str:
    """Định dạng fingerprint cho dễ đọc."""
    if fp is None:
        return "N/A"
    if isinstance(fp, (bytes, bytearray)):
        h = fp.hex().upper()
    else:
        s = str(fp)
        h = re.sub(r"[^0-9A-Fa-f]", "", s).upper()
        if not h:
            return s
    return " ".join(h[i:i + 2] for i in range(0, len(h), 2))

def compute_sha256_range(pdf_bytes: bytes, byte_range):
    """Tính hash SHA256 trên vùng ByteRange (2 phần)."""
    try:
        br = [int(x) for x in byte_range]
        part1 = pdf_bytes[br[0]: br[0] + br[1]]
        part2 = pdf_bytes[br[2]: br[2] + br[3]]
        return hashlib.sha256(part1 + part2).hexdigest()
    except Exception as e:
        return f"Lỗi khi tính hash: {e}"

def try_validation(sig_obj, trust_ctx):
    """
    Gọi validate_pdf_signature thử theo nhiều kiểu để tương thích các version pyHanko.
    Trả về (result, error)
    """
    attempts = [
        ("validation_context_kw", {"validation_context": trust_ctx}),
        ("vc_kw", {"vc": trust_ctx}),
        ("positional", (trust_ctx,)),
        ("no_ctx", {})
    ]
    last_err = None
    for name, params in attempts:
        try:
            if name == "positional":
                result = validation.validate_pdf_signature(sig_obj, *params)
            else:
                result = validation.validate_pdf_signature(sig_obj, **params)
            return result, None
        except TypeError as te:
            last_err = te
            continue
        except Exception as e:
            return None, f"Lỗi khi xác thực ({name}): {repr(e)}"
    return None, f"Tất cả các cách gọi đều lỗi. Ngoại lệ cuối: {repr(last_err)}"

def get_first_attr(obj: Any, *names):
    """Truy cập attribute hoặc key đầu tiên hợp lệ trong object."""
    if obj is None:
        return None
    for n in names:
        try:
            if hasattr(obj, n):
                return getattr(obj, n)
        except Exception:
            pass
        try:
            if isinstance(obj, dict) and n in obj:
                return obj[n]
        except Exception:
            pass
    return None

# ================== CHƯƠNG TRÌNH CHÍNH ==================

def main():
    # Xóa file log cũ
    try:
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
    except Exception:
        pass

    log("=== LUONG HOANG VIET - PDF SIGNATURE CHECK ===")
    log(f"TIME CHECK: {datetime.datetime.now()}")
    log(f"FILE: {PDF_PATH}")
    log("=" * 65)

    # === Tạo ValidationContext ===
    try:
        if os.path.exists(CERT_PEM):
            cert_root = load_cert_from_pemder(CERT_PEM)
            trust_ctx = ValidationContext(trust_roots=[cert_root], allow_fetching=True)
            log("- Đã nạp chứng thư gốc từ PEM.")
        else:
            trust_ctx = ValidationContext(trust_roots=None, allow_fetching=True)
            log("- Không có PEM tin cậy, cho phép OCSP/CRL online.")
    except Exception as e:
        log(f"⚠️ Lỗi khi đọc chứng thư: {e}")
        trust_ctx = ValidationContext(trust_roots=None, allow_fetching=True)

    if not os.path.exists(PDF_PATH):
        log(f"❌ File PDF không tồn tại: {PDF_PATH}")
        return

    try:
        with open(PDF_PATH, "rb") as fh:
            reader = PdfFileReader(fh)
            signatures = list(reader.embedded_signatures)
            if not signatures:
                log("❌ Không tìm thấy chữ ký trong tài liệu.")
                return

            sig = signatures[0]  # lấy chữ ký đầu tiên
            log(f"- Phát hiện signature field: {sig.field_name or 'Signature'}")

            # Lấy object chữ ký nội bộ
            sig_obj = getattr(sig, "sig_object", None)
            if sig_obj is None:
                try:
                    sig_obj = sig.get_signature()
                except Exception:
                    sig_obj = None

            # Lấy ByteRange và /Contents
            try:
                low = getattr(sig_obj, "sig_object", sig_obj)
                br = low.get("/ByteRange")
                contents = low.get("/Contents")
                br_list = [int(x) for x in br] if br else None
                log(f"- ByteRange: {br_list if br_list else 'Không có'}")
                clen = len(contents) if contents is not None else "N/A"
                log(f"- /Contents length: {clen} bytes")
            except Exception as e:
                log(f"⚠️ Không đọc được /ByteRange hoặc /Contents: {e}")
                br_list = None

            # Tính lại SHA256
            fh.seek(0)
            pdf_data = fh.read()
            if br_list:
                calc_hash = compute_sha256_range(pdf_data, br_list)
                log(f"- Hash SHA256 theo ByteRange: {calc_hash}")
            else:
                calc_hash = None
                log("- Không tính hash (thiếu ByteRange).")

            # === Gọi validate ===
            log("- Bắt đầu xác thực chữ ký (pyHanko)...")
            # ✅ Dùng chính đối tượng EmbeddedPdfSignature
            status, err = try_validation(sig, trust_ctx)
            if err:
                log(f"⚠️ Lỗi khi gọi validate: {err}")
            if status is None:
                log("❌ Không lấy được kết quả xác thực từ pyHanko.")
                return

            # Chi tiết
            try:
                pretty = status.pretty_print_details()
                log("\n--- Chi tiết validate (pyHanko) ---")
                for line in pretty.splitlines():
                    log("  " + line)
                log("-----------------------------------\n")
            except Exception:
                pass

            # Thông tin chứng thư người ký
            signer_cert = get_first_attr(status, "signer_cert", "signing_cert", "signing_certificate")
            log("Thông tin chứng thư người ký:")
            if signer_cert:
                subj = get_first_attr(signer_cert, "subject")
                readable = getattr(subj, "human_friendly", str(subj))
                fp1 = get_first_attr(signer_cert, "sha1_fingerprint") or get_first_attr(signer_cert, "sha1")
                fp2 = get_first_attr(signer_cert, "sha256_fingerprint") or get_first_attr(signer_cert, "sha256")
                log(f" - Chủ thể: {readable}")
                log(f" - SHA1 Fingerprint: {format_fp(fp1)}")
                log(f" - SHA256 Fingerprint: {format_fp(fp2)}")
            else:
                log(" - ⚠️ Không thể trích xuất chứng thư người ký.")

            # Kiểm tra chain/trust
            trusted = get_first_attr(status, "trusted")
            valid = get_first_attr(status, "valid")
            if trusted is True:
                log("- Chuỗi chứng thư: ✅ Được tin cậy (CA hợp lệ).")
            elif valid:
                log("- Chuỗi chứng thư: ⚠️ Hợp lệ nhưng chưa có CA gốc.")
            else:
                log("- Chuỗi chứng thư: ❌ Không hợp lệ hoặc không xác định.")

            # OCSP/CRL
            rev = get_first_attr(status, "revinfo_validity") or get_first_attr(status, "revinfo_summary")
            if rev:
                log(f"- Trạng thái thu hồi (OCSP/CRL): {rev}")
            else:
                log("- Không có dữ liệu OCSP/CRL.")

            # Thời gian ký
            stime = get_first_attr(status, "signing_time", "signer_reported_dt", "signer_time")
            if stime:
                try:
                    tzvn = timezone(timedelta(hours=7))
                    vn_time = stime.astimezone(tzvn)
                    log(f"- Thời gian ký (UTC): {stime}  → Giờ VN: {vn_time}")
                except Exception:
                    log(f"- Thời gian ký: {stime}")
            else:
                log("- Không tìm thấy timestamp trong chữ ký.")

            # Kiểm tra chỉnh sửa sau khi ký
            mod_level = get_first_attr(status, "modification_level")
            mod_str = str(mod_level)
            if "NONE" in mod_str or mod_level == ModificationLevel.NONE:
                log("- Kiểm tra chỉnh sửa: ✅ Không có thay đổi sau khi ký.")
            elif "FORM_FILLING" in mod_str or mod_level == ModificationLevel.FORM_FILLING:
                log("- Kiểm tra chỉnh sửa: ⚠️ Có điền form sau khi ký.")
            else:
                log("- Kiểm tra chỉnh sửa: ❌ File có thể đã bị thay đổi hoặc không xác định rõ.")

            # Tổng kết
            log("\n=== KẾT LUẬN CHUNG ===")
            if valid:
                log("Kết quả: ✅ CHỮ KÝ HỢP LỆ — FILE NGUYÊN VẸN.")
            else:
                log("Kết quả: ❌ CHỮ KÝ KHÔNG HỢP LỆ HOẶC FILE BỊ CAN THIỆP.")

    except Exception as e:
        log(f"❌ Lỗi xử lý PDF: {e}")

    log(f"\nHoàn tất. Báo cáo lưu tại: {os.path.abspath(LOG_FILE)}")

# =========================================================

if __name__ == "__main__":
    main()
