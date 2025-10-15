import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import os

from core.models import Baby, FoodEntry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "static", "core", "fonts")

def count_profiles(username: str) -> int:
    return (
        Baby.objects.filter(owner__username=username).count()
    )

def count_entries(username: str) -> int:
    return (
        FoodEntry.objects.filter(baby__owner__username=username).count()
    )

def load_fonts():
    styled_path = os.path.join(FONT_DIR, "Grandstander-Bold.ttf")
    styled_font = ImageFont.truetype(styled_path, 72)
    user_font = ImageFont.truetype(styled_path, 48)
    meta_font = ImageFont.truetype(styled_path, 32)
    return styled_font, user_font, meta_font


def generate_report_image(username: str) -> bytes:
    W, H = 630, 815
    bg_color = ImageColor.getrgb("#FFFFFF")
    color = ImageColor.getrgb("#000000")

    image = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(image)

    title_font, user_font, meta_font = load_fonts()

    title = "DAILY REPORT"
    tw, th = draw.textbbox((0, 0), title, font=title_font)[2:]
    draw.text(((W - tw) / 2, 50), title, fill=color, font=title_font)

    timestamp = now().strftime("%Y-%m-%d %H:%M:%S %Z")
    meta = f"AS OF {timestamp}"
    mw, mh = draw.textbbox((0, 0), meta, font=meta_font)[2:]
    draw.text(((W - mw) / 2, 125), meta, fill=color, font=meta_font)

    username_string = f"{username}"
    max_width = int(W * 0.85)
    usw, ush = draw.textbbox((0, 0), username_string, font=user_font)[2:]
    draw.text(((W - usw) / 2, 300), username_string, fill=color, font=user_font)

    profiles = count_profiles(username)
    profiles_str = f"number of profiles: {str(profiles)}"
    pw, ph = draw.textbbox((0, 0), profiles_str, font=meta_font)[2:]
    draw.text(((W - pw) / 2, 450), profiles_str, fill=color, font=meta_font)

    entries = count_entries(username)
    entries_str = f"number of entries: {str(entries)}"
    ew, eh = draw.textbbox((0, 0), entries_str, font=meta_font)[2:]
    draw.text(((W - ew) / 2, 500), entries_str, fill=color, font=meta_font)

    pad = 24
    draw.rectangle([pad, pad, W - pad, H - pad], outline=color, width=2)

    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()