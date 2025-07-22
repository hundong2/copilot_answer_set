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

# Import Gemini AI library (only free AI service we use)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini AI library not installed. Install with: pip install google-generativeai")

logger = logging.getLogger(__name__)

class AISummarizer:
    def __init__(self):
        self.gemini_model = None
        
        # Initialize Gemini (our only AI service - free and powerful!)
        if GEMINI_AVAILABLE and os.getenv('GEMINI_API_KEY'):
            try:
                genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                logger.info("🚀 Gemini AI initialized successfully (FREE tier)")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
        elif not os.getenv('GEMINI_API_KEY'):
            logger.info("💡 To enable AI features, set GEMINI_API_KEY environment variable")
    
    def is_available(self) -> bool:
        """Check if Gemini AI service is available"""
        return self.gemini_model is not None
    
    # We only use Gemini - it's free and powerful! 🚀
    
    def summarize_with_gemini(self, title: str, description: str, content: str = "") -> Optional[str]:
        """Generate summary using Google Gemini"""
        if not self.gemini_model:
            return None
        
        try:
            full_text = f"Title: {title}\n\nDescription: {description}"
            if content:
                full_text += f"\n\nContent: {content[:2000]}"
            
            prompt = f"""
Summarize this Context Engineering / AI research article in 2-3 concise sentences.
Focus on the key innovation, practical implications, and relevance to prompt engineering, RAG, or LLM context management.

{full_text}

Provide only the summary without any additional text:"""
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=150,
                    temperature=0.3,
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini summarization failed: {e}")
            return None
    
    def translate_and_summarize_korean(self, title: str, description: str, content: str = "") -> Optional[dict]:
        """Generate Korean translation and summary using Google Gemini"""
        if not self.gemini_model:
            return None
        
        try:
            full_text = f"Title: {title}\n\nDescription: {description}"
            if content:
                full_text += f"\n\nContent: {content[:2000]}"
            
            prompt = f"""
Please translate and summarize this AI/Context Engineering article in Korean.

Provide the result in this EXACT format:

**제목**: [Korean translation of title]

**요약**: [2-3 sentences summary in Korean, focusing on key innovations and practical implications]

**핵심 키워드**: [3-5 Korean keywords separated by commas]

Article to translate and summarize:
{full_text}

IMPORTANT: 
- Use natural, professional Korean
- Focus on technical accuracy
- Keep the summary concise but informative
- Include practical implications for AI developers
"""
            
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=300,
                    temperature=0.2,
                )
            )
            
            result_text = response.text.strip()
            
            # Parse the structured response
            korean_data = self._parse_korean_response(result_text)
            return korean_data
            
        except Exception as e:
            logger.error(f"Korean translation failed: {e}")
            return None
    
    def _parse_korean_response(self, response_text: str) -> dict:
        """Parse structured Korean response from Gemini"""
        try:
            lines = response_text.split('\n')
            result = {
                'korean_title': '',
                'korean_summary': '',
                'korean_keywords': []
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('**제목**:'):
                    result['korean_title'] = line.replace('**제목**:', '').strip()
                elif line.startswith('**요약**:'):
                    result['korean_summary'] = line.replace('**요약**:', '').strip()
                    current_section = 'summary'
                elif line.startswith('**핵심 키워드**:'):
                    keywords_text = line.replace('**핵심 키워드**:', '').strip()
                    result['korean_keywords'] = [kw.strip() for kw in keywords_text.split(',')]
                    current_section = None
                elif current_section == 'summary' and line and not line.startswith('**'):
                    # Continue summary if it spans multiple lines
                    result['korean_summary'] += ' ' + line
            
            # Clean up
            result['korean_summary'] = result['korean_summary'].strip()
            result['korean_keywords'] = [kw for kw in result['korean_keywords'] if kw]
            
            return result
            
        except Exception as e:
            logger.warning(f"Failed to parse Korean response: {e}")
            return {
                'korean_title': '',
                'korean_summary': response_text[:200] + '...' if len(response_text) > 200 else response_text,
                'korean_keywords': []
            }
    
    def generate_summary(self, title: str, description: str, content: str = "") -> Optional[str]:
        """Generate summary using Gemini AI (free and powerful!)"""
        return self.summarize_with_gemini(title, description, content)
    
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
                # Only use Gemini for insights (free and effective!)
                if self.gemini_model:
                    prompt = f"""
Analyze these {category.replace('_', ' ')} news headlines and identify 2-3 key trends or insights:

{category_text}

Key insights (as bullet points):"""
                    
                    response = self.gemini_model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            max_output_tokens=200,
                            temperature=0.4,
                        )
                    )
                    
                    insight_text = response.text.strip()
                    
                    # Parse bullet points
                    insights[category] = [
                        line.strip().lstrip('•-*').strip() 
                        for line in insight_text.split('\n') 
                        if line.strip() and not line.strip().startswith('Key insights')
                    ][:3]
                    
                    time.sleep(0.5)  # Gentle rate limiting for free tier
                    
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
            
            # Generate AI summary and Korean translation for high-quality items
            if item.get('score', 0) >= 0.4:
                # English summary
                summary = self.generate_summary(
                    item['title'], 
                    item['description'], 
                    item.get('content', '')
                )
                
                if summary:
                    enhanced_item['ai_summary'] = summary
                
                # Korean translation and summary
                korean_data = self.translate_and_summarize_korean(
                    item['title'],
                    item['description'],
                    item.get('content', '')
                )
                
                if korean_data:
                    enhanced_item.update(korean_data)
                    logger.info(f"Generated Korean translation for item {i+1}/{len(items)}")
                else:
                    logger.info(f"Generated English summary for item {i+1}/{len(items)}")
                
                time.sleep(0.8)  # Slightly longer delay for translation
            
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
        print("\u26a0️  Gemini AI not available. Skipping enhancement.")
        print("To enable FREE AI features, set GEMINI_API_KEY environment variable:")
        print("  1. Visit https://makersuite.google.com/app/apikey")
        print("  2. Create API key")
        print("  3. export GEMINI_API_KEY='your-key'")
        print("  🆓 Completely FREE - 1,500 requests/month!")
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
