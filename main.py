from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy import text
from config import DB_TYPE
from db import engine, mongo_client
from v1.router import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"Database ({DB_TYPE}) connection successful!")

        await mongo_client.admin.command("ping")
        print("MongoDB connection successful!")

    except Exception as e:
        print(f"Database connection failed: {e}")
    yield

    engine.dispose()
    print("Database connection closed.")

    await mongo_client.close()
    print("MongoDB connection closed.")


app = FastAPI(title="Refill Go API",
               description="A simple API to manage water refilling stations pick up and delivery services.",
               version="1.0.0",
               lifespan=lifespan
            )


@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Refill Go API! This is a simple API to manage water refilling stations pick up and delivery services. Visit our documentation at /docs for more information."}


app.include_router(v1_router, prefix="/v1")