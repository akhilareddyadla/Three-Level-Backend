from pydantic import BaseModel
from typing import List, Union
class LoginModel(BaseModel):
    email: str
    password: str

class SignupModel(BaseModel):
    email: str
    username: str
    password: str
class PatternModel(BaseModel):
    user_id: str
    pattern: list[int]  # A list of integers for pattern


class ImageModel(BaseModel):
    user_id: str  # User's ID to identify the account
    facial_image: str  # Base64 encoded image for facial verification