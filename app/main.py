import os
from fastapi import FastAPI
from .routers import auth, notes
from mangum import Mangum
root_path = os.environ.get('API_ROOT_PATH')

app = FastAPI(root_path=root_path)
app.include_router(auth.router)
app.include_router(notes.router)

handler = Mangum(app)
