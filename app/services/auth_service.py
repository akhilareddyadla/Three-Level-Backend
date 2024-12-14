import base64
from fastapi import HTTPException
from pymongo import MongoClient
from passlib.context import CryptContext
from bson import ObjectId
from app.models.user_model import LoginModel, SignupModel, PatternModel, ImageModel
from pymongo.collection import Collection

# MongoDB client setup
client = MongoClient("mongodb://localhost:27017/Three_Level_Authentication")
db = client['Three_Level_Authentication']
users_collection = db['users']
patterns_collection = db['patterns']  # Create a new collection for patterns

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility functions for password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Login logic
def login_user(credentials: LoginModel):
    user = users_collection.find_one({"email": credentials.email})
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "user_id": str(user["_id"])}

# Signup logic
def signup_user(user_data: SignupModel):
    # Check if the email is already registered
    if users_collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if the username is already taken
    if users_collection.find_one({"username": user_data.username}):
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password securely
    hashed_password = get_password_hash(user_data.password)

    # Prepare the user document
    user = {
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password
    }

    # Insert the user into the collection
    try:
        result = users_collection.insert_one(user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")

    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

# Pattern save function
def save_pattern_data(pattern_data: PatternModel, users_collection: Collection, patterns_collection: Collection):
    # Convert the user_id to ObjectId if it's not already an ObjectId
    user_object_id = ObjectId(pattern_data.user_id)
    
    # Validate if the user exists in the users collection
    user = users_collection.find_one({"_id": user_object_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create the pattern entry document
    pattern_entry = {
        "user_id": pattern_data.user_id,
        "pattern": pattern_data.pattern,
    }
    
    # Insert the pattern entry into the patterns collection
    result = patterns_collection.insert_one(pattern_entry)
    
    # Return the result (which is an InsertOneResult object)
    return {"inserted_id": str(result.inserted_id)}  # Return the inserted ID as a string

# Pattern validation function
def validate_pattern(pattern_data: PatternModel):
    user_object_id = ObjectId(pattern_data.user_id.strip())
    
    # Find user pattern
    user = patterns_collection.find_one({"user_id": pattern_data.user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the stored pattern exists
    stored_pattern = user.get("pattern")
    if not stored_pattern:
        raise HTTPException(status_code=400, detail="No pattern stored for this user")
    
    # Validate if the patterns match
    if stored_pattern == pattern_data.pattern:
        return {"success": True, "message": "Pattern is valid"}
    else:
        raise HTTPException(status_code=401, detail="Invalid pattern")

# Function to save facial data
def save_facial_data(image_data: ImageModel):
    try:
        user_object_id = ObjectId(image_data.user_id.strip())  # Ensure no extra spaces in user_id
        user = users_collection.find_one({"_id": user_object_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Decode the Base64-encoded image
        image_bytes = base64.b64decode(image_data.image.split(",")[1])  # Strip off 'data:image/jpeg;base64,' part

        # Prepare the image entry for storage
        image_entry = {
            "user_id": image_data.user_id,
            "facial_image": image_bytes
        }

        # Save the facial image into the database
        result = users_collection.update_one(
            {"_id": user_object_id},
            {"$set": {"facial_image": image_entry}}
        )

        if result.modified_count == 1:
            return {"message": "Facial image stored successfully", "user_id": image_data.user_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to store the image")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while saving facial data: {e}")

# Facial verification logic
def verify_facial_data(image_data: ImageModel):
    try:
        user_object_id = ObjectId(image_data.user_id.strip())  # Ensure no extra spaces in user_id
        user = users_collection.find_one({"_id": user_object_id})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Decode the Base64-encoded image
        image_bytes = base64.b64decode(image_data.image.split(",")[1])  # Strip off 'data:image/jpeg;base64,' part

        # Retrieve the stored facial image from the user document
        stored_image = user.get("facial_image", {}).get("facial_image")

        if not stored_image:
            raise HTTPException(status_code=404, detail="No facial image stored for this user")

        # Compare the stored image with the received image (this is a placeholder logic)
        if stored_image == image_bytes:
            return {"success": True, "message": "Facial image verified successfully"}
        else:
            raise HTTPException(status_code=401, detail="Facial image does not match")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during facial verification: {e}")
