"""Content generator for InstaNote - renders the vehicle infographic images (Pillow)."""

import logging
import os
import re
import textwrap
import time
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.config import get_config, project_path

logger = logging.getLogger(__name__)

BASE_W, BASE_H = 1080, 1350  # we always draw at this size and resize at the end if needed
MARGIN = 60

# --------------------------------------------------------------------------- fonts

FONT_CANDIDATES = {
    "regular": [
        "assets/fonts/regular.ttf",
        r"C:\Windows\Fonts\segoeui.ttf", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
    ],
    "bold": [
        "assets/fonts/bold.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\calibrib.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
    ],
    "hand": [
        "assets/fonts/hand.ttf",
        r"C:\Windows\Fonts\Inkfree.ttf", r"C:\Windows\Fonts\segoepr.ttf", r"C:\Windows\Fonts\comic.ttf",
        "/usr/share/fonts/truetype/comic-neue/ComicNeue-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Chalkboard.ttc", "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
    ],
}


@lru_cache(maxsize=128)
def find_font(size: int, kind: str = "regular"):
    """Find a TrueType font for ``kind`` ('regular' | 'bold' | 'hand'); falls back gracefully."""
    candidates = FONT_CANDIDATES.get(kind, []) + FONT_CANDIDATES["bold" if kind == "hand" else "regular"]
    for path in candidates:
        full = project_path(path) if not os.path.isabs(path) else Path(path)
        if full.exists():
            try:
                return ImageFont.truetype(str(full), size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size)  # Pillow >= 10.1 returns a scalable font
    except TypeError:  # very old Pillow
        return ImageFont.load_default()


# --------------------------------------------------------------------------- themes

THEMES = {
    "aesthetic": dict(bg=(250, 245, 233), card=(255, 253, 247), ink=(40, 40, 48), muted=(120, 112, 98), accent=(13, 148, 136),
                      accent2=(245, 158, 11), line=(228, 218, 196), pattern="lines", hand=True, margin_line=False),
    "notebook": dict(bg=(253, 253, 250), card=(255, 255, 255), ink=(30, 41, 59), muted=(100, 116, 139), accent=(37, 99, 235),
                     accent2=(220, 38, 38), line=(191, 219, 254), pattern="lines", hand=True, margin_line=True),
    "colorful": dict(bg=(255, 247, 214), card=(255, 255, 255), ink=(49, 30, 80), muted=(120, 100, 150), accent=(219, 39, 119),
                     accent2=(124, 58, 237), line=(253, 224, 138), pattern="dots", hand=True, margin_line=False),
    "realistic3d": dict(bg=(15, 23, 42), card=(30, 41, 59), ink=(241, 245, 249), muted=(148, 163, 184), accent=(251, 146, 60),
                        accent2=(56, 189, 248), line=(51, 65, 85), pattern="none", hand=False, margin_line=False),
    "technical": dict(bg=(12, 38, 74), card=(18, 52, 98), ink=(224, 242, 254), muted=(125, 170, 220), accent=(56, 189, 248),
                      accent2=(250, 204, 21), line=(30, 70, 120), pattern="grid", hand=False, margin_line=False),
    "doodle": dict(bg=(228, 250, 240), card=(255, 255, 255), ink=(30, 58, 52), muted=(90, 130, 120), accent=(244, 114, 82),
                   accent2=(99, 102, 241), line=(186, 230, 213), pattern="dots", hand=True, margin_line=False),
    "premium": dict(bg=(14, 14, 16), card=(28, 28, 32), ink=(245, 240, 228), muted=(160, 150, 130), accent=(212, 175, 55),
                    accent2=(240, 220, 150), line=(50, 48, 44), pattern="none", hand=False, margin_line=False),
    "kraft": dict(bg=(226, 205, 170), card=(244, 232, 208), ink=(60, 42, 26), muted=(120, 96, 68), accent=(150, 60, 40),
                  accent2=(60, 100, 70), line=(206, 184, 148), pattern="lines", hand=True, margin_line=False),
}

STYLE_TO_THEME = [
    ("aesthetic", "aesthetic"), ("notebook photography", "kraft"), ("handwritten notebook", "notebook"),
    ("colorful", "colorful"), ("3d", "realistic3d"), ("technical", "technical"),
    ("doodle", "doodle"), ("premium", "premium"), ("kraft", "kraft"),
]


