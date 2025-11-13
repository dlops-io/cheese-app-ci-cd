"""
Cheese App API Service - Messy Version
This is the 'before' state from previous tutorials
Let's clean it up with CI/CD!
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import math

# import os
from api.utils import power

# Setup FastAPI app
app = FastAPI(title="Cheese API Server", description="API Server for Cheese App", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to the Cheese App CI/CD Tutorial!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/euclidean_distance/")
async def calculate_euclidean_distance(x: float = 1, y: float = 2):
    """Calculate the Euclidean distance from origin: sqrt(x^2 + y^2)
    Returns the distance of a point (x, y) from the origin (0, 0)
    """
    z = power(x, 2) + power(y, 2)
    result = math.sqrt(z)
    return {
        "x": x,
        "y": y,
        "distance": result,
        "message": "This is a very long line that exceeds 120 characters blah",
    }
