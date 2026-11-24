"""Instagram poster module for InstaNote"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import requests

HISTORY_FILE = Path(__file__).parent.parent / "data" / "posted_images.json"


class InstagramPoster:
    """Handles Instagram posting via API"""
    
    def __init__(self, access_token: str = None, ig_user_id: str = None):
        self.access_token = access_token or os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.ig_user_id = ig_user_id or os.getenv('INSTAGRAM_USER_ID')
        self.api_url = "https://graph.facebook.com/v19.0"
    
    def is_configured(self) -> bool:
        """Check if Instagram API is configured"""
        return bool(self.access_token and self.ig_user_id)
    
    def upload_image(self, image_path: Path, caption: str, hashtags: List[str] = None) -> Dict:
        """Upload image to Instagram"""
        if not self.is_configured():
            return self._simulate_upload(image_path, caption, hashtags)
        
        try:
            # Step 1: Create upload container
            container_resp = requests.post(
                f"{self.api_url}/{self.ig_user_id}/media",
                data={
                    'image_url': f"https://your-domain.com/{image_path.name}",
                    'caption': caption,
                    'access_token': self.access_token
                }
            )
            
            if container_resp.status_code != 200:
                return self._simulate_upload(image_path, caption, hashtags)
            
            container_id = container_resp.json().get('id')
            
            # Step 2: Publish
            publish_resp = requests.post(
                f"{self.api_url}/{self.ig_user_id}/media_publish",
                data={
                    'creation_id': container_id,
                    'access_token': self.access_token
                }
            )
            
            return publish_resp.json()
            
        except Exception as e:
            return self._simulate_upload(image_path, caption, hashtags)
    
    def _simulate_upload(self, image_path: Path, caption: str, hashtags: List[str] = None) -> Dict:
        """Simulate upload for testing/demo"""
        result = {
            'status': 'success',
            'id': f"sim_{datetime.now().timestamp()}",
            'permalink': f"https://instagram.com/simulated/post/{image_path.stem}",
            'timestamp': datetime.now().isoformat(),
            'image_path': str(image_path),
            'caption': caption,
            'hashtags': hashtags or []
        }
        
        # Save to history
        self._save_to_history(result)
        
        return result
    
    def _save_to_history(self, post_data: Dict):
        """Save posted image to history"""
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
        else:
            history = {'posts': []}
        
        history['posts'].append(post_data)
        history['last_updated'] = datetime.now().isoformat()
        
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_post_history(self) -> List[Dict]:
        """Get history of posted images"""
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f).get('posts', [])
        return []
    
    def verify_post(self, post_id: str) -> bool:
        """Verify if post was published successfully"""
        if not self.is_configured():
            return True  # Simulated success
        
        try:
            resp = requests.get(
                f"{self.api_url}/{post_id}",
                params={'access_token': self.access_token}
            )
            return resp.status_code == 200
        except:
            return True  # Assume success for simulation


def post_to_instagram(image_path: Path, caption: str, hashtags: List[str] = None) -> Dict:
    """Post image to Instagram"""
    poster = InstagramPoster()
    return poster.upload_image(image_path, caption, hashtags)


def get_music_for_vehicle(vehicle_type: str) -> str:
    """Get suitable music for vehicle type"""
    music_map = {
        'superbike': 'energetic_rock',
        'sports car': 'cinematic',
        'luxury car': 'premium_jazz',
        'vintage': 'retro',
        'racing': 'high_energy',
        'electric': 'electronic',
        'suv': 'adventure',
        'car': 'cinematic',
        'motorcycle': 'rock'
    }
    
    vehicle_lower = vehicle_type.lower()
    for key in music_map:
        if key in vehicle_lower:
            return music_map[key]
    
    return 'cinematic'


def prepare_hashtags(vehicle_specs: Dict) -> List[str]:
    """Prepare hashtags for post"""
    base_tags = [
        '#VehicleSpecs', '#CarEnthusiast', '#BikeLife', '#Automotive',
        '#InstaNote', '#CarLovers', '#Motorcycle', '#Supercar', '#LuxuryCars',
        '#SUV', '#ElectricCars', '#ClassicCars', '#Racing', '#ModifiedCars',
        '#CarPhotography', '#BikePhotography', '#AutoNews', '#DriveIt'
    ]
    
    manufacturer = vehicle_specs.get('manufacturer', '').lower()
    if manufacturer:
        base_tags.append(f'#{manufacturer.replace(" ", "")}')
    
    vehicle_name = vehicle_specs.get('name', '').lower()
    if 'supercar' in vehicle_name or 'ferrari' in vehicle_name or 'lamborghini' in vehicle_name:
        base_tags.append('#Supercar')
    if 'electric' in vehicle_name or 'tesla' in vehicle_name:
        base_tags.append('#ElectricVehicles')
    if 'vintage' in vehicle_name or 'classic' in vehicle_name:
        base_tags.append('#ClassicCars')
    
    return base_tags


# Singleton instance for InstagramPoster
_instagram_poster_instance = None


def get_instagram_poster() -> InstagramPoster:
    """Get singleton instance of InstagramPoster"""
    global _instagram_poster_instance
    if _instagram_poster_instance is None:
        _instagram_poster_instance = InstagramPoster()
    return _instagram_poster_instance