def theme_for_style(style: Optional[str]) -> Tuple[str, dict]:
    lower = (style or "").lower()
    for needle, name in STYLE_TO_THEME:
        if needle in lower:
            return name, THEMES[name]
    return "aesthetic", THEMES["aesthetic"]


COLOR_WORDS = {
    "red": (220, 38, 38), "rosso": (204, 0, 0), "blue": (37, 99, 235), "blu": (30, 64, 175), "black": (30, 30, 34),
    "nero": (20, 20, 22), "white": (245, 245, 245), "bianco": (240, 240, 240), "silver": (176, 184, 192),
    "grey": (120, 128, 136), "gray": (120, 128, 136), "yellow": (250, 204, 21), "giallo": (250, 204, 21),
    "green": (34, 160, 90), "verde": (34, 160, 90), "orange": (249, 115, 22), "arancio": (249, 115, 22),
    "purple": (126, 34, 206), "brown": (120, 72, 40), "gold": (212, 175, 55), "halcyon": (60, 110, 100),
    "chrome": (190, 195, 200),
}


def color_for_name(name: str) -> Optional[Tuple[int, int, int]]:
    lower = name.lower()
    for word, rgb in COLOR_WORDS.items():
        if word in lower:
            return rgb
    return None


# --------------------------------------------------------------------------- helpers

