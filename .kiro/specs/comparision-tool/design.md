# Design Document: Comparison Tool API

## Overview

The Comparison Tool API is a FastAPI-based service that uses Large Language Model (LLM) analysis to provide comprehensive trade-off explanations for decision-making. Rather than declaring winners, the system helps users understand the implications of each choice by highlighting strengths, weaknesses, and contextual factors.

The API focuses on qualitative analysis using LLM reasoning to generate nuanced, context-aware explanations that help users make informed decisions.

## Architecture

The system follows a simple architecture with LLM-powered analysis:

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│            (FastAPI Routes & Validation)               │
├─────────────────────────────────────────────────────────┤
│                  Service Layer                          │
│              ┌─────────────────────────────────────┐    │
│              │         LLM Analyzer                │    │
│              │    (Trade-off Analysis)             │    │
│              └─────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│                   Model Layer                           │
│            (Pydantic Data Models)                       │
└─────────────────────────────────────────────────────────┘
```

**Key Architectural Principles:**
- **LLM-Powered Analysis**: Uses AI to generate nuanced trade-off explanations
- **Context-Aware**: Incorporates user context into analysis
- **No Winner Declaration**: Focuses on explaining trade-offs rather than picking winners
- **Error Resilience**: Handles LLM failures gracefully

## Components and Interfaces

### API Layer

**FastAPI Application (`main.py`)**
- Configures the FastAPI application with documentation
- Registers the `/compare` endpoint with validation
- Handles CORS and basic configuration
- Provides health check endpoint

**Route Handler (`/compare` endpoint)**
- Accepts POST requests with comparison data
- Validates input using Pydantic models
- Calls LLM analyzer for trade-off analysis
- Returns structured comparison results

### Service Layer

**LLM Analyzer (`analyzer.py`)**
- Integrates with OpenAI GPT-4 or similar LLM
- Generates context-aware trade-off analysis
- Structures analysis per option with strengths/weaknesses
- Provides overall trade-off summary

**Key Methods:**
```python
class LLMAnalyzer:
    def analyze_options(self, question: str, options: List[str], criteria: List[str], context: Optional[str]) -> AnalysisResult
    def _build_analysis_prompt(self, question: str, options: List[str], criteria: List[str], context: Optional[str]) -> str
    def _parse_llm_response(self, response: str) -> Dict
```

### Model Layer

**Request Models (`models.py`)**
```python
class ComparisonRequest(BaseModel):
    question: str = Field(..., description="The decision question")
    options: List[str] = Field(..., min_items=2, description="Options to compare")
    criteria: List[str] = Field(..., min_items=1, description="Evaluation criteria")
    context: Optional[str] = Field(None, description="Additional context about the situation")

class OptionAnalysis(BaseModel):
    strengths: List[str]        # Key advantages
    weaknesses: List[str]       # Potential drawbacks
    explanation: str            # Detailed analysis

class ComparisonResponse(BaseModel):
    question: str
    analysis: Dict[str, OptionAnalysis]  # option -> analysis
    trade_offs: str                      # Overall trade-off summary
    context_notes: Optional[str]         # Context-specific insights
