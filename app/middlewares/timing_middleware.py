import time

from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    """ Middleware для отслеживания времени обработки запроса """

    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers['X-Process-Time'] = f"{(process_time * 1000):.3f} ms"
        return response