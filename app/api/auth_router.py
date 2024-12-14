import asyncio  # Import asyncio for graceful shutdown handling
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
from bson import ObjectId
from app.services.auth_service import login_user, signup_user, save_pattern_data, validate_pattern, save_facial_data, verify_facial_data
from app.models.user_model import SignupModel, LoginModel, PatternModel, ImageModel
from app.db import users_collection, patterns_collection  # Import users_collection for database access
from bson.errors import InvalidId  # Import to handle invalid ObjectId exceptions

router = APIRouter()

# Model for handling pattern data
class PatternModel(BaseModel):
    user_id: str 
    pattern: list[int]

# Model for handling image data
class ImageModel(BaseModel):
    user_id: str
    image: str  # Base64 encoded image

# Login route
@router.post("/login")
async def login(credentials: LoginModel):
    return login_user(credentials)

# Signup route
@router.post("/SignUp")
async def signup(user_data: SignupModel):
    return signup_user(user_data)

# Endpoint for pattern recognition
@router.post("/Pattern_Recognition")
async def save_pattern_data_route(pattern_data: PatternModel):
    return save_pattern_data(pattern_data, users_collection, patterns_collection)

@router.post("/Pattern_Validation")
async def validate_pattern_route(pattern_data: PatternModel):
    return validate_pattern(pattern_data)

@router.post("/api/facial_capture")
async def facial_capture(image_data: ImageModel):
    return save_facial_data(image_data)

@router.post("/facial_verification")
async def facial_verification(image_data: ImageModel):
    return verify_facial_data(image_data)

# Graceful shutdown handler
async def shutdown_event():
    print("Shutting down...")
    try:
        await some_cleanup_task()
    except asyncio.CancelledError:
        print("Cleanup task was cancelled.")
        pass
    except Exception as e:
        print(f"Error during cleanup: {e}")

# Example cleanup task
async def some_cleanup_task():
    try:
        await asyncio.sleep(1)  # Simulate cleanup task
        print("Cleanup complete.")
    except asyncio.CancelledError:
        print("Cleanup task was cancelled during shutdown.")
        raise
