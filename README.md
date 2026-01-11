# Comparison Tool API

A simple LLM-powered comparison API that explains trade-offs between options without declaring winners. Uses Perplexity AI for intelligent analysis. Perfect for comparing APIs, cloud services, tech stacks, and more.

## Features

- **Trade-off Analysis**: Explains strengths and weaknesses of each option
- **No Winner Declaration**: Focuses on helping users understand implications
- **Context-Aware**: Incorporates user context into analysis
- **Web UI**: Simple, responsive interface for easy comparisons
- **API Access**: RESTful API for programmatic access
- **Comprehensive Validation**: Clear error messages for invalid requests
- **Multiple Scenarios**: Supports APIs, cloud services, tech stacks, etc.
- **Perplexity AI**: Uses advanced AI models for nuanced analysis

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Perplexity API key
```

Get your Perplexity API key from: https://www.perplexity.ai/settings/api

### 3. Run the Application

**Option A: With UI (Recommended)**
```bash
python demo.py
```
This will start the server and open the web UI at `http://localhost:8000`

**Option B: API Only**
```bash
python main.py
```

### 4. Use the Tool

- **Web UI**: Visit `http://localhost:8000` for the interactive interface
- **API docs**: Visit `http://localhost:8000/docs` for API documentation
- **Health check**: Visit `http://localhost:8000/health`

- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Usage

### Compare Payment APIs

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which payment API should I use for my e-commerce project?",
    "options": ["Stripe", "PayPal", "Square"],
    "criteria": ["Integration complexity", "Fees", "Feature set"],
    "context": "Small startup with limited development resources"
  }'
```

### Compare Cloud Providers

```bash
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which cloud provider should I choose?",
    "options": ["AWS", "Google Cloud", "Azure"],
    "criteria": ["Cost", "Ease of use", "Service availability"],
    "context": "Small team, limited DevOps experience"
  }'
```

## Response Format

```json
{
  "question": "Which payment API should I use?",
  "analysis": {
    "Stripe": {
      "strengths": [
        "Excellent documentation",
        "Comprehensive features",
        "Strong fraud protection"
      ],
      "weaknesses": [
        "Higher fees for small volumes",
        "Complex pricing structure"
      ],
      "explanation": "Stripe offers the most developer-friendly experience..."
    }
  },
  "trade_offs": "For a small startup, Stripe offers fastest implementation...",
  "context_notes": "Given your startup context, prioritize development speed..."
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run integration tests only
pytest tests/test_integration.py

# Run with verbose output
pytest -v
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /compare` - Compare options (main endpoint)
- `GET /docs` - Interactive API documentation

## Requirements

- Python 3.8+
- Perplexity API key
- FastAPI
- Pydantic
- OpenAI Python client (for Perplexity compatibility)

## Environment Variables

- `PERPLEXITY_API_KEY` - Your Perplexity API key (required)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

## Error Handling

The API provides clear error messages for:

- Invalid JSON (400)
- Missing required fields (422)
- Insufficient options (422)
- Empty criteria (422)
- LLM service errors (500)

## License

No License