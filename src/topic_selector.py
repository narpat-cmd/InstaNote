"""Topic selector for InstaNote - selects random bike/car topics"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

HISTORY_FILE = Path(__file__).parent.parent / "data" / "published_topics.json"

TOPICS = [
    "Bikes and motorcycles",
    "Sports bikes",
    "Scooters",
    "Superbikes",
    "Electric bikes",
    "Cars",
    "Supercars",
    "Luxury cars",
    "SUVs",
    "Electric cars",
    "Vintage and classic vehicles",
    "Racing cars",
    "Modified vehicles",
    "Upcoming vehicles",
    "Automobile brands",
    "Engines and automotive technology"
]

SUBCATEGORIES = {
    "Bikes and motorcycles": ["Harley-Davidson Street 750", "Yamaha R1", "Ducati Monster", "Royal Enfield Classic 350", "Kawasaki Ninja 400"],
    "Sports bikes": ["Ducati Panigale V4", "Yamaha YZF-R1M", "BMW S1000RR", "Kawasaki ZX-14R", "Triumph Daytona 660"],
    "Scooters": ["Vespa GTS 300", "Honda PCX125", "Yamaha NMAX", "Aprilia Scarlett 50", "BMW C 400 GT"],
    "Superbikes": ["Kawasaki Ninja ZX-14", "Suzuki Hayabusa", "Ducati Panigale", "Yamaha YZF-R6", "Triumph Speed Triple"],
    "Electric bikes": ["Zero SR/F", "Energica Ego", "Harley-Davidson LiveWire", "Canadian Electric Bike", "Specialized Turbo"],
    "Cars": ["Toyota Camry", "Honda Civic", "Ford Mustang", "BMW 3 Series", "Audi A4"],
    "Supercars": ["Ferrari F8 Tributo", "Lamborghini Huracan", "McLaren 720S", "Porsche 911 Turbo", "Aston Martin DB11"],
    "Luxury cars": ["Rolls-Royce Phantom", "Mercedes S-Class", "BMW 7 Series", "Audi A8", "Lexus LS"],
    "SUVs": ["Range Rover Sport", "BMW X5", "Mercedes GLE", "Toyota Land Cruiser", "Ford Explorer"],
    "Electric cars": ["Tesla Model S", "Porsche Taycan", "Lucid Air", "Rivian R1T", "Ford Mustang Mach-E"],
    "Vintage and classic vehicles": ["Ford Model T", "Chevrolet Corvette C1", "Jaguar E-Type", "Porsche 911 Carrera RS", "Ferrari 250 GTO"],
    "Racing cars": ["Formula 1 Car", "NASCAR Chevrolet", "DTM BMW M3", "F3 Dallara", "LMP1 Porsche 919"],
    "Modified vehicles": ["Racing Honda Civic", "Drift Nissan Skyline", "Show Car Toyota Supra", "Custom Harley Street 750", "Tuner Mazda RX-7"],
    "Upcoming vehicles": ["2025 Tesla Cybertruck", "2025 Ford Mustang EV", "2025 BMW i5", "2025 Audi Q6", "2025 Hyundai Ioniq 7"],
    "Automobile brands": ["Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Hyundai", "Kia", "Nissan"],
    "Engines and automotive technology": ["Turbocharged Engines", "Hybrid Systems", "Electric Motors", "Direct Injection", "CVT Transmissions"]
}


def load_published_topics() -> set:
    """Load set of already published topics"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('topics', []))
    return set()


def save_topic(topic: str, vehicle_name: str = None):
    """Save a published topic to history"""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    topics = load_published_topics()
    topics.add(topic)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump({'topics': list(topics), 'last_updated': datetime.now().isoformat()}, f, indent=2)


def select_random_topic() -> Dict:
    """Select a random topic that hasn't been published recently"""
    published = load_published_topics()
    
    # Try to find an unpublished topic
    available_topics = [t for t in TOPICS if t not in published or len(published) < 10]
    
    if not available_topics:
        # Reset if all topics published
        available_topics = TOPICS
    
    category = random.choice(available_topics)
    
    # Get a specific vehicle from the category
    if category in SUBCATEGORIES:
        vehicle = random.choice(SUBCATEGORIES[category])
    else:
        vehicle = category
    
    return {
        'category': category,
        'vehicle': vehicle,
        'timestamp': datetime.now().isoformat()
    }


