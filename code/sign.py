# ==========================================
# sign_pdf_footer_clean.py - PyHanko 0.31.0 (Windows)
# Làm sạch PDF hybrid xref + ký PDF với Footer chữ ký + ảnh + metadata
# ==========================================
from datetime import datetime
from pyhanko.sign import signers, fields
from pyhanko.stamp.text import TextStampStyle
from pyhanko.pdf_utils import images
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.pdf_utils.layout import SimpleBoxLayoutRule, AxisAlignment, Margins
from pyhanko.sign.general import load_cert_from_pemder
from pyhanko_certvalidator import ValidationContext
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign.fields import SigFieldSpec
from pypdf import PdfReader, PdfWriter  # Dùng để làm sạch PDF hybrid

import os

# === ĐƯỜNG DẪN Windows ===
PDF_ORIG = r"D:\LHV_BMTT_BT2\pdf\Original.pdf"
PDF_CLEAN = r"D:\LHV_BMTT_BT2\pdf\Original_clean.pdf"
PDF_OUT = r"D:\LHV_BMTT_BT2\pdf\signed.pdf"
KEY_FILE = r"D:\LHV_BMTT_BT2\key\private.pem"
CERT_FILE = r"D:\LHV_BMTT_BT2\key\certificate.pem"
SIG_IMG = r"D:\LHV_BMTT_BT2\chuky\chuky.png"

# === Bước 1: Làm sạch file PDF gốc (loại bỏ hybrid xref) ===
print("🧹 Đang chuyển đổi PDF sang dạng non-hybrid...")

reader = PdfReader(PDF_ORIG)
writer_clean = PdfWriter()
for page in reader.pages:
    writer_clean.add_page(page)

with open(PDF_CLEAN, "wb") as f:
    writer_clean.write(f)

print("✅ Đã tạo file sạch:", PDF_CLEAN)

# === Bước 2: Tạo signer & validation context ===
signer = signers.SimpleSigner.load(KEY_FILE, CERT_FILE, key_passphrase=None)
vc = ValidationContext(trust_roots=[load_cert_from_pemder(CERT_FILE)])

# === Bước 3: Mở PDF sạch và ký ===
with open(PDF_CLEAN, "rb") as inf:
    writer = IncrementalPdfFileWriter(inf)

    # Lấy trang cuối cùng
    pages = writer.root["/Pages"]
    num_pages = pages.get("/Count", len(pages.get("/Kids", [])))
    target_page = num_pages - 1  # index trang cuối

    # Thêm field chữ ký ở footer trang cuối
    fields.append_signature_field(
        writer,
        SigFieldSpec(
            sig_field_name="FooterSig",
            box=(50, 30, 550, 100),  # vị trí footer
            on_page=target_page
        )
    )

    # Ảnh chữ ký tay
    background_img = images.PdfImage(SIG_IMG)

    # Layout ảnh & text
    bg_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MIN,
        y_align=AxisAlignment.ALIGN_MID,
        margins=Margins(right=20)
    )
    text_layout = SimpleBoxLayoutRule(
        x_align=AxisAlignment.ALIGN_MIN,
        y_align=AxisAlignment.ALIGN_MID,
        margins=Margins(left=150)
    )

    # Style chữ ký text
    text_style = TextBoxStyle(font_size=13)
    ngay_ky = datetime.now().strftime("%d/%m/%Y")
    stamp_text = (
        "LUONG HOANG VIET"
        "\nSDT: 0385579617"
        "\nMSSV: K225480106073"
        f"\nNgày ký: {ngay_ky}"
    )

    stamp_style = TextStampStyle(
        stamp_text=stamp_text,
        background=background_img,
        background_layout=bg_layout,
        inner_content_layout=text_layout,
        text_box_style=text_style,
        border_width=1,
        background_opacity=1.0,
    )

    # Metadata chữ ký
    meta = signers.PdfSignatureMetadata(
        field_name="FooterSig",
        reason="Digital signature",
        location="TNUT-Thái Nguyên",
        md_algorithm="sha256",
    )

    # PdfSigner
    pdf_signer = signers.PdfSigner(
        signature_meta=meta,
        signer=signer,
        stamp_style=stamp_style
    )

    # Ký và lưu
    with open(PDF_OUT, "wb") as outf:
        pdf_signer.sign_pdf(writer, output=outf)

print("✅ PDF đã ký thành công với Footer ở trang cuối!")
print("📄 File lưu tại:", PDF_OUT)
