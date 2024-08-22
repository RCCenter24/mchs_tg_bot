from datetime import datetime as dt
from datetime import timedelta
import tempfile
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from icecream import ic

def generator():
    now = dt.now()

    yesterday_end_lie = (now - timedelta(days=1)).replace(
        hour=23, minute=59, second=59, microsecond=999
    )

    label = yesterday_end_lie.strftime("%H:%M  %d.%m.%Y")

    font = ImageFont.truetype("Arial", 52)
    font_1 = ImageFont.truetype("Arial", 68)
    img = Image.open("fire.png")

    I1 = ImageDraw.Draw(img)

    I1.text(
        (350, 50),
        text="Лесные пожары",
        fill=(0, 0, 0),
        font=font_1,
        embedded_color=True,
    )
    I1.text((400, 160), label, fill=(0, 0, 0), font=font, embedded_color=True)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False, delete_on_close=True) as temp_file:
        img.save(temp_file, format='PNG')
        temp_file_path = temp_file.name
        
    
    return temp_file_path
