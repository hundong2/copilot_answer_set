#!/usr/bin/env python3
"""
Gemini API 연결 테스트 스크립트
"""

import os
from src.ai_summarizer import AISummarizer

def test_gemini_connection():
    """Gemini API 연결 테스트"""
    print("🤖 Gemini API 연결 테스트...")
    
    # API 키 확인
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        print("❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("📝 설정 방법: export GEMINI_API_KEY='your-api-key'")
        return False
    
    print(f"✓ API 키 확인됨 ({gemini_key[:8]}...)")
    
    # AI Summarizer 초기화
    try:
        summarizer = AISummarizer()
        
        if not summarizer.gemini_model:
            print("❌ Gemini 모델 초기화 실패")
            return False
        
        print("✓ Gemini 모델 초기화 성공")
        
        # 테스트 요약 생성
        test_title = "Advanced Prompt Engineering Techniques for Large Language Models"
        test_description = "This paper presents novel methods for optimizing prompts in context learning scenarios, focusing on few-shot examples and chain-of-thought reasoning."
        
        print("🗪 테스트 요약 생성 중...")
        summary = summarizer.summarize_with_gemini(test_title, test_description)
        
        if summary:
            print("✓ 요약 생성 성공!")
            print(f"
📝 결과:\n{summary}\n")
            return True
        else:
            print("❌ 요약 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def main():
    """메인 함수"""
    success = test_gemini_connection()
    
    if success:
        print("🎉 Gemini API 연결 테스트 성공!")
        print("ℹ️ 이제 run_daily_news.py를 실행하여 전체 파이프라인을 테스트할 수 있습니다.")
    else:
        print("❌ Gemini API 연결 테스트 실패")
        print("🔗 도움말: https://makersuite.google.com/app/apikey")
    
    return success

if __name__ == "__main__":
    main()
