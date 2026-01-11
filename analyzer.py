"""
LLM Analyzer for generating trade-off analysis.

This module provides LLM-powered analysis that focuses on explaining
trade-offs between options rather than declaring winners.
"""

import os
import json
import time
from typing import Dict, List, Optional
from openai import OpenAI
from models import OptionAnalysis, ComparisonResponse


class LLMAnalyzer:
    """
    LLM-powered analyzer for generating trade-off explanations.
    
    Uses Perplexity API to analyze options and provide detailed
    trade-off analysis without declaring winners.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM analyzer with Perplexity client."""
        api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("Perplexity API key is required. Set PERPLEXITY_API_KEY environment variable or pass api_key parameter.")
        
        # Perplexity uses OpenAI-compatible API
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.perplexity.ai"
        )
        self.model = "sonar"  # Updated to current Perplexity model name
        self.max_retries = 3
        self.retry_delay = 1.0
    
    def analyze_options(
        self, 
        question: str, 
        options: List[str], 
        criteria: List[str], 
        context: Optional[str] = None
    ) -> ComparisonResponse:
        """
        Analyze options and generate trade-off explanations.
        
        Args:
            question: The decision question
            options: List of options to compare
            criteria: List of evaluation criteria
            context: Optional context about the situation
            
        Returns:
            ComparisonResponse with detailed trade-off analysis
        """
        prompt = self._build_analysis_prompt(question, options, criteria, context)
        
        # Get LLM response with retry logic
        response_text = self._get_llm_response(prompt)
        
        # Parse the response
        analysis_data = self._parse_llm_response(response_text)
        
        # Build the response
        return self._build_comparison_response(
            question, options, analysis_data, context
        )
    
    def _build_analysis_prompt(
        self, 
        question: str, 
        options: List[str], 
        criteria: List[str], 
        context: Optional[str] = None
    ) -> str:
        """Build the analysis prompt for the LLM."""
        
        context_section = f"\nContext: {context}" if context else ""
        
        prompt = f"""Analyze these options briefly. No winner declarations.

Question: {question}
Options: {', '.join(options)}
Criteria: {', '.join(criteria)}{context_section}

For each option:
- 2 key strengths (short phrases)
- 1-2 weaknesses (short phrases)
- 1-2 sentence explanation

Be very concise. No citations or references.

JSON only:
{{
    "options": {{
        "{options[0]}": {{
            "strengths": ["Short strength 1", "Short strength 2"],
            "weaknesses": ["Short weakness"],
            "explanation": "Brief explanation in 1-2 sentences."
        }}{f', "{options[1]}": {{"strengths": ["Short strength 1", "Short strength 2"], "weaknesses": ["Short weakness"], "explanation": "Brief explanation."}}' if len(options) > 1 else ''}
    }},
    "trade_offs": "Key trade-off in 1-2 sentences.",
    "context_notes": "{f'Brief context note.' if context else 'null'}"
}}"""

        return prompt
    
    def _get_llm_response(self, prompt: str) -> str:
        """Get response from LLM with retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert decision analyst who helps people understand trade-offs without declaring winners."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"LLM analysis failed after {self.max_retries} attempts: {str(e)}")
                
                # Exponential backoff
                time.sleep(self.retry_delay * (2 ** attempt))
        
        raise Exception("Unexpected error in LLM response")
    
    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse the LLM response JSON with improved error handling."""
        try:
            # Try to extract JSON from the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[start_idx:end_idx]
            
            # Clean up common JSON issues
            json_text = json_text.replace('\n', ' ')  # Remove newlines
            json_text = json_text.replace('\\', '\\\\')  # Escape backslashes
            
            return json.loads(json_text)
            
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parsing fails, create a fallback response
            print(f"JSON parsing failed: {e}")
            print(f"Response text: {response_text[:500]}...")
            
            # Return a simple fallback structure
            return {
                "options": {},
                "trade_offs": "Analysis parsing failed. Please try again.",
                "context_notes": None
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse LLM response: {str(e)}")
    
    def _build_comparison_response(
        self, 
        question: str, 
        options: List[str], 
        analysis_data: Dict, 
        context: Optional[str]
    ) -> ComparisonResponse:
        """Build the final ComparisonResponse from parsed data."""
        
        # Build analysis for each option
        analysis = {}
        options_data = analysis_data.get("options", {})
        
        for option in options:
            option_data = options_data.get(option, {})
            
            # Provide fallback data if LLM didn't provide complete analysis
            strengths = option_data.get("strengths", [f"Strong capabilities in key areas"])
            weaknesses = option_data.get("weaknesses", ["May require additional consideration"])
            explanation = option_data.get("explanation", f"{option} offers a balanced approach with distinct advantages for specific use cases.")
            
            # Ensure we have valid lists
            if not isinstance(strengths, list) or not strengths:
                strengths = [f"Strong capabilities in key areas"]
            if not isinstance(weaknesses, list) or not weaknesses:
                weaknesses = ["May require additional consideration"]
            
            analysis[option] = OptionAnalysis(
                strengths=strengths,
                weaknesses=weaknesses,
                explanation=explanation
            )
        
        # Get trade-offs and context notes
        trade_offs = analysis_data.get("trade_offs", "Each option offers distinct advantages. Consider your specific requirements and constraints when making a decision.")
        context_notes = analysis_data.get("context_notes") if context else None
        
        # Handle null context_notes
        if context_notes == "null" or context_notes == "None":
            context_notes = None
        
        return ComparisonResponse(
            question=question,
            analysis=analysis,
            trade_offs=trade_offs,
            context_notes=context_notes
        )