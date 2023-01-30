from fastapi import FastAPI
from .routers import auth, notes
from mangum import Mangum

app = FastAPI()
app.include_router(auth.router)
app.include_router(notes.router)

handler = Mangum(app)
