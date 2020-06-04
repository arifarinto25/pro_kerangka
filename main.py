import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from routes.router_user import router_user
from routes.router_hobi import router_hobi
from routes.router_wizard import router_wizard
from routes.router_filter import router_filter
from routes.router_summary import router_summary
from routes.router_graph import router_graph
from routes.router_action import router_action
from routes.router_image import router_image
from routes.router_product import router_product
from routes.router_category import router_category

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
app.include_router(router_wizard,prefix="/generatorpy/wizard",tags=["wizard"],responses={404: {"description": "Not found"}})
app.include_router(router_filter,prefix="/generatorpy/filter",tags=["filter"],responses={404: {"description": "Not found"}})
app.include_router(router_summary,prefix="/generatorpy/summary",tags=["summary"],responses={404: {"description": "Not found"}})
app.include_router(router_graph,prefix="/generatorpy/graph",tags=["graph"],responses={404: {"description": "Not found"}})
app.include_router(router_action,prefix="/generatorpy/action",tags=["action"],responses={404: {"description": "Not found"}})
app.include_router(router_image,prefix="/generatorpy/image",tags=["image"],responses={404: {"description": "Not found"}})
app.include_router(router_product,prefix="/generatorpy/product",tags=["product"],responses={404: {"description": "Not found"}})
app.include_router(router_category,prefix="/generatorpy/category",tags=["category"],responses={404: {"description": "Not found"}})

@app.on_event("startup")
async def app_startup():
    # This if fact does nothing its just an example.
    config.load_config()

@app.on_event("shutdown")
async def app_shutdown():
    # This does finish the DB driver connection.
    config.close_db_client()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info", reload=True)