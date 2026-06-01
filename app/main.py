from pathlib import Path

from fastapi import FastAPI
from loguru import logger
import uvicorn

from app.routers import *
from app.middlewares import *
from app.cache.redis import cache 

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(order_router)
app.include_router(order_product_router)
app.include_router(cart_product_router)
app.include_router(product_router)

app.add_middleware(TimingMiddleware)
app.add_middleware(LoggingMiddleware)

@app.on_event("startup")
async def startup():
    try:
        redis = await cache.init_redis()
        await redis.ping()
        logger.info("✅ Redis connection established")
    except Exception as e:
        logger.error(f"❌ Redis connection error: {e}")
        raise


if __name__ == "__main__":
    logger.info(f"FILEPATH: {Path(__file__).parent.parent}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка для разработки
        log_level="debug",
    )