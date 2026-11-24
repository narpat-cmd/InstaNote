"""Researcher module for InstaNote - collects vehicle specifications.

Sources (free, no API key):
  1. A small hand-curated knowledge base (most reliable values)
  2. Wikipedia - infobox of the vehicle page + the intro paragraph
  3. Safe defaults ("N/A" rows are simply hidden in the infographic)
"""

import json
import logging
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import requests

from src.config import get_config

logger = logging.getLogger(__name__)

CACHE_FILE = Path(__file__).resolve().parent.parent / "data" / "research_cache.json"
_cache_lock = threading.Lock()

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "InstaNote/2.0 (https://github.com/narpat-cmd/InstaNote; vehicle infographic bot)"}

MANUFACTURERS = [
    "Harley-Davidson", "Royal Enfield", "Aston Martin", "Rolls-Royce", "Mercedes-Benz", "Land Rover",
    "Yamaha", "Ducati", "Kawasaki", "Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", "Volkswagen",
    "Porsche", "Ferrari", "Lamborghini", "McLaren", "Lexus", "Jaguar", "Maserati", "Chevrolet", "Nissan",
    "Hyundai", "Kia", "Subaru", "Mazda", "Tesla", "Lucid", "Rivian", "Zero", "Energica", "Vespa",
    "Aprilia", "Suzuki", "Triumph", "Peugeot", "Piaggio", "Kymco", "Ola", "Ather", "Dallara", "NASCAR",
]

# --------------------------------------------------------------------------- cache

def load_cache() -> Dict:
    with _cache_lock:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return {}
        return {}


def save_cache(data: Dict) -> None:
    with _cache_lock:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# --------------------------------------------------------------------------- helpers

def extract_manufacturer(vehicle_name: str) -> str:
    lower = (vehicle_name or "").lower()
    for manuf in MANUFACTURERS:
        if manuf.lower() in lower:
            return manuf
    return vehicle_name.split()[0] if vehicle_name else ""


def extract_year(vehicle_name: str) -> str:
    match = re.search(r"\b(?:19|20)\d{2}\b", vehicle_name or "")
    return match.group(0) if match else "N/A"


_CONVERT = re.compile(r"\{\{\s*(?:convert|cvt)\s*\|([^{}]*)\}\}", re.I)


def _convert_template(match) -> str:
    parts = [p.strip() for p in match.group(1).split("|")]
    if len(parts) >= 4 and parts[1] in ("to", "-", "–", "and", "or"):
        return f"{parts[0]}–{parts[2]} {parts[3]}"
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    return parts[0] if parts else ""


