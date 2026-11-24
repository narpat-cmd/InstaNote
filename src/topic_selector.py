"""Topic selector for InstaNote - picks vehicles and keeps the published-post history."""

import json
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
HISTORY_FILE = DATA_DIR / "published_posts.json"
_lock = threading.RLock()

TOPICS = [
    "Bikes and motorcycles", "Sports bikes", "Scooters", "Superbikes", "Electric bikes",
    "Cars", "Supercars", "Luxury cars", "SUVs", "Electric cars",
    "Vintage and classic vehicles", "Racing cars", "Modified vehicles",
    "Upcoming vehicles", "Automobile brands", "Engines and automotive technology",
]

SUBCATEGORIES = {
    "Bikes and motorcycles": ["Harley-Davidson Street 750", "Yamaha R1", "Ducati Monster", "Royal Enfield Classic 350", "Kawasaki Ninja 400"],
    "Sports bikes": ["Ducati Panigale V4", "Yamaha YZF-R1M", "BMW S1000RR", "Kawasaki ZX-14R", "Triumph Daytona 660"],
    "Scooters": ["Vespa GTS 300", "Honda PCX125", "Yamaha NMAX", "Aprilia Scarlett 50", "BMW C 400 GT"],
    "Superbikes": ["Kawasaki Ninja ZX-14", "Suzuki Hayabusa", "Ducati Panigale", "Yamaha YZF-R6", "Triumph Speed Triple"],
    "Electric bikes": ["Zero SR/F", "Energica Ego", "Harley-Davidson LiveWire", "Ola S1 Pro", "Ather 450X"],
    "Cars": ["Toyota Camry", "Honda Civic", "Ford Mustang", "BMW 3 Series", "Audi A4"],
    "Supercars": ["Ferrari F8 Tributo", "Lamborghini Huracan", "McLaren 720S", "Porsche 911 Turbo", "Aston Martin DB11"],
    "Luxury cars": ["Rolls-Royce Phantom", "Mercedes S-Class", "BMW 7 Series", "Audi A8", "Lexus LS"],
    "SUVs": ["Range Rover Sport", "BMW X5", "Mercedes GLE", "Toyota Land Cruiser", "Ford Explorer"],
    "Electric cars": ["Tesla Model S", "Porsche Taycan", "Lucid Air", "Rivian R1T", "Ford Mustang Mach-E"],
    "Vintage and classic vehicles": ["Ford Model T", "Chevrolet Corvette C1", "Jaguar E-Type", "Porsche 911 Carrera RS", "Ferrari 250 GTO"],
    "Racing cars": ["Formula 1 Car", "NASCAR Chevrolet", "BMW M3 DTM", "Dallara F3", "Porsche 919 Hybrid"],
    "Modified vehicles": ["Honda Civic Type R", "Nissan Skyline GT-R", "Toyota Supra", "Mazda RX-7", "Subaru WRX STI"],
    "Upcoming vehicles": ["Tesla Cybertruck", "Ford Mustang Mach-E", "BMW i5", "Audi Q6 e-tron", "Hyundai Ioniq 7"],
    "Automobile brands": ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Hyundai", "Kia", "Nissan"],
    "Engines and automotive technology": ["Turbocharged Engines", "Hybrid Systems", "Electric Motors", "Direct Injection", "CVT Transmissions"],
}