def _has(value) -> bool:
    return bool(value) and str(value).strip().upper() not in ("N/A", "", "NONE", "CONTACT DEALER", "SEE SPECIFICATIONS")


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> List[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _clamp_lines(draw, lines: List[str], font, max_width: int, max_lines: int) -> List[str]:
    if len(lines) <= max_lines:
        return lines
    kept = lines[:max_lines]
    last = kept[-1]
    while last and draw.textlength(last + "…", font=font) > max_width:
        last = last[:-1]
    kept[-1] = last.rstrip(" ,.;") + "…"
    return kept


def _fit_font(draw, text: str, max_width: int, start: int, minimum: int, kind: str):
    size = start
    while size > minimum:
        font = find_font(size, kind)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return find_font(minimum, kind)


def _shade(rgb, delta: int):
    return tuple(max(0, min(255, c + delta)) for c in rgb)


def _is_bike(specs: Dict, category: str = "") -> bool:
    text = f"{category} {specs.get('name', '')}".lower()
    words = ("bike", "motorcycle", "scooter", "superbike", "ninja", "panigale", "s1000", "enfield", "yamaha r",
             "ducati", "kawasaki", "hayabusa", "vespa", "nmax", "harley", "livewire", "ather", "ola s1", "triumph", "zero sr")
    return any(w in text for w in words) and "bikes and" not in "" and not any(w in text for w in ("bikes and car",))


# --------------------------------------------------------------------------- generator

@dataclass
class GenerationResult:
    image_path: str
    style_used: str
    generation_time: float
    width: int = BASE_W
    height: int = BASE_H
    extra_paths: Optional[List[str]] = None


class InfographicGenerator:
    """Draws the infographic slides."""

    def __init__(self, width: int = BASE_W, height: int = BASE_H, style: Optional[str] = None):
        self.width = width
        self.height = height
        self.style = style
        self.theme_name, self.t = theme_for_style(style)

    # ---- public API -------------------------------------------------------

    def generate(self, topic, specs: Dict, style: Optional[str] = None, output_dir: Optional[Path] = None) -> GenerationResult:
        """Render one infographic for ``topic`` and save it in ``output/``."""
        start = time.time()
        cfg = get_config().image
        style = style or cfg.default_style
        self.style = style
        self.theme_name, self.t = theme_for_style(style)
        self.width, self.height = cfg.width or BASE_W, cfg.height or BASE_H

        category = getattr(topic, "category_key", "") or ""
        specs = dict(specs)
        specs.setdefault("name", getattr(topic, "vehicle_name", "Vehicle"))
        img = self.create_image(specs, category)

        out_dir = Path(output_dir) if output_dir else project_path("output")
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = re.sub(r"[^a-z0-9]+", "-", specs["name"].lower()).strip("-") or "vehicle"
        path = out_dir / f"{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
        img.save(path, format="PNG", optimize=True)
        return GenerationResult(str(path), style, round(time.time() - start, 2), img.width, img.height)

    def generate_caption(self, topic, specs: Dict) -> Tuple[str, List[str]]:
        from src.researcher import generate_caption, generate_hashtags
        return generate_caption(specs), generate_hashtags(specs)

    def create_image(self, specs: Dict, category: str = "") -> Image.Image:
        """Create the main infographic (drawn at 1080x1350, resized when another size is configured)."""
        img = Image.new("RGB", (BASE_W, BASE_H), self.t["bg"])
        draw = ImageDraw.Draw(img)
        self._background(draw)
        y = self._header(draw, specs, category)
        y = self._illustration(draw, specs, category, y)
        y = self._spec_cards(draw, specs, y)
        self._about_and_features(draw, specs, y)
        self._footer(draw, specs)
        if (self.width, self.height) != (BASE_W, BASE_H):
            img = img.resize((self.width, self.height), Image.LANCZOS)
        return img

    def create_detail_slide(self, specs: Dict) -> Image.Image:
        """Second slide: every spec we know in a clean table."""
        img = Image.new("RGB", (BASE_W, BASE_H), self.t["bg"])
        draw = ImageDraw.Draw(img)
        self._background(draw)
        font = _fit_font(draw, "Technical Specifications", BASE_W - 2 * MARGIN, 64, 36, "hand" if self.t["hand"] else "bold")
        draw.text((BASE_W // 2, 70), "Technical Specifications", font=font, fill=self.t["ink"], anchor="mt")
        draw.text((BASE_W // 2, 150), specs.get("name", ""), font=find_font(32, "bold"), fill=self.t["accent"], anchor="mt")
        rows = self._spec_rows(specs, limit=40)
        y = 230
        for i, (label, value) in enumerate(rows):
            if y > BASE_H - 160:
                break
            fill = self.t["card"] if i % 2 == 0 else self.t["bg"]
            draw.rounded_rectangle([MARGIN, y, BASE_W - MARGIN, y + 62], 12, fill=fill)
            draw.text((MARGIN + 24, y + 31), label.upper(), font=find_font(22, "bold"), fill=self.t["muted"], anchor="lm")
            lines = _clamp_lines(draw, _wrap(draw, value, find_font(28, "bold"), 560), find_font(28, "bold"), 560, 1)
            draw.text((BASE_W - MARGIN - 24, y + 31), lines[0] if lines else "", font=find_font(28, "bold"),
                      fill=self.t["ink"], anchor="rm")
            y += 70
        self._footer(draw, specs)
        if (self.width, self.height) != (BASE_W, BASE_H):
            img = img.resize((self.width, self.height), Image.LANCZOS)
        return img

    def generate_multiple_slides(self, specs: Dict, category: str = "") -> List[Image.Image]:
        return [self.create_image(specs, category), self.create_detail_slide(specs)]

    # ---- drawing blocks ---------------------------------------------------

    def _background(self, draw):
        t = self.t
        if t["pattern"] == "lines":
            for y in range(150, BASE_H, 44):
                draw.line([(0, y), (BASE_W, y)], fill=t["line"], width=1)
        elif t["pattern"] == "grid":
            for x in range(0, BASE_W, 54):
                draw.line([(x, 0), (x, BASE_H)], fill=t["line"], width=1)
            for y in range(0, BASE_H, 54):
                draw.line([(0, y), (BASE_W, y)], fill=t["line"], width=1)
        elif t["pattern"] == "dots":
            for x in range(30, BASE_W, 48):
                for y in range(30, BASE_H, 48):
                    draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=t["line"])
        if t.get("margin_line"):
            draw.line([(MARGIN - 20, 0), (MARGIN - 20, BASE_H)], fill=t["accent2"], width=3)
        draw.rectangle([0, 0, BASE_W, 12], fill=t["accent"])  # top accent bar

    def _header(self, draw, specs: Dict, category: str) -> int:
        t = self.t
        label = (category or "Vehicle").upper()
        chip_font = find_font(22, "bold")
        chip_w = int(draw.textlength(label, font=chip_font)) + 44
        draw.rounded_rectangle([MARGIN, 52, MARGIN + chip_w, 94], 21, fill=t["accent"])
        text_color = (255, 255, 255) if sum(t["accent"]) < 560 else (20, 20, 20)
        draw.text((MARGIN + chip_w // 2, 73), label, font=chip_font, fill=text_color, anchor="mm")

        name = specs.get("name", "Vehicle")
        kind = "hand" if t["hand"] else "bold"
        max_w = BASE_W - 2 * MARGIN
        font = _fit_font(draw, name, max_w, 84, 46, kind)
        if draw.textlength(name, font=font) > max_w:
            lines = _clamp_lines(draw, _wrap(draw, name, find_font(52, kind), max_w), find_font(52, kind), max_w, 2)
            font = find_font(52, kind)
        else:
            lines = [name]
        y = 112
        for line in lines:
            draw.text((MARGIN, y), line, font=font, fill=t["ink"])
            y += int(font.size * 1.15) if hasattr(font, "size") else 60

        sub = " • ".join(p for p in [specs.get("manufacturer", ""), f"Since {specs['launch_year']}" if _has(specs.get("launch_year")) else ""] if p)
        if sub:
            draw.text((MARGIN, y + 2), sub, font=find_font(28, "regular"), fill=t["muted"])
            y += 40
        draw.line([(MARGIN, y + 14), (MARGIN + 160, y + 14)], fill=t["accent2"], width=6)
        return y + 34

    def _illustration(self, draw, specs: Dict, category: str, y: int) -> int:
        t = self.t
        h = 250
        x0, x1 = MARGIN, BASE_W - MARGIN
        draw.rounded_rectangle([x0, y, x1, y + h], 28, fill=t["card"], outline=t["line"], width=2)
        w = 640
        ox, oy = (BASE_W - w) // 2, y + 26
        ih = h - 52
        if _is_bike(specs, category):
            self._draw_bike(draw, ox, oy, w, ih)
        else:
            self._draw_car(draw, ox, oy, w, ih)
        # ground line
        draw.line([(x0 + 40, y + h - 28), (x1 - 40, y + h - 28)], fill=t["line"], width=3)
        return y + h + 26

    def _wheel(self, draw, cx, cy, r):
        t = self.t
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 24, 28))
        draw.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=(190, 196, 204))
        draw.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=(40, 42, 48))
        draw.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16], fill=t["accent2"])

    def _draw_car(self, draw, ox, oy, w, h):
        t = self.t

        def P(px, py):
            return (ox + px * w, oy + py * h)

        body = [P(.03, .72), P(.05, .55), P(.20, .48), P(.33, .45), P(.42, .18), P(.64, .18),
                P(.76, .45), P(.93, .50), P(.98, .64), P(.96, .78), P(.04, .78)]
        draw.polygon(body, fill=t["accent"], outline=t["ink"])
        draw.line(body + [body[0]], fill=t["ink"], width=4, joint="curve")
        window = [P(.435, .23), P(.525, .23), P(.525, .45), P(.36, .45)]
        window2 = [P(.545, .23), P(.635, .23), P(.715, .45), P(.545, .45)]
        for poly in (window, window2):
            draw.polygon(poly, fill=(205, 228, 245), outline=t["ink"])
        draw.line([P(.30, .62), P(.92, .62)], fill=_shade(t["accent"], -50), width=4)
        draw.ellipse([*P(.93, .54), *P(.97, .60)], fill=(255, 236, 150))  # headlight
        draw.ellipse([*P(.025, .56), *P(.06, .62)], fill=(220, 60, 60))   # tail light
        r = h * 0.19
        for cx in (.24, .76):
            self._wheel(draw, ox + cx * w, oy + .78 * h, r)

    def _draw_bike(self, draw, ox, oy, w, h):
        t = self.t

        def P(px, py):
            return (ox + px * w, oy + py * h)

        r = h * 0.27
        rear, front = P(.18, .70), P(.82, .70)
        self._wheel(draw, rear[0], rear[1], r)
        self._wheel(draw, front[0], front[1], r)
        line = dict(fill=t["ink"], width=7)
        draw.line([rear, P(.44, .45)], **line)             # swing arm / frame
        draw.line([P(.44, .45), P(.66, .36)], **line)       # top tube
        draw.line([P(.66, .36), front], **line)             # fork
        draw.line([P(.66, .36), P(.60, .16)], **line)       # steering stem
        draw.line([P(.54, .13), P(.68, .13)], fill=t["ink"], width=9)  # handlebar
        draw.polygon([P(.44, .50), P(.64, .46), P(.64, .72), P(.46, .74)], fill=_shade(t["accent"], -35), outline=t["ink"])  # engine
        draw.polygon([P(.40, .22), P(.64, .20), P(.66, .38), P(.42, .42)], fill=t["accent"], outline=t["ink"])  # tank
        draw.polygon([P(.22, .38), P(.42, .36), P(.42, .44), P(.20, .46)], fill=t["ink"])  # seat
        draw.ellipse([*P(.70, .30), *P(.76, .38)], fill=(255, 236, 150), outline=t["ink"])  # headlight
        draw.line([P(.30, .62), P(.14, .66)], fill=t["muted"], width=9)  # exhaust

    # ---- specs ------------------------------------------------------------

    def _spec_rows(self, specs: Dict, limit: int = 8) -> List[Tuple[str, str]]:
        dims = specs.get("dimensions") or {}
        dim_values = [dims.get(k) for k in ("length", "width", "height")]
        rows = [
            ("Engine", specs.get("engine")), ("Power", specs.get("horsepower")), ("Torque", specs.get("torque")),
            ("Top speed", specs.get("top_speed")), ("Transmission", specs.get("transmission")),
            ("Weight", specs.get("weight")), ("Range", specs.get("range")), ("Mileage", specs.get("mileage")),
            ("Battery", specs.get("battery")), ("Fuel tank", specs.get("fuel_tank")),
            ("Dimensions (L×W×H)", " × ".join(v for v in dim_values if _has(v)) if sum(_has(v) for v in dim_values) >= 2 else None),
            ("Wheelbase", specs.get("wheelbase")), ("Seat height", specs.get("seat_height")),
            ("Suspension", specs.get("suspension")), ("Brakes", specs.get("brakes")),
            ("Launched", specs.get("launch_year")), ("Price", specs.get("price")),
        ]
        return [(k, str(v)) for k, v in rows if _has(v)][:limit]

    def _spec_cards(self, draw, specs: Dict, y: int) -> int:
        t = self.t
        rows = self._spec_rows(specs, 8)
        if not rows:
            return y
        gap = 20
        card_w = (BASE_W - 2 * MARGIN - gap) // 2
        card_h = 112
        label_font, value_font = find_font(20, "bold"), find_font(27, "bold")
        for i, (label, value) in enumerate(rows):
            cx = MARGIN + (i % 2) * (card_w + gap)
            cy = y + (i // 2) * (card_h + gap)
            draw.rounded_rectangle([cx + 3, cy + 5, cx + card_w + 3, cy + card_h + 5], 20, fill=_shade(t["bg"], -14 if sum(t["bg"]) > 400 else 12))
            draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], 20, fill=t["card"], outline=t["line"], width=2)
            draw.rounded_rectangle([cx, cy + 18, cx + 7, cy + card_h - 18], 3, fill=t["accent"])
            draw.text((cx + 28, cy + 16), label.upper(), font=label_font, fill=t["muted"])
            lines = _clamp_lines(draw, _wrap(draw, value, value_font, card_w - 52), value_font, card_w - 52, 2)
            for j, line in enumerate(lines):
                draw.text((cx + 28, cy + 46 + j * 32), line, font=value_font, fill=t["ink"])
        return y + ((len(rows) + 1) // 2) * (card_h + gap) + 4

    def _about_and_features(self, draw, specs: Dict, y: int) -> None:
        t = self.t
        bottom = BASE_H - 170
        available = bottom - y
        if available < 90:
            return
        desc = (specs.get("description") or "").replace("\n", " ").strip()
        features = [f for f in specs.get("features", []) if _has(f)]
        has_specs = y > 700
        body_font = find_font(26 if has_specs else 30, "regular")
        box_h = min(available, 190 if has_specs else 560)
        draw.rounded_rectangle([MARGIN, y, BASE_W - MARGIN, y + box_h], 24, fill=t["card"], outline=t["line"], width=2)
        draw.text((MARGIN + 28, y + 18), "ABOUT", font=find_font(20, "bold"), fill=t["accent"])
        text = desc or "Follow InstaNote for daily vehicle specs, history and fun facts."
        max_lines = max(2, (box_h - 80) // 36) if not features else max(2, (box_h - 80) // 36)
        lines = _clamp_lines(draw, _wrap(draw, text, body_font, BASE_W - 2 * MARGIN - 56), body_font, BASE_W - 2 * MARGIN - 56, max_lines)
        ty = y + 52
        for line in lines:
            draw.text((MARGIN + 28, ty), line, font=body_font, fill=t["ink"])
            ty += 36
        # feature chips
        if features and ty + 56 < y + box_h + 60 and y + box_h + 70 < bottom + 90:
            cx, cy = MARGIN, y + box_h + 18
            chip_font = find_font(22, "bold")
            for feat in features[:5]:
                tw = int(draw.textlength(feat, font=chip_font)) + 36
                if cx + tw > BASE_W - MARGIN:
                    break
                draw.rounded_rectangle([cx, cy, cx + tw, cy + 44], 22, outline=t["accent"], width=2, fill=t["card"])
                draw.text((cx + tw // 2, cy + 22), feat, font=chip_font, fill=t["ink"], anchor="mm")
                cx += tw + 12

    def _footer(self, draw, specs: Dict) -> None:
        t = self.t
        y = BASE_H - 130
        draw.line([(MARGIN, y - 14), (BASE_W - MARGIN, y - 14)], fill=t["line"], width=2)
        x = MARGIN
        if _has(specs.get("price")):
            font = find_font(26, "bold")
            text = str(specs["price"])
            tw = min(int(draw.textlength(text, font=font)) + 44, 420)
            text = _clamp_lines(draw, [text], font, tw - 44, 1)[0]
            draw.rounded_rectangle([x, y + 10, x + tw, y + 66], 28, fill=t["accent2"])
            ink = (20, 20, 20) if sum(t["accent2"]) > 380 else (255, 255, 255)
            draw.text((x + tw // 2, y + 38), text, font=font, fill=ink, anchor="mm")
            x += tw + 24
        colors = [(n, color_for_name(n)) for n in specs.get("colors", [])]
        colors = [(n, c) for n, c in colors if c][:5]
        if colors:
            draw.text((x, y + 38), "Colors", font=find_font(20, "bold"), fill=t["muted"], anchor="lm")
            x += 90
            for _, rgb in colors:
                draw.ellipse([x, y + 20, x + 38, y + 58], fill=rgb, outline=t["ink"], width=2)
                x += 48
        brand = "@InstaNote"
        draw.text((BASE_W - MARGIN, y + 38), brand, font=find_font(30, "bold"), fill=t["accent"], anchor="rm")


# --------------------------------------------------------------------------- module-level API

def generate_infographic(vehicle_specs: Dict, output_path: Optional[Path] = None) -> Path:
    """Generate the main infographic and return its path."""
    generator = InfographicGenerator()
    img = generator.create_image(vehicle_specs)
    if output_path is None:
        slug = re.sub(r"[^a-z0-9]+", "-", vehicle_specs.get("name", "vehicle").lower()).strip("-") or "vehicle"
        output_path = project_path("output") / f"{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)
    return output_path


def generate_multiple_infographics(vehicle_specs: Dict) -> List[Path]:
    generator = InfographicGenerator()
    slug = re.sub(r"[^a-z0-9]+", "-", vehicle_specs.get("name", "vehicle").lower()).strip("-") or "vehicle"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    paths = []
    for i, slide in enumerate(generator.generate_multiple_slides(vehicle_specs), 1):
        path = project_path("output") / f"{slug}-{stamp}-slide{i}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        slide.save(path, format="PNG", optimize=True)
        paths.append(path)
    return paths


_generator: Optional[InfographicGenerator] = None


def get_content_generator() -> InfographicGenerator:
    global _generator
    if _generator is None:
        _generator = InfographicGenerator()
    return _generator
