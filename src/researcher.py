"""Researcher module for InstaNote - researches vehicle specifications"""

import requests
from typing import Dict, Optional
from datetime import datetime
import re
import json
from pathlib import Path

CACHE_FILE = Path(__file__).parent.parent / "data" / "research_cache.json"


def load_cache() -> Dict:
    """Load research cache"""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_cache(data: Dict):
    """Save research cache"""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def research_vehicle(vehicle_name: str) -> Dict:
    """Research a vehicle and return specifications"""
    cache = load_cache()
    
    if vehicle_name in cache:
        return cache[vehicle_name]
    
    # Use Wikipedia API for vehicle information
    specs = {
        'name': vehicle_name,
        'manufacturer': '',
        'launch_year': '',
        'history': '',
        'engine_specs': {},
        'dimensions': {},
        'features': [],
        'price': '',
        'colors': [],
        'research_timestamp': datetime.now().isoformat()
    }
    
    try:
        # Search Wikipedia
        search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + vehicle_name.replace(' ', '_')
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            specs['manufacturer'] = extract_manufacturer(vehicle_name)
            specs['launch_year'] = extract_year(vehicle_name)
            specs['description'] = data.get('extract', '')
    except Exception as e:
        pass
    
    # Get detailed specs from cached knowledge base
    specs = get_vehicle_specs(vehicle_name, specs)
    
    cache[vehicle_name] = specs
    save_cache(cache)
    
    return specs


def extract_manufacturer(vehicle_name: str) -> str:
    """Extract manufacturer from vehicle name"""
    manufacturers = [
        'Harley-Davidson', 'Yamaha', 'Ducati', 'Royal Enfield', 'Kawasaki',
        'Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen',
        'Porsche', 'Ferrari', 'Lamborghini', 'McLaren', 'Aston Martin',
        'Rolls-Royce', 'Lexus', 'Jaguar', 'Maserati', 'Chevrolet', 'Nissan',
        'Hyundai', 'Kia', 'Subaru', 'Mazda', 'Tesla', 'Lucid', 'Rivian',
        'Zero', 'Energica', 'Canadian', 'Specialized', 'Vespa', 'Aprilia',
        'Suzuki', 'Honda', 'Peugeot', 'Piaggio', 'Kymco', 'Giant'
    ]
    
    for manuf in manufacturers:
        if manuf.lower() in vehicle_name.lower():
            return manuf
    return vehicle_name.split()[0] if vehicle_name else ''


def extract_year(vehicle_name: str) -> str:
    """Extract launch year from vehicle name"""
    years = re.findall(r'(19|20)\d{2}', vehicle_name)
    return years[0] if years else 'N/A'


