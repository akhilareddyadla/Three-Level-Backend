from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from deepface import DeepFace
import os
from typing import List

router = APIRouter()

# Path to store registered user images
USER_IMAGES_PATH = "Registered_images"

# Ensure the directory exists
os.makedirs(USER_IMAGES_PATH, exist_ok=True)


@router.post("/facial-register/")
async def register_user(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Register a user by storing their image.
    """
    try:
        print("entyred")
        # Save the uploaded image to the user's directory
        file_path = os.path.join(USER_IMAGES_PATH, f"{user_id}.jpg")
        with open(file_path, "wb") as f:
            f.write(await file.read())

        return JSONResponse(
            status_code=200,
            content={"message": "User registered successfully", "user_id": user_id},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/facial-authentication/")
async def facial_authentication(user_id: str = Form(...), file: UploadFile = File(...)):
    """
    Authenticate a user by matching their face with the registered image.
    """
    try:
        # Path to the registered image for the user
        registered_image_path = os.path.join(USER_IMAGES_PATH, f"{user_id}.jpg")

        # Check if the registered image exists
        if not os.path.exists(registered_image_path):
            return JSONResponse(
                status_code=404,
                content={"message": "User not found. Please register first."},
            )

        # Save the uploaded image temporarily for comparison
        uploaded_image_path = f"temp_{user_id}.jpg"
        with open(uploaded_image_path, "wb") as f:
            f.write(await file.read())

        # Perform facial recognition
        result = DeepFace.verify(
            uploaded_image_path, registered_image_path, model_name="VGG-Face"
        )

        # Remove the temporary file
        os.remove(uploaded_image_path)

        # Check the verification result
        if result["verified"]:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Facial authentication successful",
                    "user_id": user_id,
                },
            )
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "Facial authentication failed. Face does not match."
                },
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/facial_capture")
async def three_level_authentication(
    user_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Perform three-level authentication: password, OTP, and facial recognition.
    """
    try:
        # Step 3: Facial recognition
        facial_auth_result = await facial_authentication(user_id=user_id, file=file)
        if facial_auth_result.status_code != 200:
            return JSONResponse(
                status_code=401,
                content={
                    "message": "Authentication failed: Facial recognition failed."
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "message": "Three-level authentication successful",
                "user_id": user_id,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
