"""Open Graph image generation service using Pillow.

Generates 1200x630 PNG images for WhatsApp link previews.
"""

import io
import os

from PIL import Image, ImageDraw, ImageFont

# Image dimensions for OG images
OG_WIDTH = 1200
OG_HEIGHT = 630

# Colors
BG_COLOR = "#0A0A0A"
GOLD = "#D4AF37"
WHITE = "#FFFFFF"
GRAY = "#888888"

# Font paths - try several common locations, fall back to default
_FONT_SEARCH_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
]

_FONT_REGULAR_PATHS = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _find_font(paths: list[str]) -> str | None:
    """Return the first font path that exists on disk."""
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a TrueType font at the given size, falling back to default."""
    search = _FONT_SEARCH_PATHS if bold else _FONT_REGULAR_PATHS
    font_path = _find_font(search)
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except (OSError, IOError):
            pass
    # Fallback: Pillow's built-in default font (scaled via size arg in newer Pillow)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines: list[str] = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines or [text]


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    font,
    x: int,
    y: int,
    fill: str,
    max_width: int,
    line_spacing: int = 8,
) -> int:
    """Draw word-wrapped text, returning the y position after the last line."""
    lines = _wrap_text(draw, text, font, max_width)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def generate_anti_vote_image(
    region: str,
    rejected: str,
    recommended: str,
) -> bytes:
    """Generate an OG image for anti-vote sharing.

    Args:
        region: Region name (e.g. "Lima").
        rejected: Rejected party/candidate name.
        recommended: Recommended party/candidate name.

    Returns:
        PNG image bytes.
    """
    img = Image.new("RGB", (OG_WIDTH, OG_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    pad_x = 80
    max_w = OG_WIDTH - pad_x * 2

    # Logo text
    font_logo = _load_font(42, bold=True)
    draw.text((pad_x, 45), "VotoClaro", font=font_logo, fill=GOLD)

    # Peru flag emoji - render as text (may show as box on systems without emoji font)
    font_flag = _load_font(36)
    flag_text = "\U0001f1f5\U0001f1ea"  # 🇵🇪
    bbox_logo = draw.textbbox((pad_x, 45), "VotoClaro", font=font_logo)
    draw.text((bbox_logo[2] + 16, 50), flag_text, font=font_flag, fill=WHITE)

    # Subtitle: "En {region}, para frenar a {rejected}:"
    font_sub = _load_font(34)
    subtitle = f"En {region}, para frenar a {rejected}:"
    y = 140
    y = _draw_wrapped(draw, subtitle, font_sub, pad_x, y, WHITE, max_w)

    # Main text: "Vota por {recommended}"
    font_main = _load_font(64, bold=True)
    main_text = f"Vota por {recommended}"
    y += 20
    y = _draw_wrapped(draw, main_text, font_main, pad_x, y, GOLD, max_w)

    # Bottom tagline
    font_bottom = _load_font(26)
    tagline = "Simula tu voto en votaclaro.com"
    bbox_tag = draw.textbbox((0, 0), tagline, font=font_bottom)
    tag_w = bbox_tag[2] - bbox_tag[0]
    draw.text(
        ((OG_WIDTH - tag_w) // 2, OG_HEIGHT - 70),
        tagline,
        font=font_bottom,
        fill=GRAY,
    )

    # Decorative line under logo
    draw.line([(pad_x, 105), (OG_WIDTH - pad_x, 105)], fill=GOLD, width=2)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_quiz_image(
    match: str,
    percent: float,
) -> bytes:
    """Generate an OG image for quiz result sharing.

    Args:
        match: Name of the matching party/candidate.
        percent: Match percentage.

    Returns:
        PNG image bytes.
    """
    img = Image.new("RGB", (OG_WIDTH, OG_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    pad_x = 80
    max_w = OG_WIDTH - pad_x * 2

    # Logo text
    font_logo = _load_font(42, bold=True)
    draw.text((pad_x, 45), "VotoClaro", font=font_logo, fill=GOLD)

    # Decorative line under logo
    draw.line([(pad_x, 105), (OG_WIDTH - pad_x, 105)], fill=GOLD, width=2)

    # "Mi resultado en VotoClaro"
    font_heading = _load_font(36)
    draw.text((pad_x, 140), "Mi resultado en VotoClaro", font=font_heading, fill=WHITE)

    # "Coincido {percent}% con {match}"
    font_main = _load_font(56, bold=True)
    pct_display = int(percent) if percent == int(percent) else percent
    main_text = f"Coincido {pct_display}% con {match}"
    y = 220
    y = _draw_wrapped(draw, main_text, font_main, pad_x, y, GOLD, max_w)

    # Bottom CTA
    font_bottom = _load_font(26)
    cta = "\u00bfCon qui\u00e9n coincides t\u00fa? \u2192 votaclaro.com/quiz"
    bbox_cta = draw.textbbox((0, 0), cta, font=font_bottom)
    cta_w = bbox_cta[2] - bbox_cta[0]
    draw.text(
        ((OG_WIDTH - cta_w) // 2, OG_HEIGHT - 70),
        cta,
        font=font_bottom,
        fill=GRAY,
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
