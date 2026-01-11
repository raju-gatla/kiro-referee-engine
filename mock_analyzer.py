"""
Mock analyzer for testing when OpenAI API is not available.
"""

from typing import Dict, List, Optional
from models import OptionAnalysis, ComparisonResponse


class MockAnalyzer:
    """
    Mock analyzer that provides sample responses without calling OpenAI.
    Useful for testing and development when API quota is exceeded.
    """
    
    def analyze_options(
        self, 
        question: str, 
        options: List[str], 
        criteria: List[str], 
        context: Optional[str] = None
    ) -> ComparisonResponse:
        """
        Generate mock trade-off analysis.
        """
        
        # Generate mock analysis for each option
        analysis = {}
        for i, option in enumerate(options):
            analysis[option] = OptionAnalysis(
                strengths=[
                    f"Strong performance in {criteria[0] if criteria else 'key areas'}",
                    f"Good {criteria[1] if len(criteria) > 1 else 'value proposition'}",
                    f"Reliable {criteria[2] if len(criteria) > 2 else 'solution'}"
                ],
                weaknesses=[
                    f"Higher {criteria[-1] if criteria else 'cost'} compared to alternatives",
                    f"Learning curve for {criteria[0] if criteria else 'implementation'}"
                ],
                explanation=f"{option} offers a balanced approach with strong capabilities in {criteria[0] if criteria else 'core functionality'}. While it may require more investment in {criteria[-1] if criteria else 'setup'}, it provides solid long-term value for your use case."
            )
        
        # Generate mock trade-offs
        trade_offs = f"When choosing between {', '.join(options)}, consider your priorities around {', '.join(criteria[:2]) if len(criteria) >= 2 else 'key factors'}. Each option has distinct advantages that align with different use cases and constraints."
        
        # Add context notes if context provided
        context_notes = None
        if context:
            context_notes = f"Given your context ({context}), focus on solutions that balance immediate needs with long-term scalability."
        
        return ComparisonResponse(
            question=question,
            analysis=analysis,
            trade_offs=trade_offs,
            context_notes=context_notes
        )