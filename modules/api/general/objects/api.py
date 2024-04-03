from fastapi import FastAPI

from modules.api.general.methods.api import lifespan

app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)
