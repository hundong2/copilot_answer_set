#!/usr/bin/env python3
"""
한글 번역 기능 테스트 스크립트
"""

import os
from src.ai_summarizer import AISummarizer

def test_korean_translation():
    """한글 번역 기능 테스트"""
    print("🇰🇷 한글 번역 기능 테스트...")
    
    # API 키 확인
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False
    
    print(f"✓ API 키 확인됨 ({gemini_key[:8]}...)")
    
    # AI Summarizer 초기화
    try:
        summarizer = AISummarizer()
        
        if not summarizer.gemini_model:
            print("❌ Gemini 모델 초기화 실패")
            return False
        
        print("✓ Gemini 모델 초기화 성공")
        
        # 테스트 케이스
        test_cases = [
            {
                "title": "Advanced Prompt Engineering Techniques for Large Language Models",
                "description": "This paper presents novel methods for optimizing prompts in context learning scenarios, focusing on few-shot examples and chain-of-thought reasoning. The research demonstrates significant improvements in model performance across various NLP tasks."
            },
            {
                "title": "RAG-Enhanced Question Answering with Vector Databases",
                "description": "A comprehensive study on improving retrieval-augmented generation systems using advanced vector similarity search and embedding techniques for better context relevance."
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🗪 테스트 케이스 {i}: {test_case['title'][:50]}...")
            
            # 한글 번역 및 요약 생성
            result = summarizer.translate_and_summarize_korean(
                test_case['title'],
                test_case['description']
            )
            
            if result:
                print("✅ 번역 성공!")
                print(f"\n🇰🇷 한글 제목: {result.get('korean_title', 'N/A')}")
                print(f"📝 한글 요약: {result.get('korean_summary', 'N/A')}")
                print(f"🏷️ 한글 키워드: {', '.join(result.get('korean_keywords', []))}")
            else:
                print("❌ 번역 실패")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    success = test_korean_translation()
    
    if success:
        print("\n🎉 한글 번역 기능 테스트 성공!")
        print("ℹ️ 이제 run_daily_news.py를 실행하면 한글 번역이 포함된 뉴스레터가 생성됩니다.")
        print("🔗 뉴스레터에서 다음을 확인할 수 있습니다:")
        print("  - 🇰🇷 한글 제목")
        print("  - 📝 한글 요약")
        print("  - 🏷️ 한글 키워드")
        print("  - 🤖 영문 AI 요약")
    else:
        print("\n❌ 한글 번역 기능 테스트 실패")
        print("🔗 도움말: https://makersuite.google.com/app/apikey")
    
    return success

if __name__ == "__main__":
    main()
