from hashlib import sha256
from fastapi import status, APIRouter, HTTPException

from access.user import access_user
from dto.user import UserDto

auth_router = APIRouter(prefix="/login", tags=["Аутентификация"])

@auth_router.post("/", status_code=status.HTTP_201_CREATED)
async def auth_user(user_dto: UserDto.Create):
    user_dump = user_dto.model_dump()
    user_pass = user_dump.get("password")
    user_hash = sha256(user_pass.encode("utf-8")).hexdigest()
    
    user_dump.pop("password")
    user_dump["passhash"] = user_hash
    full_dump = {"method": "post", "dto": user_dump}

    user_resp =  await access_user(**full_dump)

    if isinstance(user_resp, HTTPException):
        user_resp.status_code = user_resp.status_code
        return HTTPException(status_code=user_resp.status_code)
    user_resp.status_code = status.HTTP_201_CREATED
    return user_resp