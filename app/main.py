from fastapi import FastAPI
from .routers import auth
from .routers.v1 import notes
from mangum import Mangum
from .settings import Settings

settings = Settings()
root_path = settings.api_root_path

app = FastAPI(root_path=root_path)
app.include_router(auth.router)
app.include_router(notes.router)

handler = Mangum(app)