VEHICLE_CATEGORIES = {
    "Bikes and motorcycles": {"name": "Bikes and Motorcycles", "description": "All types of two-wheelers", "hashtags": ["#bikes", "#motorcycles", "#riding"]},
    "Sports bikes": {"name": "Sports Bikes", "description": "High-performance motorcycles", "hashtags": ["#sportbikes", "#racing", "#performance"]},
    "Scooters": {"name": "Scooters", "description": "Urban mobility vehicles", "hashtags": ["#scooter", "#urban", "#commute"]},
    "Superbikes": {"name": "Superbikes", "description": "Top-tier performance bikes", "hashtags": ["#superbike", "#speed", "#track"]},
    "Electric bikes": {"name": "Electric Bikes", "description": "E-bikes and electric motorcycles", "hashtags": ["#ebike", "#electric", "#green"]},
    "Cars": {"name": "Cars", "description": "Regular passenger cars", "hashtags": ["#cars", "#automotive", "#driving"]},
    "Supercars": {"name": "Supercars", "description": "High-performance luxury cars", "hashtags": ["#supercar", "#luxury", "#exotic"]},
    "Luxury cars": {"name": "Luxury Cars", "description": "Premium vehicles", "hashtags": ["#luxurycars", "#premium", "#comfort"]},
    "SUVs": {"name": "SUVs", "description": "Sport utility vehicles", "hashtags": ["#suv", "#crossover", "#adventure"]},
    "Electric cars": {"name": "Electric Cars", "description": "Battery-powered vehicles", "hashtags": ["#electriccars", "#ev", "#sustainable"]},
    "Vintage and classic vehicles": {"name": "Vintage & Classic", "description": "Historic vehicles", "hashtags": ["#vintage", "#classic", "#retro"]},
    "Racing cars": {"name": "Racing Cars", "description": "Track and motorsport vehicles", "hashtags": ["#racing", "#motorsport", "#formula1"]},
    "Modified vehicles": {"name": "Modified Vehicles", "description": "Custom and modified cars", "hashtags": ["#modified", "#custom", "#tuning"]},
    "Upcoming vehicles": {"name": "Upcoming Vehicles", "description": "New launches and concepts", "hashtags": ["#upcoming", "#new", "#launch"]},
    "Automobile brands": {"name": "Automobile Brands", "description": "Car manufacturers", "hashtags": ["#brand", "#manufacturer", "#auto"]},
    "Engines and automotive technology": {"name": "Engines & Technology", "description": "Technical innovations", "hashtags": ["#technology", "#engineering", "#innovation"]},
}
for _key, _info in VEHICLE_CATEGORIES.items():
    _info["examples"] = SUBCATEGORIES[_key]


# --------------------------------------------------------------------------- Topic

class Topic:
    """A vehicle that we want to make a post about."""

    def __init__(self, category_key: str, vehicle_name: str, vehicle_year: Optional[int] = None):
        self.category_key = category_key or ""
        self.vehicle_name = (vehicle_name or "").strip()
        self.vehicle_year = int(vehicle_year) if vehicle_year else datetime.now().year
        self.id = f"{self.vehicle_name}_{self.vehicle_year}".replace(" ", "_")

    def to_dict(self) -> Dict:
        return {
            "category_key": self.category_key,
            "vehicle_name": self.vehicle_name,
            "vehicle_year": self.vehicle_year,
            "id": self.id,
        }

    def __repr__(self) -> str:
        return f"Topic({self.category_key!r}, {self.vehicle_name!r}, {self.vehicle_year})"


# --------------------------------------------------------------------------- storage

def _load_posts() -> List[Dict]:
    with _lock:
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f).get("posts", [])
            except (json.JSONDecodeError, OSError):
                return []
        return []


def _save_posts(posts: List[Dict]) -> None:
    with _lock:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = HISTORY_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"posts": posts, "last_updated": datetime.now().isoformat()}, f, indent=2)
        tmp.replace(HISTORY_FILE)


def _parse_dt(value: Optional[str]) -> datetime:
    try:
        return datetime.fromisoformat(value) if value else datetime.now()
    except (TypeError, ValueError):
        return datetime.now()


def _hydrate(post: Dict) -> Dict:
    """Return a copy with a real datetime in ``published_at`` (templates call strftime)."""
    out = dict(post)
    out["published_at"] = _parse_dt(post.get("published_at"))
    return out


def load_published_topics() -> set:
    """Set of vehicle names that were already published."""
    return {p.get("vehicle_name") for p in _load_posts()}


def save_topic(topic: str, vehicle_name: Optional[str] = None, **extra) -> Dict:
    """Record a published post. Kept with its old signature for the automation cycle."""
    vehicle_name = vehicle_name or topic
    now = datetime.now()
    record = {
        "id": f"{vehicle_name}_{int(now.timestamp())}".replace(" ", "_"),
        "category_key": topic if topic in VEHICLE_CATEGORIES else extra.pop("category_key", topic),
        "vehicle_name": vehicle_name,
        "vehicle_year": extra.pop("vehicle_year", now.year),
        "image_path": extra.pop("image_path", ""),
        "instagram_post_id": extra.pop("instagram_post_id", ""),
        "caption": extra.pop("caption", ""),
        "hashtags": extra.pop("hashtags", []),
        "published_at": now.isoformat(),
    }
    with _lock:
        posts = _load_posts()
        posts.append(record)
        _save_posts(posts)
    return record


def category_of(vehicle_name: str) -> str:
    for cat, vehicles in SUBCATEGORIES.items():
        if vehicle_name in vehicles:
            return cat
    return ""


def select_random_topic(category: Optional[str] = None, skip_posted: bool = True) -> Dict:
    """Pick a random (category, vehicle) that was not published yet (resets when all are used)."""
    published = load_published_topics() if skip_posted else set()
    categories = [category] if category in SUBCATEGORIES else list(TOPICS)

    candidates = [(c, v) for c in categories for v in SUBCATEGORIES[c] if v not in published]
    if not candidates:  # everything has been posted once -> start a new round
        candidates = [(c, v) for c in categories for v in SUBCATEGORIES[c]]

    cat, vehicle = random.choice(candidates)
    return {"category": cat, "vehicle": vehicle, "timestamp": datetime.now().isoformat()}


def select_topic() -> Dict:
    return select_random_topic()


def get_topic_history() -> Dict:
    posts = _load_posts()
    return {"topics": [p.get("vehicle_name") for p in posts], "posts": posts,
            "last_updated": posts[-1].get("published_at") if posts else None}


# --------------------------------------------------------------------------- class API

class TopicSelector:
    """Class based API used by the admin panel."""

    def select_topic(self, category: Optional[str] = None) -> Dict:
        return select_random_topic(category)

    def mark_published(self, topic: Topic, image_path, post_id: str, caption: str, hashtags: List[str]) -> Dict:
        return save_topic(
            topic.category_key, topic.vehicle_name,
            vehicle_year=topic.vehicle_year, image_path=str(image_path),
            instagram_post_id=post_id or "", caption=caption, hashtags=hashtags,
        )

    def get_stats(self) -> Dict:
        posts = _load_posts()
        now = datetime.now()
        today = now.date()
        week_start = now - timedelta(days=7)

        by_category: Dict[str, int] = {}
        today_count = week_count = 0
        for p in posts:
            cat = p.get("category_key") or category_of(p.get("vehicle_name", ""))
            by_category[cat] = by_category.get(cat, 0) + 1
            when = _parse_dt(p.get("published_at"))
            if when.date() == today:
                today_count += 1
            if when >= week_start:
                week_count += 1

        return {
            "total_posts": len(posts),
            "total_published": len(posts),
            "today": today_count,
            "this_week": week_count,
            "by_category": by_category,
            "last_updated": posts[-1].get("published_at") if posts else None,
        }

    def get_published_history(self, limit: int = 50, category: Optional[str] = None) -> List[Dict]:
        posts = [_hydrate(p) for p in _load_posts()]
        if category:
            posts = [p for p in posts if p.get("category_key") == category]
        posts.sort(key=lambda p: p["published_at"], reverse=True)
        return posts[:limit]

    def delete_topic(self, topic_id: str) -> None:
        with _lock:
            posts = [p for p in _load_posts() if p.get("id") != topic_id]
            _save_posts(posts)
