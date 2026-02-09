import random
import string
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_unique_numeric_part(length=11):
    """
    Generates a random numeric string of a given length.
    Ensures it is not sequential basically by randomness.
    Collision check should be done at the model level or usage level.
    """
    return ''.join(random.choices(string.digits, k=length))

def generate_qr_code(data, filename=None):
    """
    Generates a QR code image from the given data string.
    Returns a ContentFile that can be saved to an ImageField.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    if not filename:
        # Sanitize data to be safe for filename
        safe_data = "".join(c if c.isalnum() else "_" for c in data)
        filename = f"qr_{safe_data}.png"
    
    return ContentFile(buffer.getvalue(), filename)