```

## Data Models

### Input Data Structure

```json
{
  "question": "Which API should I use for my e-commerce project?",
  "options": ["Stripe API", "PayPal API", "Square API"],
  "criteria": ["Integration complexity", "Fees", "Feature set", "Documentation"],
  "context": "Small startup with limited development resources, focusing on US market initially"
}
```

### Output Data Structure

```json
{
  "question": "Which API should I use for my e-commerce project?",
  "analysis": {
    "Stripe API": {
      "strengths": [
        "Excellent documentation and developer experience",
        "Comprehensive feature set including subscriptions",
        "Strong fraud protection"
      ],
      "weaknesses": [
        "Higher transaction fees for small volumes",
        "Complex pricing structure"
      ],
      "explanation": "Stripe offers the most developer-friendly experience with excellent documentation and comprehensive features. However, the pricing can be complex and fees may be higher for smaller transaction volumes."
    },
    "PayPal API": {
      "strengths": [
        "Widely recognized brand increases customer trust",
        "Lower fees for certain transaction types",
        "Built-in buyer protection"
      ],
      "weaknesses": [
        "More complex integration process",
        "Limited customization options",
        "Potential account holds and restrictions"
      ],
      "explanation": "PayPal provides strong brand recognition and customer trust, which can improve conversion rates. However, integration is more complex and there are potential issues with account restrictions."
    }
  },
  "trade_offs": "For a small startup with limited development resources, Stripe offers the fastest path to implementation despite higher fees. PayPal provides better brand recognition but requires more development effort. Square falls in between but has limited advanced features.",
  "context_notes": "Given your startup context and US focus, prioritize development speed over marginal fee savings. Stripe's superior documentation will save significant development time."
}
```

## LLM Integration

**OpenAI GPT-4 Integration:**
- Uses structured output for reliable JSON responses
- Implements retry logic for reliability
- Handles rate limiting and errors gracefully
- Optimizes prompts for trade-off analysis

**Prompt Engineering:**
```python
ANALYSIS_PROMPT = """
You are an expert consultant helping with decision-making. Analyze the following options without declaring a winner.

Question: {question}
Options: {options}
Criteria: {criteria}
Context: {context}

For each option, provide:
1. Key strengths (3-5 points)
2. Potential weaknesses or limitations (2-4 points)  
3. Detailed explanation of when this option makes sense

Then provide an overall trade-off analysis explaining the key decisions users need to make.

Focus on helping users understand implications rather than picking winners.
Return response in JSON format.
"""
```

## Error Handling

**LLM-Specific Error Handling:**
- **Connection Errors**: Retry with exponential backoff
- **Rate Limiting**: Queue requests and retry
- **Malformed Responses**: Parse partial responses when possible
- **Timeout Errors**: Configurable timeout limits

**General Error Handling:**
- **Validation Errors (422)**: Field-level error messages
- **Client Errors (400)**: Clear descriptions for malformed requests
- **Server Errors (500)**: Safe error messages

## Testing Strategy

**Unit Testing:**
- Test LLM integration with mocked responses
- Test input validation and error handling
- Test response parsing and structure

**Integration Testing:**
- Test complete analysis pipeline
- Test various input combinations
- Test API endpoint responses

**Property-Based Testing:**
- Test API contract compliance
- Test error handling robustness
- Test response structure consistency

**Testing Framework:**
- **pytest** for unit and integration testing
- **Hypothesis** for property-based testing
- **FastAPI TestClient** for API testing
- **pytest-mock** for LLM mocking

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid Request Processing
*For any* valid comparison request with proper JSON structure, question, options (≥2), and criteria (≥1), the API should accept the request and initiate LLM analysis.
**Validates: Requirements 1.1, 1.3, 1.4**

### Property 2: Trade-off Analysis Structure
*For any* successful analysis, the response should contain structured explanations for each option with strengths, weaknesses, and detailed explanations.
**Validates: Requirements 2.1, 2.2, 2.3**

### Property 3: No Winner Declaration
*For any* analysis response, the system should avoid declaring a single winner and instead focus on explaining trade-offs between options.
**Validates: Requirements 2.4, 2.5**

### Property 4: Context Integration
*For any* request that includes context, the analysis should reference and incorporate that context into the explanations and trade-off analysis.
**Validates: Requirements 1.5, 3.4**

### Property 5: Response Structure Consistency
*For any* successful comparison response, it should contain exactly the required fields: question, analysis (with strengths/weaknesses per option), and trade_offs summary.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 6: Error Handling Robustness
*For any* invalid request (missing fields, insufficient options, empty criteria), the system should return appropriate HTTP error codes (400/422) with descriptive messages.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**