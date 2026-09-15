import sys
import os

# Add root directory to sys.path so imports like `backend.main` resolve cleanly on Vercel
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Export FastAPI app for Vercel Serverless Function handler
handler = app
