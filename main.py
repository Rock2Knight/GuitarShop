from fastapi import FastAPI
import uvicorn

from routers import *

app = FastAPI()

app.include_router(user_router)
app.include_router(order_router)
app.include_router(order_product_router)
app.include_router(cart_product_router)
app.include_router(guitar_router)
app.include_router(combo_router)
app.include_router(processor_router)
app.include_router(effect_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка для разработки
    )