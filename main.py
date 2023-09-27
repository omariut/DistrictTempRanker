from fastapi import FastAPI
from fastapi import APIRouter
from services.routers import service_routers

app = FastAPI()
routers = APIRouter()
routers.include_router(service_routers)
app.include_router(routers)


@app.get("/")
async def root():
    return {"message": "Hello World!"}