def get_vehicle_specs(vehicle_name: str, specs: Dict) -> Dict:
    """Get detailed vehicle specifications from knowledge base"""
    
    # Knowledge base of vehicle specifications
    knowledge_base = {
        'Ducati Panigale V4': {
            'manufacturer': 'Ducati',
            'launch_year': '2018',
            'engine': '1289 cc Testastretta DVT',
            'horsepower': '157 hp @ 10,500 rpm',
            'torque': '106.9 lb-ft @ 9,000 rpm',
            'mileage': '15-18 km/l',
            'top_speed': '300 km/h',
            'transmission': '6-speed Ducati Quick Shift',
            'suspension': 'Öhlins NPX 2018 fork, Sachs rear shock',
            'brakes': 'Brembo Stylema 4-piston calipers',
            'dimensions': {'length': '2070 mm', 'width': '810 mm', 'height': '1160 mm'},
            'weight': '182 kg',
            'features': ['Cornering ABS', 'Ducati Traction Control', 'Quick Shifter', 'Full LED'],
            'price': '$22,995',
            'colors': ['Red', 'Black', 'White', 'Blue']
        },
        'Tesla Model S': {
            'manufacturer': 'Tesla',
            'launch_year': '2012',
            'engine': 'Dual Electric Motors',
            'horsepower': '670 hp (Plaid)',
            'torque': '1,050 lb-ft',
            'range': '405 miles (Plaid)',
            'top_speed': '200 mph',
            'transmission': 'Single-speed',
            'suspension': 'Adaptive air suspension',
            'brakes': 'Regenerative braking, 4-wheel disc',
            'dimensions': {'length': '4970 mm', 'width': '1964 mm', 'height': '1446 mm'},
            'weight': '2140 kg',
            'battery': '100 kWh',
            'features': ['Autopilot', 'FSD Computer', '17" touchscreen', 'Keyless entry'],
            'price': '$104,990 (Plaid)',
            'colors': ['Deep Blue Metallic', 'Red', 'White', 'Black', 'Silver']
        },
        'Ferrari F8 Tributo': {
            'manufacturer': 'Ferrari',
            'launch_year': '2020',
            'engine': '3.9L V8 twin-turbo',
            'horsepower': '710 hp @ 8,000 rpm',
            'torque': '568 lb-ft @ 3,000-5,750 rpm',
            'mileage': '12-14 km/l',
            'top_speed': '340 km/h',
            'transmission': '7-speed DCT',
            'suspension': 'Double wishbone, magnetorheological dampers',
            'brakes': 'Carbon-ceramic, 4-piston calipers',
            'dimensions': {'length': '4644 mm', 'width': '1998 mm', 'height': '1219 mm'},
            'weight': '1570 kg',
            'features': ['Active aerodynamics', 'F1-derived tech', 'Cockpit styling', 'Lap time performance'],
            'price': '$185,000',
            'colors': ['Rosso Corsa', 'Blu Pozzi', 'Yellow', 'Black', 'White']
        },
        'BMW S1000RR': {
            'manufacturer': 'BMW',
            'launch_year': '2009',
            'engine': '999 cc inline-4',
            'horsepower': '205 hp @ 13,500 rpm',
            'torque': '83 lb-ft @ 10,500 rpm',
            'mileage': '18-22 km/l',
            'top_speed': '299 km/h',
            'transmission': '6-speed',
            'suspension': 'White Power fork, rear monoshock',
            'brakes': 'Brembo 4-piston radials',
            'dimensions': {'length': '2055 mm', 'width': '836 mm', 'height': '1215 mm'},
            'weight': '169 kg',
            'features': ['Ride Modes', 'Dynamic Traction Control', 'Quick Shifter', 'LED indicators'],
            'price': '$16,995',
            'colors': ['White', 'Black', 'Blue', 'Red', 'Silver']
        },
        'Range Rover Sport': {
            'manufacturer': 'Land Rover',
            'launch_year': '2005',
            'engine': '3.0L V6 mild-hybrid / 4.4L V8 diesel',
            'horsepower': '395 hp (PHEV)',
            'torque': '600 lb-ft (diesel)',
            'mileage': '12-18 km/l',
            'top_speed': '250 km/h',
            'transmission': '8-speed automatic',
            'suspension': 'Adaptive air suspension',
            'brakes': 'Ventilated discs, ABS',
            'dimensions': {'length': '4756 mm', 'width': '1958 mm', 'height': '1750 mm'},
            'weight': '2350 kg',
            'features': ['Terrain Response', 'All-wheel drive', 'Panoramic roof', 'Massage seats'],
            'price': '$71,000',
            'colors': ['White', 'Black', 'Grey', 'Red', 'Blue']
        },
        'Lamborghini Huracan': {
            'manufacturer': 'Lamborghini',
            'launch_year': '2014',
            'engine': '5.2L V10 naturally aspirated',
            'horsepower': '602 hp @ 8,000 rpm',
            'torque': '405 lb-ft @ 5,500 rpm',
            'mileage': '8-10 km/l',
            'top_speed': '325 km/h',
            'transmission': '7-speed DNA',
            'suspension': 'Double wishbone, magnetorheological',
            'brakes': 'Carbon-ceramic, 4-piston',
            'dimensions': {'length': '4430 mm', 'width': '1930 mm', 'height': '1240 mm'},
            'weight': '1420 kg',
            'features': ['Lamborghini Drive Select', 'Corsa mode', 'Aerodynamic flaps', 'Laser headlights'],
            'price': '$275,000',
            'colors': ['Giallo Orion', 'Verde Iago', 'Rosso Corsa', 'Nero Noctis', 'Blu Siracusa']
        },
        'Royal Enfield Classic 350': {
            'manufacturer': 'Royal Enfield',
            'launch_year': '2020',
            'engine': '349 cc single-cylinder',
            'horsepower': '20.2 hp @ 5,250 rpm',
            'torque': '26.2 Nm @ 3,500 rpm',
            'mileage': '35-40 km/l',
            'top_speed': '130 km/h',
            'transmission': '5-speed',
            'suspension': 'Telescopic fork, swingarm',
            'brakes': 'Disc front, drum rear, ABS',
            'dimensions': {'length': '2140 mm', 'width': '790 mm', 'height': '1110 mm'},
            'weight': '191 kg',
            'features': ['UCE engine', 'LED lighting', 'Digital console', 'Tubeless tires'],
            'price': '$3,999',
            'colors': ['Classic Black', 'Royal Enfield Blue', 'Red', 'Grey', 'White']
        },
        'Porsche 911 Turbo': {
            'manufacturer': 'Porsche',
            'launch_year': '1975',
            'engine': '3.8L twin-turbo flat-6',
            'horsepower': '572 hp @ 6,500 rpm',
            'torque': '590 lb-ft @ 2,250 rpm',
            'mileage': '10-12 km/l',
            'top_speed': '330 km/h',
            'transmission': '8-speed PDK',
            'suspension': 'Adaptive dampers, air suspension',
            'brakes': 'Porsche Ceramic Composite',
            'dimensions': {'length': '4504 mm', 'width': '1880 mm', 'height': '1310 mm'},
            'weight': '1640 kg',
            'features': ['All-wheel drive', 'Active suspension', 'Sport Chrono', 'Mode switch'],
            'price': '$205,000',
            'colors': [' Guards Red', 'Racing Yellow', 'Black', 'White', 'Silver']
        }
    }
    
    # Find matching vehicle
    for key, data in knowledge_base.items():
        if key.lower() in vehicle_name.lower() or vehicle_name.lower() in key.lower():
            return {**specs, **data}
    
    # Default specs if not found
    return {
        **specs,
        'manufacturer': extract_manufacturer(vehicle_name),
        'launch_year': extract_year(vehicle_name),
        'engine': 'See specifications',
        'horsepower': 'N/A',
        'torque': 'N/A',
        'mileage': 'N/A',
        'top_speed': 'N/A',
        'transmission': 'N/A',
        'suspension': 'N/A',
        'brakes': 'N/A',
        'dimensions': {'length': 'N/A', 'width': 'N/A', 'height': 'N/A'},
        'weight': 'N/A',
        'features': ['Advanced technology', 'Premium features'],
        'price': 'Contact dealer',
        'colors': ['Multiple options']
    }


