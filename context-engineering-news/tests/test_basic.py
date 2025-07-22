#!/usr/bin/env python3
"""
Basic tests for Context Engineering Daily News
"""

import os
import sys
import json
import tempfile
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_config_loading():
    """Test that configuration files can be loaded"""
    config_dir = Path(__file__).parent.parent / 'config'
    
    # Test categories config
    categories_file = config_dir / 'categories.json'
    assert categories_file.exists(), "categories.json not found"
    
    with open(categories_file) as f:
        categories = json.load(f)
    
    assert 'categories' in categories
    assert 'priority_keywords' in categories
    assert len(categories['categories']) > 0
    
    # Test sources config
    sources_file = config_dir / 'sources.json'
    assert sources_file.exists(), "sources.json not found"
    
    with open(sources_file) as f:
        sources = json.load(f)
    
    assert 'sources' in sources
    assert len(sources['sources']) > 0

def test_news_scraper_import():
    """Test that news scraper can be imported"""
    try:
        from news_scraper import ContextEngineeringNewsScraper, NewsItem
        scraper = ContextEngineeringNewsScraper('config')
        assert scraper is not None
    except ImportError as e:
        pytest.fail(f"Failed to import news_scraper: {e}")

def test_html_generator_import():
    """Test that HTML generator can be imported"""
    try:
        from html_generator import NewsletterGenerator
        generator = NewsletterGenerator('config')
        assert generator is not None
    except ImportError as e:
        pytest.fail(f"Failed to import html_generator: {e}")

def test_categorization():
    """Test news categorization logic"""
    from news_scraper import ContextEngineeringNewsScraper
    
    scraper = ContextEngineeringNewsScraper('config')
    
    # Test prompt engineering categorization
    category, score, keywords = scraper.categorize_content(
        "Advanced Prompt Engineering Techniques for LLMs",
        "This paper discusses few-shot prompting and instruction following"
    )
    
    assert score > 0.3  # Should have decent relevance
    assert 'prompt' in ' '.join(keywords).lower() or 'few-shot' in ' '.join(keywords).lower()
    
    # Test irrelevant content
    category, score, keywords = scraper.categorize_content(
        "Recipe for Chocolate Cake",
        "How to bake a delicious chocolate cake with frosting"
    )
    
    assert score < 0.3  # Should have low relevance

def test_sample_data_processing():
    """Test processing of sample news data"""
    from html_generator import NewsletterGenerator
    
    # Create sample data
    sample_data = {
        "generated_at": "2024-01-01T12:00:00",
        "total_items": 2,
        "items": [
            {
                "title": "New Prompt Engineering Research",
                "url": "https://example.com/paper1",
                "description": "Research on advanced prompting techniques",
                "published_date": "2024-01-01T10:00:00",
                "source": "Test Source",
                "category": "prompt_engineering",
                "keywords": ["prompt", "engineering"],
                "score": 0.8
            },
            {
                "title": "RAG Implementation Guide",
                "url": "https://example.com/guide1",
                "description": "Comprehensive guide to RAG systems",
                "published_date": "2024-01-01T09:00:00",
                "source": "Test Blog",
                "category": "rag_retrieval",
                "keywords": ["RAG", "retrieval"],
                "score": 0.7
            }
        ]
    }
    
    # Save sample data to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_file = f.name
    
    try:
        generator = NewsletterGenerator('config')
        categories = generator.organize_by_category(sample_data['items'])
        
        assert 'prompt_engineering' in categories
        assert 'rag_retrieval' in categories
        assert len(categories['prompt_engineering']['news_items']) == 1
        assert len(categories['rag_retrieval']['news_items']) == 1
        
    finally:
        os.unlink(temp_file)

def test_trending_keywords():
    """Test trending keywords extraction"""
    from html_generator import NewsletterGenerator
    
    generator = NewsletterGenerator('config')
    
    sample_items = [
        {"keywords": ["prompt", "engineering", "LLM"]},
        {"keywords": ["prompt", "GPT", "fine-tuning"]},
        {"keywords": ["RAG", "retrieval", "prompt"]},
    ]
    
    trending = generator.get_trending_keywords(sample_items)
    
    assert 'prompt' in trending  # Should be most frequent
    assert len(trending) <= 10  # Should limit to top 10

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
