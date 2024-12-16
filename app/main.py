from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.facial import router as facial_validation_router


import asyncio
from app.api.auth_router import router as auth_router  # Import your auth router

app = FastAPI()

# Allow requests from specific origins (e.g., localhost:3000 for frontend)
origins = [
    "http://localhost:3000",  # Adjust to your frontend origin
    "http://localhost:5173",  # Add any other frontend origins as necessary
    "http://localhost:5176",  # Add any other frontend origins as necessary
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# # Include your routes
app.include_router(auth_router)
app.include_router(facial_validation_router)


# Global shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down...")
    try:
        await some_cleanup_task()
    except asyncio.CancelledError:
        print("Cleanup task was cancelled.")
        pass
    except Exception as e:
        print(f"Error during cleanup: {e}")


async def some_cleanup_task():
    try:
        # Simulate cleanup task with sleep
        await asyncio.sleep(1)
        print("Cleanup complete.")
    except asyncio.CancelledError:
        print("Cleanup task was cancelled during shutdown.")
        raise
