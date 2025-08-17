from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import router


app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        version="1.0.0"
        )

Base.metadata.create_all(bind=engine)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )


app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "LinguaParser API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
