from fastapi import FastAPI
from core.controllers import routers

app = FastAPI()       
app.include_router(routers.router)
