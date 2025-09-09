from fastapi import FastAPI

app = FastAPI(title="Cricket Connect API")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Cricket Connect!"}

# Import and include User and Chat routers
from .users import router as users_router
from .chat import router as chat_router

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

if __name__ == "__main__":
    import uvicorn
    # It's common to run uvicorn with reload for development like this:
    # uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # However, the Dockerfile CMD will run it directly.
    uvicorn.run(app, host="0.0.0.0", port=8000)
