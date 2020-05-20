from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from routes.router_user import router_user
from routes.router_hobi import router_hobi
from routes.router_filter import router_filter
from routes.router_summary import router_summary
from routes.router_action import router_action
from routes.router_image import router_image

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_user,prefix="/generatorpy/user",tags=["user"],responses={404: {"description": "Not found"}})
app.include_router(router_hobi,prefix="/generatorpy/hobi",tags=["hobi"],responses={404: {"description": "Not found"}})
app.include_router(router_filter,prefix="/generatorpy/filter",tags=["filter"],responses={404: {"description": "Not found"}})
app.include_router(router_summary,prefix="/generatorpy/summary",tags=["summary"],responses={404: {"description": "Not found"}})
app.include_router(router_action,prefix="/generatorpy/action",tags=["action"],responses={404: {"description": "Not found"}})
app.include_router(router_image,prefix="/generatorpy/image",tags=["image"],responses={404: {"description": "Not found"}})

@app.on_event("startup")
async def app_startup():
    # This if fact does nothing its just an example.
    config.load_config()

@app.on_event("shutdown")
async def app_shutdown():
    # This does finish the DB driver connection.
    config.close_db_client()