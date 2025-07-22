#!/usr/bin/env python3
"""
RSS Feed Generator for Context Engineering Daily News
"""

import json
from datetime import datetime, timezone
from typing import Dict, List
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import html
import logging

logger = logging.getLogger(__name__)

class RSSGenerator:
    def __init__(self):
        self.site_url = "https://your-username.github.io/context-engineering-news"
        self.feed_title = "Context Engineering Daily"
        self.feed_description = "Daily news and research updates in AI Context Engineering, Prompt Engineering, RAG, and LLM development"
        self.feed_language = "en-us"
        self.feed_copyright = f"Copyright {datetime.now().year} Context Engineering Daily"
    
    def load_news_data(self, data_file: str = "data/daily_news.json") -> Dict:
        """Load news data from JSON file"""
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_rss_feed(self, items: List[Dict], output_file: str = "docs/rss.xml") -> str:
        """Generate RSS 2.0 feed"""
        # Create root RSS element
        rss = Element('rss', {
            'version': '2.0',
            'xmlns:atom': 'http://www.w3.org/2005/Atom',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'
        })
        
        # Create channel element
        channel = SubElement(rss, 'channel')
        
        # Channel metadata
        SubElement(channel, 'title').text = self.feed_title
        SubElement(channel, 'link').text = self.site_url
        SubElement(channel, 'description').text = self.feed_description
        SubElement(channel, 'language').text = self.feed_language
        SubElement(channel, 'copyright').text = self.feed_copyright
        SubElement(channel, 'generator').text = "Context Engineering News Generator"
        SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Add atom:link for self-reference
        atom_link = SubElement(channel, 'atom:link', {
            'href': f"{self.site_url}/rss.xml",
            'rel': 'self',
            'type': 'application/rss+xml'
        })
        
        # Add category
        SubElement(channel, 'category').text = "Technology"
        SubElement(channel, 'category').text = "Artificial Intelligence"
        SubElement(channel, 'category').text = "Machine Learning"
        
        # Add items (limit to latest 50)
        for item_data in items[:50]:
            self.add_rss_item(channel, item_data)
        
        # Generate XML string
        rough_string = tostring(rss, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
        
        # Remove empty lines and fix encoding declaration
        xml_lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
        xml_content = '\n'.join(xml_lines)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.info(f"Generated RSS feed: {output_file}")
        return xml_content
    
    def add_rss_item(self, channel: Element, item_data: Dict):
        """Add a single item to RSS feed"""
        item = SubElement(channel, 'item')
        
        # Basic item data
        SubElement(item, 'title').text = html.escape(item_data['title'])
        SubElement(item, 'link').text = item_data['url']
        SubElement(item, 'guid', {'isPermaLink': 'false'}).text = item_data['url']
        
        # Description with HTML content
        description_html = self.format_item_description(item_data)
        SubElement(item, 'description').text = html.escape(description_html)
        
        # Enhanced content if available
        if 'ai_summary' in item_data:
            content_html = f"""
            <div>
                <h3>Summary</h3>
                <p>{html.escape(item_data['ai_summary'])}</p>
                <h3>Original Description</h3>
                <p>{html.escape(item_data['description'])}</p>
            </div>
            """
            content_elem = SubElement(item, 'content:encoded')
            content_elem.text = content_html
        
        # Publication date
        try:
            pub_date = datetime.fromisoformat(item_data['published_date'].replace('Z', '+00:00'))
            SubElement(item, 'pubDate').text = pub_date.strftime('%a, %d %b %Y %H:%M:%S %z')
        except:
            SubElement(item, 'pubDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Source
        SubElement(item, 'author').text = f"noreply@contextengineering.news ({item_data['source']})"
        
        # Categories (from keywords)
        category_name = item_data.get('category', 'general').replace('_', ' ').title()
        SubElement(item, 'category').text = category_name
        
        # Add keywords as additional categories
        for keyword in item_data.get('keywords', [])[:3]:  # Limit to 3 keywords
            SubElement(item, 'category').text = keyword
    
    def format_item_description(self, item_data: Dict) -> str:
        """Format item description with metadata"""
        description = item_data['description']
        source = item_data['source']
        
        # Add AI summary if available
        if 'ai_summary' in item_data:
            description = f"<strong>AI Summary:</strong> {item_data['ai_summary']}<br><br>{description}"
        
        # Add metadata
        metadata = f"<br><br><small><strong>Source:</strong> {source}"
        
        # Add keywords
        if item_data.get('keywords'):
            keywords = ', '.join(item_data['keywords'][:5])
            metadata += f" | <strong>Keywords:</strong> {keywords}"
        
        # Add relevance score
        if 'score' in item_data:
            score_percent = int(item_data['score'] * 100)
            metadata += f" | <strong>Relevance:</strong> {score_percent}%"
        
        metadata += "</small>"
        
        return description + metadata
    
    def generate_category_feeds(self, items: List[Dict], output_dir: str = "docs"):
        """Generate separate RSS feeds for each category"""
        # Group items by category
        categories = {}
        for item in items:
            category = item.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        category_names = {
            'prompt_engineering': 'Prompt Engineering',
            'in_context_learning': 'In-Context Learning', 
            'chain_of_thought': 'Chain-of-Thought',
            'rag_retrieval': 'RAG & Retrieval',
            'context_management': 'Context Management',
            'multimodal_context': 'Multimodal Context',
            'tools_frameworks': 'Tools & Frameworks',
            'research_papers': 'Research Papers',
            'industry_news': 'Industry News'
        }
        
        for category_id, category_items in categories.items():
            if len(category_items) < 3:  # Skip categories with too few items
                continue
            
            category_name = category_names.get(category_id, category_id.replace('_', ' ').title())
            
            # Create category-specific RSS
            rss = Element('rss', {
                'version': '2.0',
                'xmlns:atom': 'http://www.w3.org/2005/Atom'
            })
            
            channel = SubElement(rss, 'channel')
            SubElement(channel, 'title').text = f"{self.feed_title} - {category_name}"
            SubElement(channel, 'link').text = f"{self.site_url}#{category_id}"
            SubElement(channel, 'description').text = f"Latest {category_name} news in Context Engineering"
            SubElement(channel, 'language').text = self.feed_language
            
            # Add items
            for item_data in category_items[:20]:  # Limit to 20 items per category
                self.add_rss_item(channel, item_data)
            
            # Save category feed
            rough_string = tostring(rss, encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ", encoding='utf-8')
            
            xml_lines = [line for line in pretty_xml.decode('utf-8').split('\n') if line.strip()]
            xml_content = '\n'.join(xml_lines)
            
            output_file = f"{output_dir}/rss-{category_id.replace('_', '-')}.xml"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            logger.info(f"Generated category RSS feed: {output_file}")
    
    def generate_feeds(self, data_file: str = "data/daily_news.json"):
        """Generate all RSS feeds"""
        news_data = self.load_news_data(data_file)
        items = news_data['items']
        
        # Generate main RSS feed
        self.create_rss_feed(items)
        
        # Generate category-specific feeds
        self.generate_category_feeds(items)
        
        logger.info(f"Generated RSS feeds for {len(items)} items")

def main():
    """Main function to generate RSS feeds"""
    generator = RSSGenerator()
    generator.generate_feeds()
    
    print("📡 RSS feeds generated successfully!")
    print("Available feeds:")
    print(f"  - Main feed: docs/rss.xml")
    print(f"  - Category feeds: docs/rss-*.xml")

if __name__ == "__main__":
    main()
