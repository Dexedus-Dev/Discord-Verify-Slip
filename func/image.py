import base64
import io
import mimetypes
from PIL import Image
from pyzbar.pyzbar import decode

def read_qrcode(path: str):
    img = Image.open(path)
    decoded_objects = decode(img)
    return [obj.data.decode("utf-8") for obj in decoded_objects]

def image_to_data_uri(path: str) -> str:
    img = Image.open(path)
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/png"
    fmt = img.format if img.format else "PNG"
    buffered = io.BytesIO()
    img.save(buffered, format=fmt)
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{img_base64}"

def bytes_to_data_uri(img_bytes: bytes, content_type: str = "image/png") -> str:
    img = Image.open(io.BytesIO(img_bytes))
    buffered = io.BytesIO()
    img.save(buffered, format=img.format if img.format else "PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:{content_type};base64,{img_base64}"

def bytes_read_qrcode(img_bytes: bytes, content_type: str = "image/png"):
    img = Image.open(io.BytesIO(img_bytes))
    decoded_objects = decode(img)
    return [obj.data.decode("utf-8") for obj in decoded_objects]