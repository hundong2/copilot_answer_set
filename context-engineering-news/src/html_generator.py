#!/usr/bin/env python3
"""
HTML Newsletter Generator for Context Engineering Daily
"""

import json
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter
from jinja2 import Template
import logging

logger = logging.getLogger(__name__)

class NewsletterGenerator:
    def __init__(self, config_path: str = "config"):
        with open(f"{config_path}/categories.json", 'r') as f:
            self.categories_config = json.load(f)
        
        # Category icons mapping
        self.category_icons = {
            "prompt_engineering": "🎨",
            "in_context_learning": "🧠",
            "chain_of_thought": "🔗",
            "rag_retrieval": "🔍",
            "context_management": "📋",
            "multimodal_context": "🌍",
            "tools_frameworks": "🔧",
            "research_papers": "📜",
            "industry_news": "🏢"
        }
    
    def load_news_data(self, data_file: str = "data/daily_news.json") -> Dict[str, Any]:
        """Load news data from JSON file"""
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def format_date(self, date_string: str) -> str:
        """Format date string for display"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%b %d, %Y')
        except:
            return date_string
    
    def get_trending_keywords(self, items: List[Dict]) -> List[str]:
        """Extract trending keywords from all items"""
        all_keywords = []
        for item in items:
            all_keywords.extend(item.get('keywords', []))
        
        # Count and return top keywords
        keyword_counts = Counter(all_keywords)
        return [kw for kw, count in keyword_counts.most_common(10)]
    
    def organize_by_category(self, items: List[Dict]) -> Dict[str, Dict]:
        """Organize news items by category"""
        categories = {}
        
        for item in items:
            category_id = item.get('category', 'industry_news')
            
            if category_id not in categories:
                category_config = self.categories_config['categories'].get(
                    category_id, 
                    {'name': category_id.replace('_', ' ').title(), 'description': ''}
                )
                
                categories[category_id] = {
                    'name': category_config['name'],
                    'description': category_config['description'],
                    'icon': self.category_icons.get(category_id, '📰'),
                    'news_items': []  # Changed from 'items' to avoid conflict with dict.items()
                }
            
            # Format item for template
            formatted_item = {
                'title': item['title'],
                'url': item['url'],
                'description': item['description'],
                'published_date_formatted': self.format_date(item['published_date']),
                'source': item['source'],
                'keywords': item.get('keywords', []),
                'score': item.get('score', 0.0)
            }
            
            categories[category_id]['news_items'].append(formatted_item)
        
        # Sort items within each category by score and date
        for category_data in categories.values():
            category_data['news_items'].sort(
                key=lambda x: (x['score'], x['published_date_formatted']), 
                reverse=True
            )
            # Add count for template
            category_data['count'] = len(category_data['news_items'])
        
        return categories
    
    def generate_html(self, data_file: str = "data/daily_news.json", 
                     template_file: str = "templates/newsletter.html",
                     output_file: str = "docs/index.html") -> str:
        """Generate HTML newsletter"""
        # Load data
        news_data = self.load_news_data(data_file)
        items = news_data['items']
        
        # Organize data
        categories = self.organize_by_category(items)
        trending_keywords = self.get_trending_keywords(items)
        
        # Get unique sources
        sources = list(set(item['source'] for item in items))
        
        # Load template
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        template = Template(template_content)
        
        # Template data
        template_data = {
            'date': datetime.now().strftime('%B %d, %Y'),
            'generation_time': datetime.now().strftime('%H:%M UTC'),
            'total_items': len(items),
            'categories_count': len([cat for cat in categories.values() if cat['news_items']]),
            'sources_count': len(sources),
            'trending_keywords': trending_keywords,
            'categories': categories
        }
        
        # Generate HTML
        html_content = template.render(**template_data)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML newsletter: {output_file}")
        return html_content
    
    def generate_summary_stats(self, data_file: str = "data/daily_news.json") -> Dict:
        """Generate summary statistics"""
        news_data = self.load_news_data(data_file)
        items = news_data['items']
        
        # Category distribution
        category_dist = Counter(item.get('category', 'unknown') for item in items)
        
        # Source distribution
        source_dist = Counter(item['source'] for item in items)
        
        # Score distribution
        high_quality = len([item for item in items if item.get('score', 0) >= 0.7])
        medium_quality = len([item for item in items if 0.4 <= item.get('score', 0) < 0.7])
        low_quality = len([item for item in items if item.get('score', 0) < 0.4])
        
        return {
            'total_items': len(items),
            'generation_time': news_data.get('generated_at'),
            'category_distribution': dict(category_dist),
            'source_distribution': dict(source_dist),
            'quality_distribution': {
                'high': high_quality,
                'medium': medium_quality,
                'low': low_quality
            }
        }

def main():
    """Main function to generate newsletter"""
    generator = NewsletterGenerator()
    
    # Generate HTML newsletter
    html_content = generator.generate_html()
    
    # Generate and display stats
    stats = generator.generate_summary_stats()
    
    print(f"📰 Newsletter Generated Successfully!")
    print(f"Total items: {stats['total_items']}")
    print(f"Generated at: {stats['generation_time']}")
    print("\nCategory distribution:")
    for category, count in stats['category_distribution'].items():
        print(f"  {category}: {count}")
    
    print("\nSource distribution:")
    for source, count in stats['source_distribution'].items():
        print(f"  {source}: {count}")
    
    print("\nQuality distribution:")
    print(f"  High relevance (70%+): {stats['quality_distribution']['high']}")
    print(f"  Medium relevance (40-69%): {stats['quality_distribution']['medium']}")
    print(f"  Low relevance (<40%): {stats['quality_distribution']['low']}")

if __name__ == "__main__":
    main()