def clean_wikitext(value: str, limit: int = 70) -> str:
    """Turn a raw infobox value into short, readable plain text."""
    if not value:
        return ""
    text = re.sub(r"<!--.*?-->", "", value, flags=re.S)
    text = re.sub(r"<ref[^>]*?/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"<br\s*/?>", ", ", text, flags=re.I)
    text = _CONVERT.sub(_convert_template, text)
    text = re.sub(r"\{\{\s*(?:nowrap|nobr|small)\s*\|([^{}]*)\}\}", r"\1", text, flags=re.I)
    text = re.sub(r"\{\{\s*(?:flatlist|plainlist|ubl|unbulleted list)\s*\|", "", text, flags=re.I)
    for _ in range(5):  # drop remaining (possibly nested) templates
        new = re.sub(r"\{\{[^{}]*\}\}", "", text)
        if new == text:
            break
        text = new
    text = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("'''", "").replace("''", "").replace("&nbsp;", " ").replace("&ndash;", "–")
    text = re.sub(r"^[\s*#:,]+", "", text)
    text = re.sub(r"\s*\n\s*[*#]?\s*", ", ", text)
    text = re.sub(r"[{}|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;")
    if len(text) > limit:
        text = text[: limit - 1].rsplit(" ", 1)[0].rstrip(",;") + "…"
    return text


def parse_infobox(wikitext: str) -> Dict[str, str]:
    """Return {field: raw value} for the first ``{{Infobox ...}}`` of a page."""
    start = re.search(r"\{\{\s*infobox", wikitext or "", re.I)
    if not start:
        return {}
    fields: Dict[str, str] = {}
    key = None
    depth = 0
    for line in wikitext[start.start():].splitlines():
        if key is None and not fields and depth == 0 and "{{" in line:
            depth += line.count("{{") - line.count("}}")
            continue
        m = re.match(r"^\s*\|\s*([A-Za-z0-9_ \-]+?)\s*=\s*(.*)$", line)
        if m and depth <= 1:
            key = m.group(1).strip().lower().replace(" ", "_")
            fields[key] = m.group(2)
            depth = 1 + (m.group(2).count("{{") - m.group(2).count("}}"))
            continue
        if key is not None:
            depth += line.count("{{") - line.count("}}")
            if depth <= 0 or line.strip().startswith("}}"):
                if depth <= 0:
                    break
            elif not line.strip().startswith("|"):
                fields[key] += "\n" + line
    return fields


FIELD_MAP = {
    "engine": ["engine", "engine_capacity", "displacement"],
    "horsepower": ["power", "power_output", "horsepower"],
    "torque": ["torque"],
    "top_speed": ["top_speed", "topspeed", "maximum_speed"],
    "transmission": ["transmission", "gearbox"],
    "weight": ["weight", "curb_weight", "kerb_weight", "wet_weight", "dry_weight"],
    "fuel_tank": ["fuel_capacity", "fuel_tank"],
    "battery": ["battery", "battery_capacity"],
    "range": ["range", "electric_range"],
    "mileage": ["fuel_economy", "fuel_consumption", "mileage"],
    "suspension": ["suspension", "front_suspension"],
    "brakes": ["brakes", "front_brake", "brakes_front"],
    "price": ["price", "msrp"],
    "wheelbase": ["wheelbase"],
    "seat_height": ["seat_height"],
}


def specs_from_infobox(fields: Dict[str, str]) -> Dict:
    specs: Dict = {}
    for target, candidates in FIELD_MAP.items():
        for cand in candidates:
            if cand in fields:
                value = clean_wikitext(fields[cand])
                if value:
                    specs[target] = value
                    break
    dims = {}
    for dim in ("length", "width", "height"):
        value = clean_wikitext(fields.get(dim, ""), 30)
        if value:
            dims[dim] = value
    if dims:
        specs["dimensions"] = dims
    prod = fields.get("production", "")
    year = re.search(r"\b(19|20)\d{2}\b", clean_wikitext(prod, 40))
    if year:
        specs["launch_year"] = year.group(0)
    manuf = clean_wikitext(fields.get("manufacturer", ""), 40)
    if manuf:
        specs["manufacturer"] = manuf
    return specs


def _wiki_get(params: Dict, timeout: int, retries: int) -> Optional[Dict]:
    for attempt in range(max(1, retries)):
        try:
            resp = requests.get(WIKI_API, params={**params, "format": "json"}, headers=HEADERS, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            logger.warning("Wikipedia returned HTTP %s", resp.status_code)
        except (requests.RequestException, ValueError) as exc:
            logger.warning("Wikipedia request failed (%s/%s): %s", attempt + 1, retries, exc)
        time.sleep(0.5 * (attempt + 1))
    return None


def fetch_wikipedia(vehicle_name: str, timeout: int = 15, retries: int = 2) -> Dict:
    """Return {'title', 'description', 'specs'} for a vehicle (empty dict when nothing was found)."""
    found = _wiki_get({"action": "query", "list": "search", "srsearch": vehicle_name, "srlimit": 1}, timeout, retries)
    hits = (found or {}).get("query", {}).get("search", [])
    if not hits:
        return {}
    title = hits[0]["title"]

    info = _wiki_get({"action": "query", "prop": "extracts", "exintro": 1, "explaintext": 1,
                      "redirects": 1, "titles": title}, timeout, retries)
    description = ""
    for page in (info or {}).get("query", {}).get("pages", {}).values():
        description = (page.get("extract") or "").strip()

    parsed = _wiki_get({"action": "parse", "page": title, "prop": "wikitext", "section": 0, "redirects": 1}, timeout, retries)
    wikitext = ((parsed or {}).get("parse", {}).get("wikitext", {}) or {}).get("*", "")
    specs = specs_from_infobox(parse_infobox(wikitext))
    return {"title": title, "description": description, "specs": specs}


# --------------------------------------------------------------------------- knowledge base

KNOWLEDGE_BASE = {
    "Ducati Panigale V4": {
        "manufacturer": "Ducati", "launch_year": "2018", "engine": "1103 cc Desmosedici Stradale V4",
        "horsepower": "214 hp @ 13,000 rpm", "torque": "124 Nm @ 10,000 rpm", "top_speed": "299 km/h",
        "transmission": "6-speed with quick shifter", "suspension": "Showa BPF fork, Sachs rear shock",
        "brakes": "Brembo Stylema 4-piston calipers", "weight": "175 kg (dry)",
        "dimensions": {"length": "2,100 mm", "width": "800 mm", "height": "1,150 mm"},
        "features": ["Cornering ABS", "Traction Control", "Quick Shifter", "Full LED"], "price": "from $24,000",
        "colors": ["Red", "Black", "White"]},
    "Tesla Model S": {
        "manufacturer": "Tesla", "launch_year": "2012", "engine": "Dual electric motors", "horsepower": "670 hp (Plaid: 1,020 hp)",
        "torque": "1,050 lb-ft (Plaid)", "range": "~405 miles", "top_speed": "322 km/h (Plaid)",
        "transmission": "Single-speed", "suspension": "Adaptive air suspension", "brakes": "Regenerative + 4-wheel disc",
        "dimensions": {"length": "4,970 mm", "width": "1,964 mm", "height": "1,445 mm"}, "weight": "2,100 kg",
        "battery": "100 kWh", "features": ["Autopilot", "17\" touchscreen", "Over-the-air updates"],
        "price": "from $74,990", "colors": ["White", "Black", "Blue", "Red"]},
    "Ferrari F8 Tributo": {
        "manufacturer": "Ferrari", "launch_year": "2019", "engine": "3.9 L twin-turbo V8", "horsepower": "710 hp @ 8,000 rpm",
        "torque": "770 Nm @ 3,250 rpm", "top_speed": "340 km/h", "transmission": "7-speed dual-clutch",
        "suspension": "Double wishbone, magnetorheological dampers", "brakes": "Brembo carbon-ceramic",
        "dimensions": {"length": "4,611 mm", "width": "1,979 mm", "height": "1,206 mm"}, "weight": "1,435 kg (dry)",
        "features": ["Active aerodynamics", "Side Slip Control 6.1", "Launch control"], "price": "from $276,000",
        "colors": ["Rosso Corsa", "Giallo Modena", "Nero", "Bianco Avus"]},
    "BMW S1000RR": {
        "manufacturer": "BMW Motorrad", "launch_year": "2009", "engine": "999 cc inline-4", "horsepower": "205 hp @ 13,500 rpm",
        "torque": "113 Nm @ 11,000 rpm", "top_speed": "299 km/h", "transmission": "6-speed",
        "suspension": "Upside-down fork, rear monoshock", "brakes": "Dual 320 mm discs, 4-piston radial calipers",
        "dimensions": {"length": "2,073 mm", "width": "848 mm", "height": "1,184 mm"}, "weight": "197 kg (wet)",
        "features": ["Ride Modes", "Dynamic Traction Control", "Shift Assistant Pro", "Full LED"], "price": "from $17,000",
        "colors": ["White", "Black", "Blue"]},
    "Range Rover Sport": {
        "manufacturer": "Land Rover", "launch_year": "2005", "engine": "3.0 L inline-6 mild hybrid / 4.4 L V8",
        "horsepower": "395 hp (P400)", "torque": "550 Nm", "top_speed": "242 km/h", "transmission": "8-speed automatic",
        "suspension": "Adaptive air suspension", "brakes": "Ventilated discs, ABS",
        "dimensions": {"length": "4,946 mm", "width": "2,209 mm", "height": "1,820 mm"}, "weight": "2,360 kg",
        "features": ["Terrain Response 2", "All-wheel drive", "Panoramic roof"], "price": "from $84,000",
        "colors": ["White", "Black", "Grey"]},
    "Lamborghini Huracan": {
        "manufacturer": "Lamborghini", "launch_year": "2014", "engine": "5.2 L V10 naturally aspirated",
        "horsepower": "631 hp @ 8,000 rpm", "torque": "565 Nm @ 6,500 rpm", "top_speed": "325 km/h",
        "transmission": "7-speed dual-clutch", "suspension": "Double wishbone, magnetorheological",
        "brakes": "Carbon-ceramic", "dimensions": {"length": "4,520 mm", "width": "1,933 mm", "height": "1,165 mm"},
        "weight": "1,422 kg (dry)", "features": ["ANIMA drive modes", "Aerodynamic flaps", "Launch control"],
        "price": "from $210,000", "colors": ["Giallo Orion", "Verde Mantis", "Arancio Borealis"]},
    "Royal Enfield Classic 350": {
        "manufacturer": "Royal Enfield", "launch_year": "2021", "engine": "349 cc air-oil cooled single",
        "horsepower": "20.2 hp @ 6,100 rpm", "torque": "27 Nm @ 4,000 rpm", "mileage": "35-41 km/l", "top_speed": "~120 km/h",
        "transmission": "5-speed", "suspension": "Telescopic fork, twin rear shocks", "brakes": "Disc front, drum/disc rear, ABS",
        "dimensions": {"length": "2,145 mm", "width": "785 mm", "height": "1,090 mm"}, "weight": "195 kg",
        "fuel_tank": "13 L", "features": ["J-series engine", "LED headlamp", "Tripper navigation"],
        "price": "from Rs 1.9 lakh (ex-showroom)", "colors": ["Halcyon", "Redditch", "Chrome"]},
    "Porsche 911 Turbo": {
        "manufacturer": "Porsche", "launch_year": "1975", "engine": "3.7 L twin-turbo flat-6", "horsepower": "572 hp @ 6,750 rpm",
        "torque": "750 Nm @ 2,500 rpm", "top_speed": "320 km/h", "transmission": "8-speed PDK",
        "suspension": "Adaptive dampers (PASM)", "brakes": "Steel or PCCB ceramic",
        "dimensions": {"length": "4,535 mm", "width": "1,900 mm", "height": "1,296 mm"}, "weight": "1,640 kg",
        "features": ["All-wheel drive", "Active aero", "Sport Chrono"], "price": "from $175,000",
        "colors": ["Guards Red", "Racing Yellow", "Black"]},
}


def find_in_knowledge_base(vehicle_name: str) -> Optional[Dict]:
    lower = (vehicle_name or "").lower().strip()
    for key, data in KNOWLEDGE_BASE.items():
        if key.lower() == lower or key.lower() in lower:
            return data
    return None


def default_specs(vehicle_name: str) -> Dict:
    return {
        "name": vehicle_name,
        "manufacturer": extract_manufacturer(vehicle_name),
        "launch_year": extract_year(vehicle_name),
        "description": "",
        "engine": "N/A", "horsepower": "N/A", "torque": "N/A", "mileage": "N/A", "range": "N/A",
        "top_speed": "N/A", "transmission": "N/A", "suspension": "N/A", "brakes": "N/A",
        "dimensions": {"length": "N/A", "width": "N/A", "height": "N/A"},
        "weight": "N/A", "fuel_tank": "N/A", "battery": "N/A", "price": "N/A",
        "features": [], "colors": [],
        "source": "defaults",
        "research_timestamp": datetime.now().isoformat(),
    }


def research_vehicle(vehicle_name: str, force: bool = False) -> Dict:
    """Research a vehicle and return a specifications dict (never raises)."""
    cfg = get_config().research
    cache = load_cache()
    cached = cache.get(vehicle_name)
    if cached and not force:
        try:
            age = (datetime.now() - datetime.fromisoformat(cached.get("research_timestamp"))).total_seconds()
        except (TypeError, ValueError):
            age = float("inf")
        if age < max(cfg.cache_ttl, 3600) * 24:  # specs rarely change: keep a day per TTL hour
            return cached

    specs = default_specs(vehicle_name)
    sources = ["defaults"]

    if "wikipedia" in (cfg.sources or []):
        try:
            wiki = fetch_wikipedia(vehicle_name, timeout=min(cfg.timeout, 20), retries=cfg.max_retries)
        except Exception as exc:  # network/parse problems must never break posting
            logger.warning("Wikipedia research failed for %s: %s", vehicle_name, exc)
            wiki = {}
        if wiki:
            sources.append("wikipedia")
            specs["description"] = wiki.get("description", "")
            specs["wikipedia_title"] = wiki.get("title", "")
            for key, value in wiki.get("specs", {}).items():
                if key == "dimensions":
                    specs["dimensions"].update(value)
                else:
                    specs[key] = value

    kb = find_in_knowledge_base(vehicle_name)
    if kb:
        sources.append("knowledge_base")
        for key, value in kb.items():
            if key == "dimensions":
                specs["dimensions"].update(value)
            else:
                specs[key] = value

    specs["source"] = "+".join(sources[1:]) or "defaults"
    specs["name"] = vehicle_name
    specs["research_timestamp"] = datetime.now().isoformat()

    cache[vehicle_name] = specs
    save_cache(cache)
    return specs


class Researcher:
    """Class wrapper used by the admin panel."""

    def research(self, topic, force: bool = False) -> Dict:
        name = getattr(topic, "vehicle_name", None) or str(topic)
        return research_vehicle(name, force=force)


_researcher: Optional[Researcher] = None


def get_researcher() -> Researcher:
    global _researcher
    if _researcher is None:
        _researcher = Researcher()
    return _researcher


# --------------------------------------------------------------------------- captions

def _has(value) -> bool:
    return bool(value) and str(value).upper() != "N/A"


def generate_caption(vehicle_specs: Dict) -> str:
    """Instagram caption (text + hashtags)."""
    name = vehicle_specs.get("name", "Vehicle")
    lines = [f"🏁 {name}"]
    facts = []
    if _has(vehicle_specs.get("horsepower")):
        facts.append(f"⚡ {vehicle_specs['horsepower']}")
    if _has(vehicle_specs.get("torque")):
        facts.append(f"🔧 {vehicle_specs['torque']}")
    if _has(vehicle_specs.get("top_speed")):
        facts.append(f"🚀 {vehicle_specs['top_speed']}")
    if facts:
        lines.append(" | ".join(facts))
    if _has(vehicle_specs.get("price")):
        lines.append(f"💰 {vehicle_specs['price']}")
    desc = (vehicle_specs.get("description") or "").split(". ")[0].strip()
    if desc:
        lines.append("\n" + desc[:220].rstrip(".") + ".")
    lines.append("\n💬 Save this post & follow @InstaNote for daily vehicle specs!\n")
    lines.append(" ".join(generate_hashtags(vehicle_specs)))
    return "\n".join(lines)


def generate_hashtags(vehicle_specs: Dict) -> list:
    tags = ["#VehicleSpecs", "#CarEnthusiast", "#BikeLife", "#Automotive", "#InstaNote",
            "#CarLovers", "#Motorcycle", "#Supercar", "#Racing", "#CarSpotting"]
    manufacturer = re.sub(r"[^A-Za-z0-9]", "", vehicle_specs.get("manufacturer", ""))
    if manufacturer:
        tags.append(f"#{manufacturer}")
    model = re.sub(r"[^A-Za-z0-9]", "", vehicle_specs.get("name", ""))
    if model:
        tags.append(f"#{model}")
    return tags
