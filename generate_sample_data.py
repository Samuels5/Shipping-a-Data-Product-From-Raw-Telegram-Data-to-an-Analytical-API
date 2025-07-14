"""
Sample data generator for testing purposes.
Generates mock Telegram data that follows the same structure as real data.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import uuid

from src.config import Config

class SampleDataGenerator:
    """Generates sample Telegram data for testing."""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Sample medical product names
        self.medical_products = [
            "paracetamol", "ibuprofen", "aspirin", "amoxicillin", "metformin",
            "vitamin d", "vitamin c", "calcium", "iron tablets", "bandages",
            "insulin", "antibiotics", "pain relief", "antiseptic", "thermometer",
            "blood pressure monitor", "glucose meter", "surgical mask", "gloves",
            "syringes", "dextrose", "saline", "antihistamine", "cough syrup"
        ]
        
        # Sample message templates
        self.message_templates = [
            "🏥 {product} available now at discounted price!",
            "💊 New stock of {product} arrived. Contact us for orders.",
            "🔥 Special offer on {product} - Limited time only!",
            "📞 Call us for {product} delivery. Fast and reliable service.",
            "✅ Quality {product} certified by health ministry.",
            "🚚 Free delivery on {product} orders above 500 birr.",
            "⚡ Emergency supply of {product} available 24/7.",
            "🏪 Visit our pharmacy for authentic {product}.",
            "💰 Best price guarantee on {product} in Addis Ababa.",
            "📋 {product} - Check our catalog for more details."
        ]
        
        # Sample channel names
        self.channels = [
            "chemed_et",
            "lobelia4cosmetics",
            "tikvahpharma",
            "ethiopian_pharmacy",
            "medical_supplies_et"
        ]
    
    def generate_sample_message(self, channel_name: str, base_date: datetime) -> Dict[str, Any]:
        """Generate a single sample message."""
        
        # Random message ID
        message_id = random.randint(1000, 999999)
        
        # Random product and message
        product = random.choice(self.medical_products)
        template = random.choice(self.message_templates)
        text = template.format(product=product)
        
        # Random date within the last few days
        date_offset = timedelta(
            days=random.randint(0, 7),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        message_date = base_date - date_offset
        
        # Random media presence
        has_media = random.choice([True, False, False])  # 1/3 chance of having media
        media_type = None
        image_path = None
        
        if has_media:
            media_type = random.choice(["photo", "image"])
            # Generate a fake image path
            image_path = f"images/{channel_name}/{message_date.strftime('%Y-%m-%d')}/img_{message_id}.jpg"
        
        message_data = {
            'message_id': message_id,
            'channel_name': channel_name,
            'date': message_date.isoformat(),
            'text': text,
            'sender_id': random.randint(100000, 999999),
            'has_media': has_media,
            'media_type': media_type,
            'image_path': image_path,
            'scraped_at': datetime.now().isoformat(),
            'raw_data': {
                'views': random.randint(10, 1000) if random.random() > 0.3 else None,
                'forwards': random.randint(0, 50) if random.random() > 0.7 else None,
                'replies': None,
                'edit_date': None,
                'grouped_id': None
            }
        }
        
        return message_data
    
    def generate_channel_data(
        self, 
        channel_name: str, 
        num_messages: int = 50,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Generate sample data for a channel."""
        
        base_date = datetime.now()
        messages = []
        
        for _ in range(num_messages):
            message = self.generate_sample_message(channel_name, base_date)
            messages.append(message)
        
        # Sort by date (newest first)
        messages.sort(key=lambda x: x['date'], reverse=True)
        
        return messages
    
    def save_sample_data(self, num_messages_per_channel: int = 50):
        """Generate and save sample data for all channels."""
        
        # Create data lake directory
        data_lake_path = Path(self.config.DATA_LAKE_PATH)
        date_str = datetime.now().strftime('%Y-%m-%d')
        messages_dir = data_lake_path / 'telegram_messages' / date_str
        messages_dir.mkdir(parents=True, exist_ok=True)
        
        total_messages = 0
        
        for channel in self.channels:
            print(f"Generating sample data for {channel}...")
            
            # Generate messages
            messages = self.generate_channel_data(
                channel, 
                num_messages_per_channel
            )
            
            # Save to JSON file
            file_path = messages_dir / f'{channel}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            total_messages += len(messages)
            print(f"Saved {len(messages)} messages for {channel}")
        
        print(f"Total sample messages generated: {total_messages}")
        print(f"Data saved to: {messages_dir}")
        
        return total_messages
    
    def generate_sample_images(self, num_images: int = 20):
        """Generate placeholder image files for testing."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            for channel in self.channels:
                for i in range(num_images // len(self.channels)):
                    # Create directory
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    image_dir = Path(self.config.DATA_LAKE_PATH) / 'images' / channel / date_str
                    image_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create a simple placeholder image
                    img = Image.new('RGB', (300, 200), color='lightblue')
                    draw = ImageDraw.Draw(img)
                    
                    # Add some text
                    text = f"{channel}\nSample Image {i+1}"
                    draw.text((50, 80), text, fill='black')
                    
                    # Save image
                    image_path = image_dir / f'sample_{i+1}.jpg'
                    img.save(image_path)
            
            print(f"Generated {num_images} sample images")
            
        except ImportError:
            print("PIL not available. Skipping image generation.")


def main():
    """Generate sample data."""
    print("Generating sample Telegram data...")
    
    # Initialize configuration
    config = Config()
    
    # Create generator
    generator = SampleDataGenerator(config)
    
    # Generate sample data
    total_messages = generator.save_sample_data(num_messages_per_channel=100)
    
    # Generate sample images
    generator.generate_sample_images(num_images=30)
    
    print(f"Sample data generation complete!")
    print(f"Generated {total_messages} messages across {len(generator.channels)} channels")
    print("You can now run the data loader to load this data into the database.")


if __name__ == "__main__":
    main()
