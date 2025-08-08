
from fastapi import FastAPI
from app.server import create_app

app: FastAPI = create_app()
