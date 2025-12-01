import os
from io import BytesIO
from datetime import date as Date

from django.conf import settings
from PIL import Image, ImageDraw, ImageFont, ImageColor

from core.models import Baby, FoodEntry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "static", "core", "fonts")

RESAMPLING = Image.Resampling.LANCZOS

EMOJI_FONT_FILE = "NotoColorEmoji-Regular.ttf"

REACTION_ICON_MAP = {
    "love": "core/img/reactions/love.png",
    "happy": "core/img/reactions/happy.png",
    "neutral": "core/img/reactions/neutral.png",
    "sad": "core/img/reactions/sad.png",
    "gross": "core/img/reactions/gross.png",
}


def abs_static(path: str) -> str | None:
    if not path:
        return None

    candidates: list[str] = []

    static_root = getattr(settings, "STATIC_ROOT", None)
    if static_root:
        candidates.append(os.path.join(static_root, path))

    for directory in getattr(settings, "STATICFILES_DIRS", []):
        candidates.append(os.path.join(directory, path))

    app_static_root = os.path.normpath(os.path.join(FONT_DIR, "..", ".."))
    candidates.append(os.path.join(app_static_root, path))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return candidate

    return None


def resolve_baby_image(baby: Baby) -> str | None:
    if baby.image:
        try:
            return baby.image.path
        except (ValueError, AttributeError):
            pass

    if baby.stock_avatar:
        p = abs_static(baby.stock_avatar)
        if p:
            return p

    return abs_static("core/img/stock-avatars/tomato.png")


def paste_circular_photo(image: Image.Image,
                         circle_bbox: list[float],
                         photo_path: str) -> None:
    try:
        avatar = Image.open(photo_path).convert("RGBA")
    except OSError:
        return

    w, h = avatar.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    avatar = avatar.crop((left, top, left + side, top + side))

    diam = int(circle_bbox[2] - circle_bbox[0])
    avatar = avatar.resize((diam, diam), RESAMPLING)

    r, g, b, a = avatar.split()
    white_bg = Image.new("RGBA", (diam, diam), (255, 255, 255, 255))
    composite = Image.composite(avatar, white_bg, a)
    avatar_flat = composite.convert("RGB")

    mask = Image.new("L", (diam, diam), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, diam, diam), fill=255)

    x0 = int(circle_bbox[0])
    y0 = int(circle_bbox[1])

    image.paste(avatar_flat, (x0, y0), mask)

    bg_r, bg_g, bg_b = (255, 255, 255)
    pixels = image.load()
    W, H = image.size

    cx = (circle_bbox[0] + circle_bbox[2]) / 2.0
    cy = (circle_bbox[1] + circle_bbox[3]) / 2.0
    radius = (circle_bbox[2] - circle_bbox[0]) / 2.0

    clean_margin = 2
    ix0 = max(0, x0 - clean_margin)
    iy0 = max(0, y0 - clean_margin)
    ix1 = min(W - 1, x0 + diam + clean_margin)
    iy1 = min(H - 1, y0 + diam + clean_margin)

    r2 = (radius - 0.5) ** 2

    for y in range(iy0, iy1 + 1):
        for x in range(ix0, ix1 + 1):
            dx = (x + 0.5) - cx
            dy = (y + 0.5) - cy
            if dx * dx + dy * dy > r2:
                pixels[x, y] = (bg_r, bg_g, bg_b)


def load_fonts(base: float):
    styled_path = os.path.join(FONT_DIR, "Grandstander-Bold.ttf")
    emoji_path = os.path.join(FONT_DIR, EMOJI_FONT_FILE)

    title_size = int(base * 2.4)
    user_size = int(base * 1.8)
    meta_size = int(base * 1.0)
    info_size = int(base * 0.8)
    emoji_size = info_size

    title_font = ImageFont.truetype(styled_path, title_size)
    user_font = ImageFont.truetype(styled_path, user_size)
    meta_font = ImageFont.truetype(styled_path, meta_size)
    info_font = ImageFont.truetype(styled_path, info_size)

    try:
        emoji_font = ImageFont.truetype(emoji_path, emoji_size)
    except OSError:
        emoji_font = info_font

    return title_font, user_font, meta_font, info_font, emoji_font


