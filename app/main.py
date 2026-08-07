from fastapi import FastAPI
from app.webhooks.whatsapp_webhook import router as whatsapp_router

app = FastAPI()
app.include_router(whatsapp_router)