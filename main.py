"""
Comparison Tool API - Main FastAPI Application

A comparison API that uses LLM analysis to provide comprehensive trade-off 
explanations for decision-making without declaring winners.
"""

import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from dotenv import load_dotenv
from models import ComparisonRequest, ComparisonResponse
from analyzer import LLMAnalyzer
from mock_analyzer import MockAnalyzer

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI(
    title="Comparison Tool API",
    description="LLM-powered comparison API that explains trade-offs without declaring winners",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer (try LLM first, fallback to mock)
analyzer = None
analyzer_type = "none"

# Force mock mode for testing (comment out to try LLM again)
USE_MOCK_MODE = False

if USE_MOCK_MODE:
    analyzer = MockAnalyzer()
    analyzer_type = "mock"
    print("✓ Using mock analyzer (forced for testing)")
else:
    try:
        analyzer = LLMAnalyzer()
        analyzer_type = "llm"
        print("✓ Using Perplexity LLM analyzer")
    except ValueError as e:
        print(f"Warning: {e}")
        analyzer = MockAnalyzer()
        analyzer_type = "mock"
        print("✓ Using mock analyzer (Perplexity not configured)")
    except Exception as e:
        print(f"Warning: LLM analyzer failed: {e}")
        analyzer = MockAnalyzer()
        analyzer_type = "mock"
        print("✓ Using mock analyzer (Perplexity error)")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {
        "status": "healthy", 
        "service": "comparison-tool-api",
        "analyzer": analyzer_type
    }

# Root endpoint - serve the UI
@app.get("/")
async def root():
    """Serve the comparison tool UI"""
    return FileResponse('static/index.html')

# Main comparison endpoint
@app.post("/compare", response_model=ComparisonResponse)
async def compare(request: ComparisonRequest):
    """
    Compare options and provide trade-off analysis.
    
    Analyzes the provided options against the given criteria and returns
    detailed trade-off explanations without declaring a single winner.
    """
    if analyzer is None:
        raise HTTPException(
            status_code=500,
            detail="No analyzer available. Please check configuration."
        )
    
    try:
        # Perform analysis (LLM or mock)
        result = analyzer.analyze_options(
            question=request.question,
            options=request.options,
            criteria=request.criteria,
            context=request.context
        )
        
        return result
        
    except Exception as e:
        # Only apply detailed error handling for LLM analyzer
        if analyzer_type == "llm":
            # Handle LLM service errors
            error_message = str(e)
            if "rate limit" in error_message.lower() or "quota" in error_message.lower():
                raise HTTPException(
                    status_code=429,
                    detail="OpenAI API quota exceeded. Please check your billing and usage limits at https://platform.openai.com/account/billing"
                )
            elif "api key" in error_message.lower() or "authentication" in error_message.lower():
                raise HTTPException(
                    status_code=401,
                    detail="Invalid API key. Please check your OpenAI API key configuration."
                )
            elif "model" in error_message.lower() and "not found" in error_message.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Model not available. Your API key may not have access to the requested model."
                )
            else:
                # For debugging, let's show more detail in development
                raise HTTPException(
                    status_code=500,
                    detail=f"LLM service error: {error_message}"
                )
        else:
            # Mock analyzer should not fail, but just in case
            raise HTTPException(
                status_code=500,
                detail=f"Analysis error: {str(e)}"
            )

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        errors.append(f"{field}: {message}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "message": "Request contains invalid data",
            "details": errors
        }
    )

# Custom exception handler for JSON decode errors
@app.exception_handler(json.JSONDecodeError)
async def json_decode_exception_handler(request: Request, exc: json.JSONDecodeError):
    """Handle JSON decode errors"""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid JSON",
            "message": "Request body contains malformed JSON",
            "details": f"JSON decode error at position {exc.pos}: {exc.msg}"
        }
    )

# Custom exception handler for general validation errors
@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Data validation failed",
            "message": "The provided data does not meet validation requirements",
            "details": exc.errors()
        }
    )

# Custom exception handler for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail
        }
    )

# Global exception handler for unexpected errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors safely"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(app, host=host, port=port)