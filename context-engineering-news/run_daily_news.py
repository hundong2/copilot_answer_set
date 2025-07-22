#!/usr/bin/env python3
"""
Main script to run the complete Context Engineering Daily News pipeline
"""

import os
import sys
import logging
from datetime import datetime
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from news_scraper import ContextEngineeringNewsScraper
from html_generator import NewsletterGenerator
from rss_generator import RSSGenerator

# Try to import AI summarizer
try:
    from ai_summarizer import AISummarizer
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('context_engineering_news.log')
    ]
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = ['data', 'docs', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Ensured directory exists: {directory}")

def run_news_pipeline(use_ai: bool = True, verbose: bool = False):
    """Run the complete news generation pipeline"""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("🚀 Starting Context Engineering Daily News Pipeline")
    
    try:
        # Step 1: Ensure directories exist
        ensure_directories()
        
        # Step 2: Scrape news from all sources
        logger.info("🔍 Step 1: Scraping news from sources...")
        scraper = ContextEngineeringNewsScraper()
        news_items = scraper.scrape_all_sources()
        
        if not news_items:
            logger.warning("⚠️  No news items collected. Exiting.")
            return False
        
        # Save raw news data
        scraper.save_news_data(news_items, "data/daily_news.json")
        logger.info(f"✅ Collected {len(news_items)} news items")
        
        # Step 3: AI Enhancement (optional)
        data_file = "data/daily_news.json"
        if use_ai and AI_AVAILABLE:
            logger.info("🤖 Step 2: Enhancing news with AI summaries and Korean translation...")
            try:
                summarizer = AISummarizer()
                if summarizer.is_available():
                    enhanced_data = summarizer.enhance_news_data(
                        "data/daily_news.json", 
                        "data/enhanced_news.json"
                    )
                    if enhanced_data:
                        data_file = "data/enhanced_news.json"
                        korean_count = sum(1 for item in enhanced_data['items'] if item.get('korean_title'))
                        logger.info(f"✅ AI enhancement completed - {korean_count} items with Korean translation")
                    else:
                        logger.warning("⚠️  AI enhancement failed, using original data")
                else:
                    logger.warning("⚠️  No AI services available for enhancement")
            except Exception as e:
                logger.error(f"AI enhancement failed: {e}")
        else:
            logger.info("🙂 Skipping AI enhancement")
        
        # Step 4: Generate HTML Newsletter
        logger.info("📰 Step 3: Generating HTML newsletter...")
        html_generator = NewsletterGenerator()
        html_content = html_generator.generate_html(
            data_file=data_file,
            template_file="templates/simple_newsletter.html",
            output_file="docs/index.html"
        )
        logger.info("✅ HTML newsletter generated")
        
        # Step 5: Generate RSS Feeds
        logger.info("📡 Step 4: Generating RSS feeds...")
        rss_generator = RSSGenerator()
        rss_generator.generate_feeds(data_file)
        logger.info("✅ RSS feeds generated")
        
        # Step 6: Generate summary report
        logger.info("📊 Step 5: Generating summary report...")
        stats = html_generator.generate_summary_stats(data_file)
        
        # Create a simple stats file
        with open("data/stats.json", 'w') as f:
            import json
            json.dump(stats, f, indent=2)
        
        # Print final summary
        print("\n" + "="*60)
        print(f"🎉 Context Engineering Daily News - {datetime.now().strftime('%Y-%m-%d')}")
        print("="*60)
        print(f"📰 Total articles collected: {stats['total_items']}")
        print(f"🗺️ Categories covered: {len(stats['category_distribution'])}")
        print(f"📜 Sources used: {len(stats['source_distribution'])}")
        
        print("\n📈 Category breakdown:")
        for category, count in stats['category_distribution'].items():
            category_name = category.replace('_', ' ').title()
            print(f"  • {category_name}: {count} articles")
        
        print("\n📊 Quality distribution:")
        print(f"  • High relevance (70%+): {stats['quality_distribution']['high']} articles")
        print(f"  • Medium relevance (40-69%): {stats['quality_distribution']['medium']} articles")
        print(f"  • Lower relevance (<40%): {stats['quality_distribution']['low']} articles")
        
        print("\n🔗 Generated files:")
        print("  • HTML Newsletter: docs/index.html")
        print("  • Main RSS Feed: docs/rss.xml")
        print("  • Category RSS Feeds: docs/rss-*.xml")
        print("  • Raw Data: data/daily_news.json")
        if data_file == "data/enhanced_news.json":
            print("  • Enhanced Data: data/enhanced_news.json")
        
        print("\n🎆 Pipeline completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
        print(f"\n❌ Pipeline failed: {e}")
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate Context Engineering Daily News",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_daily_news.py                    # Full pipeline with AI
  python run_daily_news.py --no-ai           # Skip AI enhancement
  python run_daily_news.py --verbose         # Verbose logging
  python run_daily_news.py --no-ai --verbose # Skip AI with verbose logging
"""
    )
    
    parser.add_argument(
        '--no-ai', 
        action='store_true', 
        help='Skip AI enhancement step'
    )
    
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Run the pipeline
    success = run_news_pipeline(
        use_ai=not args.no_ai, 
        verbose=args.verbose
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