def get_topic_history() -> List[Dict]:
    """Get history of published topics"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {'topics': [], 'last_updated': None}


def select_topic() -> Dict:
    """Select a random topic - module-level function for admin panel import"""
    return select_random_topic()


class Topic:
    """Represents a vehicle topic"""
    def __init__(self, category_key: str, vehicle_name: str, vehicle_year: int = None):
        self.category_key = category_key
        self.vehicle_name = vehicle_name
        self.vehicle_year = vehicle_year or datetime.now().year
        self.id = f"{vehicle_name}_{self.vehicle_year}"
    
    def __dict__(self):
        return {
            'category_key': self.category_key,
            'vehicle_name': self.vehicle_name,
            'vehicle_year': self.vehicle_year,
            'id': self.id
        }


class TopicSelector:
    """Class-based topic selector for admin panel"""
    
    def __init__(self):
        self.history_file = HISTORY_FILE
    
    def select_topic(self) -> Dict:
        """Select a random topic"""
        return select_random_topic()
    
    def mark_published(self, topic: Topic, image_path: str, post_id: str, caption: str, hashtags: List[str]):
        """Mark a topic as published"""
        save_topic(topic.vehicle_name, topic.vehicle_name)
    
    def get_stats(self) -> Dict:
        """Get topic statistics"""
        history = get_topic_history()
        topics = history.get('topics', [])
        
        by_category = {}
        for t in topics:
            for cat, vehicles in SUBCATEGORIES.items():
                if t in vehicles:
                    by_category[cat] = by_category.get(cat, 0) + 1
                    break
        
        return {
            'total_published': len(topics),
            'by_category': by_category,
            'last_updated': history.get('last_updated')
        }
    
    def get_published_history(self, limit: int = 50, category: str = None) -> List[Dict]:
        """Get published topics history"""
        history = get_topic_history()
        topics = history.get('topics', [])
        return [{'topic': t, 'timestamp': history.get('last_updated')} for t in topics[:limit]]
    
    def delete_topic(self, topic_id: str):
        """Delete a topic from history"""
        topics = load_published_topics()
        topics.discard(topic_id)
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump({'topics': list(topics), 'last_updated': datetime.now().isoformat()}, f, indent=2)


# Export VEHICLE_CATEGORIES for admin panel
VEHICLE_CATEGORIES = {
    "Bikes and motorcycles": {
        "name": "Bikes and Motorcycles",
        "description": "All types of two-wheelers",
        "examples": SUBCATEGORIES["Bikes and motorcycles"],
        "hashtags": ["#bikes", "#motorcycles", "#riding"]
    },
    "Sports bikes": {
        "name": "Sports Bikes",
        "description": "High-performance motorcycles",
        "examples": SUBCATEGORIES["Sports bikes"],
        "hashtags": ["#sportbikes", "#racing", "#performance"]
    },
    "Scooters": {
        "name": "Scooters",
        "description": "Urban mobility vehicles",
        "examples": SUBCATEGORIES["Scooters"],
        "hashtags": ["#scooter", "#urban", "#commute"]
    },
    "Superbikes": {
        "name": "Superbikes",
        "description": "Top-tier performance bikes",
        "examples": SUBCATEGORIES["Superbikes"],
        "hashtags": ["#superbike", "#speed", "#track"]
    },
    "Electric bikes": {
        "name": "Electric Bikes",
        "description": "E-bikes and electric motorcycles",
        "examples": SUBCATEGORIES["Electric bikes"],
        "hashtags": ["#ebike", "#electric", "#green"]
    },
    "Cars": {
        "name": "Cars",
        "description": "Regular passenger cars",
        "examples": SUBCATEGORIES["Cars"],
        "hashtags": ["#cars", "#automotive", "#driving"]
    },
    "Supercars": {
        "name": "Supercars",
        "description": "High-performance luxury cars",
        "examples": SUBCATEGORIES["Supercars"],
        "hashtags": ["#supercar", "#luxury", "#exotic"]
    },
    "Luxury cars": {
        "name": "Luxury Cars",
        "description": "Premium vehicles",
        "examples": SUBCATEGORIES["Luxury cars"],
        "hashtags": ["#luxurycars", "#premium", "#comfort"]
    },
    "SUVs": {
        "name": "SUVs",
        "description": "Sport utility vehicles",
        "examples": SUBCATEGORIES["SUVs"],
        "hashtags": ["#suv", "#crossover", "#adventure"]
    },
    "Electric cars": {
        "name": "Electric Cars",
        "description": "Battery-powered vehicles",
        "examples": SUBCATEGORIES["Electric cars"],
        "hashtags": ["#electriccars", "#ev", "#sustainable"]
    },
    "Vintage and classic vehicles": {
        "name": "Vintage & Classic",
        "description": "Historic vehicles",
        "examples": SUBCATEGORIES["Vintage and classic vehicles"],
        "hashtags": ["#vintage", "#classic", "#retro"]
    },
    "Racing cars": {
        "name": "Racing Cars",
        "description": "Track and motorsport vehicles",
        "examples": SUBCATEGORIES["Racing cars"],
        "hashtags": ["#racing", "#motorsport", "#formula1"]
    },
    "Modified vehicles": {
        "name": "Modified Vehicles",
        "description": "Custom and modified cars",
        "examples": SUBCATEGORIES["Modified vehicles"],
        "hashtags": ["#modified", "#custom", "#tuning"]
    },
    "Upcoming vehicles": {
        "name": "Upcoming Vehicles",
        "description": "New launches and concepts",
        "examples": SUBCATEGORIES["Upcoming vehicles"],
        "hashtags": ["#upcoming", "#new", "#launch"]
    },
    "Automobile brands": {
        "name": "Automobile Brands",
        "description": "Car manufacturers",
        "examples": SUBCATEGORIES["Automobile brands"],
        "hashtags": ["#brand", "#manufacturer", "#auto"]
    },
    "Engines and automotive technology": {
        "name": "Engines & Technology",
        "description": "Technical innovations",
        "examples": SUBCATEGORIES["Engines and automotive technology"],
        "hashtags": ["#technology", "#engineering", "#innovation"]
    }
}