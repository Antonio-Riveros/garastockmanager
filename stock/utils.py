import random
import string
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_unique_numeric_part(length=11):
    return ''.join(random.choices(string.digits, k=length))

def generate_qr_code(data, filename=None):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    if not filename:
        safe_data = "".join(c if c.isalnum() else "_" for c in data)
        filename = f"qr_{safe_data}.png"
    return ContentFile(buffer.getvalue(), filename)