def draw_reaction(image: Image.Image,
                  center_x: int,
                  y: int,
                  reaction: str,
                  emoji_font: ImageFont.FreeTypeFont,
                  info_font: ImageFont.FreeTypeFont) -> None:
    icon_rel = REACTION_ICON_MAP.get(reaction)
    if icon_rel:
        icon_path = abs_static(icon_rel)
        if icon_path and os.path.exists(icon_path):
            try:
                icon = Image.open(icon_path).convert("RGBA")
                size = int(emoji_font.size * 1.25)
                icon.thumbnail((size, size), RESAMPLING)

                x_left = int(center_x - size // 2)

                y_top = int(y - size * 0.20)
                image.paste(icon, (x_left, y_top), icon)
                return
            except OSError:
                pass

    reaction_map = {
        "love": "❤️",
        "happy": "😄",
        "neutral": "😐",
        "sad": "☹️",
        "gross": "🤢",
    }
    emoji_char = reaction_map.get(reaction, "")
    if emoji_char:
        draw = ImageDraw.Draw(image)
        w, h = draw.textbbox((0, 0), emoji_char, font=emoji_font)[2:]
        x_left = int(center_x - w // 2)
        draw.text((x_left, y), emoji_char, fill=ImageColor.getrgb("#000000"),
                  font=emoji_font)


def generate_report_image(baby: Baby, report_date: Date) -> bytes:
    W, H = 1200, 1552
    base = W / 30

    pad = int(base * 2.0)
    line_gap = int(base * 1.3)
    section_gap = int(base * 0.7)
    underline_gap = int(base * 0.2)

    bg_color = ImageColor.getrgb("#FFFFFF")
    color = ImageColor.getrgb("#000000")

    image = Image.new("RGB", (W, H), bg_color)
    draw = ImageDraw.Draw(image)

    title_font, user_font, meta_font, info_font, emoji_font = load_fonts(base)

    title_text = "BabyBites Daily Report"
    t_x0, t_y0, t_x1, t_y1 = draw.textbbox((0, 0), title_text, font=title_font)
    t_w, t_h = t_x1 - t_x0, t_y1 - t_y0
    draw.text(((W - t_w) / 2, pad), title_text, fill=color, font=title_font)

    date_str = report_date.strftime("%B %d, %Y")
    d_x0, d_y0, d_x1, d_y1 = draw.textbbox((0, 0), date_str, font=meta_font)
    d_w, d_h = d_x1 - d_x0, d_y1 - d_y0
    date_y = pad + t_h + int(base * 0.5)
    draw.text(((W - d_w) / 2, date_y), date_str, fill=color, font=meta_font)

    circle_radius = int(base * 2.2)
    cx = W / 2
    cy = date_y + d_h + int(base * 2.5)
    circle_bbox = [cx - circle_radius, cy - circle_radius,
                   cx + circle_radius, cy + circle_radius]

    avatar_path = resolve_baby_image(baby)
    if avatar_path:
        paste_circular_photo(image, circle_bbox, avatar_path)

    draw.ellipse(circle_bbox, outline=color, width=4)

    baby_line = baby.name
    b_x0, b_y0, b_x1, b_y1 = draw.textbbox((0, 0), baby_line, font=user_font)
    b_w, b_h = b_x1 - b_x0, b_y1 - b_y0
    name_y = circle_bbox[3] + int(base * 0.8)
    draw.text(((W - b_w) / 2, name_y), baby_line, fill=color, font=user_font)

    current_y = name_y + b_h + int(base * 1.8)
    left_x = pad + int(base * 0.5)
    right_x = W - pad - int(base * 4.5)

    day_entries = (
        FoodEntry.objects
        .filter(baby=baby, date=report_date)
        .select_related("food")
        .order_by("id")
    )

    feeding_heading = "Daily Feeding"
    f_x0, f_y0, f_x1, f_y1 = draw.textbbox((0, 0), feeding_heading, font=meta_font)
    f_w = f_x1 - f_x0
    draw.text((left_x, current_y), feeding_heading, fill=color, font=meta_font)
    draw.line(
        (left_x, current_y + (f_y1 - f_y0) + underline_gap,
         left_x + f_w, current_y + (f_y1 - f_y0) + underline_gap),
        fill=color,
        width=2,
    )

    reactions_heading = "Reactions"
    r_x0, r_y0, r_x1, r_y1 = draw.textbbox((0, 0), reactions_heading, font=meta_font)
    r_w = r_x1 - r_x0
    draw.text((right_x, current_y), reactions_heading, fill=color, font=meta_font)
    draw.line(
        (right_x, current_y + (r_y1 - r_y0) + underline_gap,
         right_x + r_w, current_y + (r_y1 - r_y0) + underline_gap),
        fill=color,
        width=2,
    )

    reactions_center_x = right_x + (r_w // 2)

    current_y += (f_y1 - f_y0) + underline_gap + section_gap

    if day_entries.exists():
        for entry in day_entries:
            food_name = getattr(entry.food, "name", str(entry.food))
            amt = entry.portion_size
            unit = entry.portion_unit or ""
            text = f"{amt:g} {unit} {food_name}".strip()
            draw.text((left_x, current_y), text, fill=color, font=info_font)

            draw_reaction(
                image,
                reactions_center_x,
                current_y,
                (entry.reaction or "").lower(),
                emoji_font,
                info_font,
            )

            current_y += line_gap
    else:
        draw.text((left_x, current_y),
                  "No entries logged for this date.",
                  fill=color, font=info_font)
        current_y += line_gap

    current_y += section_gap * 2

    total_heading = "Total feeding:"
    t2_x0, t2_y0, t2_x1, t2_y1 = draw.textbbox((0, 0), total_heading, font=meta_font)
    t2_w = t2_x1 - t2_x0
    draw.text((left_x, current_y), total_heading, fill=color, font=meta_font)
    draw.line(
        (left_x, current_y + (t2_y1 - t2_y0) + underline_gap,
         left_x + t2_w, current_y + (t2_y1 - t2_y0) + underline_gap),
        fill=color,
        width=2,
    )
    current_y += (t2_y1 - t2_y0) + underline_gap + section_gap

    if day_entries.exists():
        totals: dict[tuple[str, str], float] = {}
        for entry in day_entries:
            name = getattr(entry.food, "name", str(entry.food))
            unit = entry.portion_unit or ""
            key = (name, unit)
            totals[key] = totals.get(key, 0.0) + (entry.portion_size or 0.0)

        for (name, unit), amt in sorted(totals.items()):
            line = f"{amt:g} {unit} {name}".strip()
            draw.text((left_x, current_y), line, fill=color, font=info_font)
            current_y += line_gap
    else:
        draw.text((left_x, current_y),
                  "No feeding totals for this date.",
                  fill=color, font=info_font)
        current_y += line_gap

    current_y += section_gap * 2

    milestones_heading = "Milestones"
    m_x0, m_y0, m_x1, m_y1 = draw.textbbox((0, 0), milestones_heading, font=meta_font)
    m_w = m_x1 - m_x0
    draw.text((left_x, current_y), milestones_heading, fill=color, font=meta_font)
    draw.line(
        (left_x, current_y + (m_y1 - m_y0) + underline_gap,
         left_x + m_w, current_y + (m_y1 - m_y0) + underline_gap),
        fill=color,
        width=2,
    )
    current_y += (m_y1 - m_y0) + underline_gap + section_gap

    milestone_foods = set()
    for entry in day_entries:
        prior = FoodEntry.objects.filter(
            baby=baby,
            food=entry.food,
            date__lt=report_date,
        ).exists()
        if not prior:
            milestone_foods.add(entry.food.name)

    if milestone_foods:
        for name in sorted(milestone_foods):
            draw.text((left_x, current_y),
                      f"• First time trying {name}!",
                      fill=color, font=info_font)
            current_y += line_gap
    else:
        draw.text((left_x, current_y),
                  "No milestones achieved for this date.",
                  fill=color, font=info_font)
        current_y += line_gap

    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()
