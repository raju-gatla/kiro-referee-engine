#!/usr/bin/env python3
"""
Demo script to start the Comparison Tool API.

This script starts the FastAPI server with the comparison tool.
Visit http://localhost:8000 to use the web interface.
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Start the comparison tool API server."""
    
    print("🚀 Starting Comparison Tool API...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Using mock analyzer.")
        print("💡 To use Perplexity API, create .env file with PERPLEXITY_API_KEY")
        print("-" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for using the Comparison Tool!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()