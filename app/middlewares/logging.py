from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request

from app.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"METHOD: {request.method}\n" \
                    f"URL: {request.url}\n" \
                    f"HEADERS: {request.headers}\n" \
                    f"CLIENT: {request.client}\n\n")
        if request.query_params:
            logger.info(f"QUERY PARAMS: {request.query_params}\n\n")

        response = await call_next(request)
        
        logger.info(f"STATUS CODE: {response.status_code}\n" \
                    f"RESPONSE Media-Type: {response.media_type}\n" \
                    f"RESPONSE HEADERS: {response.headers}\n")

        return response