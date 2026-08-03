from fastapi import FastAPI
from app.api.main import api_router

app = FastAPI()


@app.get("/")
def root():
    return {
        "message": "Welcome to root page"
    }


app.include_router(api_router, )
