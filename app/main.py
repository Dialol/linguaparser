from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import router


app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0"
        )

Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="app/static/html")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(router)


