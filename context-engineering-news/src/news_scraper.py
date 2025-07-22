#!/usr/bin/env python3
"""
Context Engineering Daily News Scraper
Collects news from various sources and categorizes them.
"""

import json
import requests
import feedparser
import re
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin, urlparse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    title: str
    url: str
    description: str
    published_date: datetime
    source: str
    category: str
    keywords: List[str]
    score: float = 0.0
    content: str = ""

class NewsScraperConfig:
    def __init__(self, config_path: str = "config"):
        with open(f"{config_path}/sources.json", 'r') as f:
            self.sources = json.load(f)
        with open(f"{config_path}/categories.json", 'r') as f:
            self.categories = json.load(f)
    
    def get_category_keywords(self) -> Dict[str, List[str]]:
        return {cat_id: cat_info['keywords'] 
                for cat_id, cat_info in self.categories['categories'].items()}

class ContextEngineeringNewsScraper:
    def __init__(self, config_path: str = "config"):
        self.config = NewsScraperConfig(config_path)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Context-Engineering-News-Bot/1.0 (Educational Purpose)'
        })
    
    def categorize_content(self, title: str, description: str) -> tuple[str, float, List[str]]:
        """Categorize content and return category, confidence score, and matched keywords"""
        text = f"{title} {description}".lower()
        category_scores = {}
        matched_keywords = []
        
        # Check each category
        for cat_id, cat_info in self.config.categories['categories'].items():
            score = 0
            cat_keywords = []
            
            for keyword in cat_info['keywords']:
                if keyword.lower() in text:
                    score += 1
                    cat_keywords.append(keyword)
            
            # Boost score for priority keywords
            for priority_kw in self.config.categories['priority_keywords']:
                if priority_kw.lower() in text:
                    score += 2
                    cat_keywords.append(priority_kw)
            
            category_scores[cat_id] = score
            if score > 0:
                matched_keywords.extend(cat_keywords)
        
        # Find best category
        best_category = max(category_scores.items(), key=lambda x: x[1])
        
        if best_category[1] == 0:
            return "industry_news", 0.1, []
        
        confidence = min(best_category[1] / 5.0, 1.0)  # Normalize to 0-1
        return best_category[0], confidence, list(set(matched_keywords))
    
    def scrape_arxiv(self, url: str) -> List[NewsItem]:
        """Scrape arXiv RSS feed"""
        logger.info(f"Scraping arXiv: {url}")
        items = []
        
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # Latest 10 papers
                # Parse arxiv date format
                pub_date = datetime(*entry.published_parsed[:6])
                
                # Skip if older than 7 days
                if pub_date < datetime.now() - timedelta(days=7):
                    continue
                
                category, score, keywords = self.categorize_content(
                    entry.title, entry.summary
                )
                
                # Only include if relevant to context engineering
                if score < 0.3:
                    continue
                
                item = NewsItem(
                    title=entry.title,
                    url=entry.link,
                    description=entry.summary[:300] + "...",
                    published_date=pub_date,
                    source="arXiv",
                    category=category,
                    keywords=keywords,
                    score=score,
                    content=entry.summary
                )
                items.append(item)
                
        except Exception as e:
            logger.error(f"Error scraping arXiv {url}: {e}")
        
        return items
    
    def scrape_rss(self, url: str, source_name: str) -> List[NewsItem]:
        """Generic RSS feed scraper"""
        logger.info(f"Scraping RSS: {source_name} - {url}")
        items = []
        
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:  # Latest 15 items
                # Parse date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                else:
                    pub_date = datetime.now()
                
                # Skip if older than 3 days for blogs
                if pub_date < datetime.now() - timedelta(days=3):
                    continue
                
                description = getattr(entry, 'summary', getattr(entry, 'description', ''))
                category, score, keywords = self.categorize_content(
                    entry.title, description
                )
                
                # Only include if relevant
                if score < 0.2:
                    continue
                
                item = NewsItem(
                    title=entry.title,
                    url=entry.link,
                    description=description[:300] + "...",
                    published_date=pub_date,
                    source=source_name,
                    category=category,
                    keywords=keywords,
                    score=score
                )
                items.append(item)
                
        except Exception as e:
            logger.error(f"Error scraping RSS {url}: {e}")
        
        return items
    
    def scrape_github_trending(self) -> List[NewsItem]:
        """Scrape GitHub trending repositories"""
        logger.info("Scraping GitHub trending repositories")
        items = []
        
        try:
            # Use GitHub API to search for relevant repositories
            queries = [
                "prompt+engineering+language:python+created:>2024-01-01",
                "LLM+context+language:python+created:>2024-01-01",
                "RAG+retrieval+language:python+created:>2024-01-01",
                "chain-of-thought+language:python+created:>2024-01-01"
            ]
            
            for query in queries:
                url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
                
                response = self.session.get(url)
                if response.status_code == 200:
                    data = response.json()
                    
                    for repo in data.get('items', [])[:5]:  # Top 5 per query
                        category, score, keywords = self.categorize_content(
                            repo['name'] + " " + repo['description'] if repo['description'] else repo['name'],
                            repo['description'] or ""
                        )
                        
                        if score < 0.3:
                            continue
                        
                        # Parse GitHub date safely
                        created_at_str = repo['created_at'].replace('Z', '+00:00')
                        try:
                            pub_date = datetime.fromisoformat(created_at_str)
                        except:
                            pub_date = datetime.now(timezone.utc)
                        
                        item = NewsItem(
                            title=f"{repo['name']} - {repo['description'] or 'GitHub Repository'}",
                            url=repo['html_url'],
                            description=repo['description'] or "No description available",
                            published_date=pub_date,
                            source="GitHub",
                            category=category,
                            keywords=keywords,
                            score=score
                        )
                        items.append(item)
                
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            logger.error(f"Error scraping GitHub: {e}")
        
        return items
    
    def scrape_all_sources(self) -> List[NewsItem]:
        """Scrape all configured sources"""
        all_items = []
        
        for source_id, source_info in self.config.sources['sources'].items():
            logger.info(f"Processing source: {source_info['name']}")
            
            try:
                if source_info['type'] == 'rss':
                    for url in source_info['urls']:
                        if 'arxiv' in url:
                            items = self.scrape_arxiv(url)
                        else:
                            items = self.scrape_rss(url, source_info['name'])
                        all_items.extend(items)
                        time.sleep(2)  # Rate limiting
                
                elif source_info['type'] == 'github_api':
                    items = self.scrape_github_trending()
                    all_items.extend(items)
                
                # Add more source types as needed
                
            except Exception as e:
                logger.error(f"Error processing source {source_id}: {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        # Sort by score and date (handle timezone-aware vs naive datetimes)
        def sort_key(item):
            date = item.published_date
            if date.tzinfo is None:
                # Make naive datetime timezone-aware (assume UTC)
                date = date.replace(tzinfo=timezone.utc)
            return (item.score, date)
        
        unique_items.sort(key=sort_key, reverse=True)
        
        logger.info(f"Collected {len(unique_items)} unique news items")
        return unique_items
    
    def save_news_data(self, items: List[NewsItem], output_file: str = "data/daily_news.json"):
        """Save news data to JSON file"""
        data = {
            "generated_at": datetime.now().isoformat(),
            "total_items": len(items),
            "items": [
                {
                    "title": item.title,
                    "url": item.url,
                    "description": item.description,
                    "published_date": item.published_date.isoformat(),
                    "source": item.source,
                    "category": item.category,
                    "keywords": item.keywords,
                    "score": item.score
                }
                for item in items
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(items)} items to {output_file}")

def main():
    """Main function to run the news scraper"""
    scraper = ContextEngineeringNewsScraper()
    items = scraper.scrape_all_sources()
    scraper.save_news_data(items)
    
    # Print summary
    print(f"\n📊 News Collection Summary:")
    print(f"Total items collected: {len(items)}")
    
    # Group by category
    categories = {}
    for item in items:
        if item.category not in categories:
            categories[item.category] = 0
        categories[item.category] += 1
    
    print("\nItems by category:")
    for cat, count in sorted(categories.items()):
        cat_name = scraper.config.categories['categories'].get(cat, {}).get('name', cat)
        print(f"  {cat_name}: {count}")

if __name__ == "__main__":
    main()
