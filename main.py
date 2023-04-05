from fastapi import FastAPI

from app.api.routers import test


app = FastAPI()

app.include_router(test.router)


@app.get("/")
def index():
    return {"message": "Hello World!"}
