#!/usr/bin/env python3
"""
Startup script for Jira Sense FastAPI Backend
"""

import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print("="*80)
    print("🚀 Starting Jira Sense API Server (Banking-Compliant)")
    print("="*80)
    print("\n📍 Server will be available at:")
    print("   - API: http://localhost:8000")
    print("   - Docs: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n🏦 Banking Compliant: All processing runs locally")
    print("="*80 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
