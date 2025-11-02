from fastapi.middleware.cors import CORSMiddleware as FastAPICORS
from typing import List


def setup_cors(app, allowed_origins: List[str] = None):
    """Setup CORS middleware"""
    
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost",
            "http://localhost:3000",
            "http://localhost:8081",
            "http://113.30.191.89",
            "https://113.30.191.89",
        ]
    
    app.add_middleware(
        FastAPICORS,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )
