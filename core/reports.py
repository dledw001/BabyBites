import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageColor
from datetime import date as Date
from django.utils.timezone import now
import os
from django.db.models import Sum

from core.models import Baby, FoodEntry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "static", "core", "fonts")

def load_fonts():
    styled_path = os.path.join(FONT_DIR, "Grandstander-Bold.ttf")
    styled_font = ImageFont.truetype(styled_path, 72)
    user_font = ImageFont.truetype(styled_path, 48)
    meta_font = ImageFont.truetype(styled_path, 32)
    info_font = ImageFont.truetype(styled_path, 16)
    return styled_font, user_font, meta_font, info_font

def count_entries_for_day(baby: Baby, report_date: Date) -> int:
    return FoodEntry.objects.filter(baby=baby, date=report_date).count()

def sum_portion_size_for_day(baby: Baby, report_date: Date) -> float:
    agg = (
        FoodEntry.objects
        .filter(baby=baby, date=report_date)
        .aggregate(sum=Sum("portion_size"))
    )["sum"]
    return agg or 0.0

def generate_report_image(baby: Baby, report_date: Date) -> bytes:
    W, H = 630, 815
    bg_color = ImageColor.getrgb("#FFFFFF")
    color = ImageColor.getrgb("#000000")

    image = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(image)

    title_font, user_font, meta_font, info_font = load_fonts()

    # Baby name
    baby_line = baby.name
    bw, bh = draw.textbbox((0, 0), baby_line, font=user_font)[2:]
    draw.text(((W - bw) / 2, 40), baby_line, fill=color, font=user_font)

    # Date
    date_str = report_date.strftime("%B %d, %Y")
    meta_date = f"{date_str}"
    mw, mh = draw.textbbox((0, 0), meta_date, font=meta_font)[2:]
    draw.text(((W - mw) / 2, 100), meta_date, fill=color, font=meta_font)

    # Layout helpers
    left_x = 40
    line_gap = 26
    section_gap = 14
    current_y = 150

    # Daily feeding log
    draw.text((left_x, current_y), "Daily feeding log", fill=color, font=meta_font)
    current_y += meta_font.size + section_gap

    day_entries = (
        FoodEntry.objects
        .filter(baby=baby, date=report_date)
        .select_related("food")
        .order_by("id")
    )

    if day_entries.exists():
        for entry in day_entries:
            food_name = getattr(entry.food, "name", str(entry.food))
            portion = entry.portion_size
            line = f"• {food_name} — {portion:g}"
            draw.text((left_x, current_y), line, fill=color, font=info_font)
            current_y += line_gap
    else:
        draw.text(
            (left_x, current_y),
            "No entries logged for this date.",
            fill=color,
            font=info_font,
        )
        current_y += line_gap

    current_y += section_gap

    #Daily totals
    total_mass = sum_portion_size_for_day(baby, report_date)
    mass_str = f"Total portion size: {total_mass:.1f}"
    draw.text((left_x, current_y), mass_str, fill=color, font=info_font)
    current_y += line_gap + section_gap

    #Report milestones
    # First time foods
    draw.text((left_x, current_y), "Milestones", fill=color, font=meta_font)
    current_y += meta_font.size + section_gap

    milestone_foods = set()
    for entry in day_entries:
        food = entry.food
        has_prior = FoodEntry.objects.filter(
            baby=baby,
            food=food,
            date__lt=report_date,
        ).exists()
        if not has_prior:
            milestone_foods.add(getattr(food, "name", str(food)))

    if milestone_foods:
        for name in sorted(milestone_foods):
            line = f"• First time trying {name}"
            draw.text((left_x, current_y), line, fill=color, font=info_font)
            current_y += line_gap
    else:
        draw.text(
            (left_x, current_y),
            "No new foods first tried on this date.",
            fill=color,
            font=info_font,
        )
        current_y += line_gap

    # timestamp
    ts = now().strftime("%Y-%m-%d %H:%M:%S %Z")
    gen_str = f"Report generated: {ts}"
    gw, gh = draw.textbbox((0, 0), gen_str, font=info_font)[2:]
    draw.text(((W - gw) / 2, H - 45), gen_str, fill=color, font=info_font)

    # border
    pad = 24
    draw.rectangle([pad, pad, W - pad, H - pad], outline=color, width=2)

    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()