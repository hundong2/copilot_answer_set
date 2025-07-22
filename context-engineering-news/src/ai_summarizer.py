#!/usr/bin/env python3
"""
AI-powered summarization and enhancement for Context Engineering news
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging
import time

# Try to import AI libraries (optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize OpenAI if available
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
        
        # Initialize Anthropic if available
        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            try:
                self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic: {e}")
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.openai_client is not None or self.anthropic_client is not None
    
    def summarize_with_openai(self, title: str, description: str, content: str = "") -> Optional[str]:
        """Generate summary using OpenAI"""
        if not self.openai_client:
            return None
        
        try:
            full_text = f"Title: {title}\n\nDescription: {description}"
            if content:
                full_text += f"\n\nContent: {content[:2000]}"  # Limit content length
            
            prompt = f"""
Summarize this Context Engineering / AI research article in 2-3 concise sentences.
Focus on the key innovation, practical implications, and relevance to prompt engineering, RAG, or LLM context management.

{full_text}

Summary:"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI researcher specializing in context engineering and prompt optimization. Provide concise, technical summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI summarization failed: {e}")
            return None
    
    def summarize_with_anthropic(self, title: str, description: str, content: str = "") -> Optional[str]:
        """Generate summary using Anthropic Claude"""
        if not self.anthropic_client:
            return None
        
        try:
            full_text = f"Title: {title}\n\nDescription: {description}"
            if content:
                full_text += f"\n\nContent: {content[:2000]}"
            
            prompt = f"""
Please summarize this Context Engineering / AI research article in 2-3 concise sentences.
Focus on the key innovation, practical implications, and relevance to prompt engineering, RAG, or LLM context management.

{full_text}"""
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=150,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic summarization failed: {e}")
            return None
    
    def generate_summary(self, title: str, description: str, content: str = "") -> Optional[str]:
        """Generate summary using available AI service"""
        # Try OpenAI first, then Anthropic
        summary = self.summarize_with_openai(title, description, content)
        if summary:
            return summary
        
        summary = self.summarize_with_anthropic(title, description, content)
        if summary:
            return summary
        
        return None
    
    def extract_key_insights(self, items: List[Dict]) -> Dict[str, List[str]]:
        """Extract key insights and trends from news items"""
        if not self.is_available():
            return {}
        
        # Group items by category
        categories = {}
        for item in items:
            category = item.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)
        
        insights = {}
        
        for category, cat_items in categories.items():
            if len(cat_items) < 3:  # Skip categories with too few items
                continue
            
            # Create a summary of the category
            titles = [item['title'] for item in cat_items[:5]]
            category_text = "\n".join(titles)
            
            try:
                if self.openai_client:
                    prompt = f"""
Analyze these {category.replace('_', ' ')} news headlines and identify 2-3 key trends or insights:

{category_text}

Key insights (as bullet points):"""
                    
                    response = self.openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=200,
                        temperature=0.4
                    )
                    
                    insight_text = response.choices[0].message.content.strip()
                    # Parse bullet points
                    insights[category] = [
                        line.strip().lstrip('•-*').strip() 
                        for line in insight_text.split('\n') 
                        if line.strip() and not line.strip().startswith('Key insights')
                    ][:3]
                    
                    time.sleep(1)  # Rate limiting
                    
            except Exception as e:
                logger.error(f"Failed to extract insights for {category}: {e}")
                continue
        
        return insights
    
    def enhance_news_data(self, data_file: str = "data/daily_news.json", 
                         output_file: str = "data/enhanced_news.json") -> Dict:
        """Enhance news data with AI-generated summaries and insights"""
        if not self.is_available():
            logger.warning("No AI services available for enhancement")
            return {}
        
        # Load existing data
        with open(data_file, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        items = news_data['items']
        enhanced_items = []
        
        logger.info(f"Enhancing {len(items)} news items with AI summaries...")
        
        for i, item in enumerate(items):
            enhanced_item = item.copy()
            
            # Generate AI summary for high-quality items
            if item.get('score', 0) >= 0.4:
                summary = self.generate_summary(
                    item['title'], 
                    item['description'], 
                    item.get('content', '')
                )
                
                if summary:
                    enhanced_item['ai_summary'] = summary
                    logger.info(f"Generated summary for item {i+1}/{len(items)}")
                
                time.sleep(0.5)  # Rate limiting
            
            enhanced_items.append(enhanced_item)
        
        # Extract key insights
        insights = self.extract_key_insights(enhanced_items)
        
        # Create enhanced data structure
        enhanced_data = news_data.copy()
        enhanced_data['items'] = enhanced_items
        enhanced_data['ai_insights'] = insights
        enhanced_data['enhanced_at'] = datetime.now().isoformat()
        
        # Save enhanced data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Enhanced news data saved to {output_file}")
        return enhanced_data

def main():
    """Main function to enhance news data"""
    summarizer = AISummarizer()
    
    if not summarizer.is_available():
        print("\u26a0️  No AI services available. Skipping enhancement.")
        print("To enable AI features, set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables.")
        return
    
    print("🤖 Starting AI enhancement of news data...")
    
    enhanced_data = summarizer.enhance_news_data()
    
    if enhanced_data:
        enhanced_count = sum(1 for item in enhanced_data['items'] if 'ai_summary' in item)
        insights_count = len(enhanced_data.get('ai_insights', {}))
        
        print(f"✨ Enhancement complete!")
        print(f"  - {enhanced_count} items with AI summaries")
        print(f"  - {insights_count} categories with key insights")
    else:
        print("⚠️  Enhancement failed")

if __name__ == "__main__":
    main()
