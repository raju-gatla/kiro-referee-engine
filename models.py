"""
Pydantic models for the Comparison Tool API.

This module defines the request and response models for the comparison API,
focusing on trade-off analysis without declaring winners.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class ComparisonRequest(BaseModel):
    """
    Request model for comparison analysis.
    
    Contains the decision question, options to compare, evaluation criteria,
    and optional context for the analysis.
    """
    question: str = Field(
        ...,
        description="The decision question or context for the comparison",
        example="Which API should I use for my e-commerce project?"
    )
    options: List[str] = Field(
        ...,
        min_items=2,
        description="List of options to compare (minimum 2 required)",
        example=["Stripe API", "PayPal API", "Square API"]
    )
    criteria: List[str] = Field(
        ...,
        min_items=1,
        description="List of evaluation criteria",
        example=["Integration complexity", "Fees", "Feature set", "Documentation"]
    )
    context: Optional[str] = Field(
        None,
        description="Additional context about the situation",
        example="Small startup with limited development resources"
    )

    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

    @validator('options')
    def options_must_be_unique_and_non_empty(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 options are required')
        
        # Check for empty options
        for option in v:
            if not option or not option.strip():
                raise ValueError('Options cannot be empty')
        
        # Check for duplicates (case-insensitive)
        lower_options = [option.lower().strip() for option in v]
        if len(set(lower_options)) != len(lower_options):
            raise ValueError('Options must be unique')
        
        return [option.strip() for option in v]

    @validator('criteria')
    def criteria_must_be_unique_and_non_empty(cls, v):
        if len(v) < 1:
            raise ValueError('At least 1 criterion is required')
        
        # Check for empty criteria
        for criterion in v:
            if not criterion or not criterion.strip():
                raise ValueError('Criteria cannot be empty')
        
        # Check for duplicates (case-insensitive)
        lower_criteria = [criterion.lower().strip() for criterion in v]
        if len(set(lower_criteria)) != len(lower_criteria):
            raise ValueError('Criteria must be unique')
        
        return [criterion.strip() for criterion in v]


class OptionAnalysis(BaseModel):
    """
    Analysis results for a single option.
    
    Contains strengths, weaknesses, and detailed explanation.
    """
    strengths: List[str] = Field(
        ...,
        description="Key advantages of this option",
        example=[
            "Excellent documentation and developer experience",
            "Comprehensive feature set including subscriptions",
            "Strong fraud protection"
        ]
    )
    weaknesses: List[str] = Field(
        ...,
        description="Potential drawbacks and limitations",
        example=[
            "Higher transaction fees for small volumes",
            "Complex pricing structure"
        ]
    )
    explanation: str = Field(
        ...,
        description="Detailed analysis of when this option makes sense",
        example="Stripe offers the most developer-friendly experience with excellent documentation and comprehensive features. However, the pricing can be complex and fees may be higher for smaller transaction volumes."
    )

    @validator('strengths')
    def strengths_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Strengths list cannot be empty')
        for strength in v:
            if not strength or not strength.strip():
                raise ValueError('Individual strengths cannot be empty')
        return [s.strip() for s in v]

    @validator('weaknesses')
    def weaknesses_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Weaknesses list cannot be empty')
        for weakness in v:
            if not weakness or not weakness.strip():
                raise ValueError('Individual weaknesses cannot be empty')
        return [w.strip() for w in v]

    @validator('explanation')
    def explanation_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Explanation cannot be empty')
        return v.strip()


class ComparisonResponse(BaseModel):
    """
    Complete comparison response with trade-off analysis.
    
    Contains the original question, detailed analysis per option,
    and overall trade-off summary.
    """
    question: str = Field(
        ...,
        description="The original decision question",
        example="Which API should I use for my e-commerce project?"
    )
    analysis: Dict[str, OptionAnalysis] = Field(
        ...,
        description="Detailed analysis for each option"
    )
    trade_offs: str = Field(
        ...,
        description="Overall trade-off analysis and summary",
        example="For a small startup with limited development resources, Stripe offers the fastest path to implementation despite higher fees. PayPal provides better brand recognition but requires more development effort."
    )
    context_notes: Optional[str] = Field(
        None,
        description="Context-specific insights when context was provided",
        example="Given your startup context and US focus, prioritize development speed over marginal fee savings."
    )

    @validator('analysis')
    def analysis_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Analysis cannot be empty')
        return v

    @validator('trade_offs')
    def trade_offs_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Trade-offs analysis cannot be empty')
        return v.strip()