def generate_caption(vehicle_specs: Dict) -> str:
    """Generate Instagram caption for vehicle"""
    name = vehicle_specs.get('name', 'Vehicle')
    hp = vehicle_specs.get('horsepower', 'N/A')
    torque = vehicle_specs.get('torque', 'N/A')
    top_speed = vehicle_specs.get('top_speed', 'N/A')
    price = vehicle_specs.get('price', 'N/A')
    
    caption = f"""🚗 {name}

⚡ {hp} | 🔧 {torque} | 🚀 {top_speed}
💰 {price}

#VehicleSpecs #CarEnthusiast #BikeLife #Automotive #Supercar #Motorcycle #InstaNote"""
    
    return caption


def generate_hashtags(vehicle_specs: Dict) -> list:
    """Generate relevant hashtags for vehicle"""
    base_tags = [
        '#VehicleSpecs', '#CarEnthusiast', '#BikeLife', '#Automotive',
        '#InstaNote', '#CarLovers', '#Motorcycle', '#Supercar', '#LuxuryCars',
        '#SUV', '#ElectricCars', '#ClassicCars', '#Racing', '#ModifiedCars'
    ]
    
    manufacturer = vehicle_specs.get('manufacturer', '').lower()
    if manufacturer:
        base_tags.append(f'#{manufacturer.replace(" ", "")}')
    
    return base_tags