from datetime import datetime as dt
from datetime import timedelta
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import os


def generator():
    now = dt.now()

    yesterday_end_lie = (now - timedelta(days=1)).replace(
        hour=23, minute=59, second=59, microsecond=999
    )

    font_url = "fonts/ARIAL.TTF"

    label = yesterday_end_lie.strftime("%H:%M  %d.%m.%Y")

    font = ImageFont.truetype(font_url, 52)
    font_1 = ImageFont.truetype(font_url, 68)

    directory = "var/log/tg_bot"
    filename = "fire.png"
    filename_result = "daily_report.png"

    file_path = os.path.join(os.getcwd(), directory, filename)
    img = Image.open(file_path)

    I1 = ImageDraw.Draw(img)

    I1.text(
        (350, 50),
        text="Лесные пожары",
        fill=(0, 0, 0),
        font=font_1,
        embedded_color=True,
    )
    I1.text((400, 160), label, fill=(0, 0, 0), font=font, embedded_color=True)

    result_file_path = os.path.join(os.getcwd(), directory, filename_result)
    img.save(result_file_path)

    return result_file_path
