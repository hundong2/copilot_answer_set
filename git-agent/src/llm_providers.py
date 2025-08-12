#!/usr/bin/env python3
"""
LLM provider implementations for Git Agent
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = config.get("model", "")
        self.temperature = config.get("temperature", 0.3)
        self.max_tokens = config.get("max_tokens", 1000)
    
    @abstractmethod
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM provider is available"""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client"""
        try:
            import google.generativeai as genai
            
            api_key = self.config.get("api_key", "")
            if not api_key:
                logger.warning("Gemini API key not provided")
                return
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info(f"Gemini provider initialized with model: {self.model}")
            
        except ImportError:
            logger.error("google-generativeai library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
    
    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.client is not None
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Gemini"""
        if not self.is_available():
            return None
        
        try:
            response = self.client.generate_content(
                prompt,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize OpenAI client"""
        try:
            import openai
            
            api_key = self.config.get("api_key", "")
            if not api_key:
                logger.warning("OpenAI API key not provided")
                return
            
            base_url = self.config.get("base_url", "https://api.openai.com/v1")
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
            logger.info(f"OpenAI provider initialized with model: {self.model}")
            
        except ImportError:
            logger.error("openai library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.client is not None
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using OpenAI"""
        if not self.is_available():
            return None
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            return None


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Anthropic client"""
        try:
            import anthropic
            
            api_key = self.config.get("api_key", "")
            if not api_key:
                logger.warning("Anthropic API key not provided")
                return
            
            self.client = anthropic.Anthropic(api_key=api_key)
            logger.info(f"Anthropic provider initialized with model: {self.model}")
            
        except ImportError:
            logger.error("anthropic library not installed")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic: {e}")
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        return self.client is not None
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using Anthropic"""
        if not self.is_available():
            return None
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            return None


class LLMManager:
    """Manager for LLM providers"""
    
    def __init__(self):
        self.providers = {}
        self.active_provider = None
        self._provider_classes = {
            "gemini": GeminiProvider,
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider
        }
    
    def add_provider(self, name: str, config: Dict[str, Any]) -> bool:
        """Add and initialize LLM provider"""
        if name not in self._provider_classes:
            logger.error(f"Unknown provider type: {name}")
            return False
        
        try:
            provider_class = self._provider_classes[name]
            provider = provider_class(config)
            
            if provider.is_available():
                self.providers[name] = provider
                if self.active_provider is None:
                    self.active_provider = name
                logger.info(f"Added {name} provider successfully")
                return True
            else:
                logger.warning(f"Provider {name} is not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
            return False
    
    def set_active_provider(self, name: str) -> bool:
        """Set active LLM provider"""
        if name in self.providers:
            self.active_provider = name
            logger.info(f"Set active provider to: {name}")
            return True
        else:
            logger.error(f"Provider {name} not found")
            return False
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """Generate response using active provider"""
        if not self.active_provider or self.active_provider not in self.providers:
            logger.error("No active LLM provider available")
            return None
        
        provider = self.providers[self.active_provider]
        return provider.generate_response(prompt)
    
    def is_available(self) -> bool:
        """Check if any LLM provider is available"""
        return self.active_provider is not None and len(self.providers) > 0