from hashlib import sha3_512
from typing import Any

from asyncpg import connect
from loguru import logger
from fastapi import status, APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from dto.user import UserDto
from dependencies.cache import get_cache
from cache.redis import RedisCache

from auth_service.auth import get_current_user
from auth_service.token_storage import TokenStorage

from app.config import settings

auth_router = APIRouter(prefix="/auth", tags=["Аутентификация"])


ADD_NEW_USER = '''
    INSERT INTO "user" (email, passhash, username)
    VALUES ($1, $2, $3)
    RETURNING id, username, email, passhash, created_at
'''


async def check_user_in_db(user_data: UserDto.Create) -> list[dict[str, Any]]:
    sql_request = '''
        SELECT id
        FROM "user"
        WHERE email = $1
        AND passhash = $2
    '''
    
    DB_NAME = settings.DB_NAME
    DB_HOST = settings.DB_HOST
    DB_PORT = settings.DB_PORT
    DB_USER = settings.DB_USER
    DB_NAME = settings.DB_NAME
    DB_PASSWORD = settings.DB_PASSWORD


    conn = await connect(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

    passhash = sha3_512(user_data.password.encode("utf-8")).hexdigest()
    logger.debug(f'passhash = {passhash}')
    list_res = await conn.fetch(sql_request, user_data.email, passhash)
    users = [dict(row) for row in list_res]
            
    await conn.close()

    return users


async def add_user_to_db(email: str, passhash: str, username: str):

    DB_NAME = settings.DB_NAME
    DB_HOST = settings.DB_HOST
    DB_PORT = settings.DB_PORT
    DB_USER = settings.DB_USER
    DB_NAME = settings.DB_NAME
    DB_PASSWORD = settings.DB_PASSWORD

    conn = await connect(database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, port=DB_PORT)

    row = await conn.fetchrow(ADD_NEW_USER, email, passhash, username)

    await conn.close()

    return dict(row)



# === РЕГИСТРАЦИЯ ===
@auth_router.post("/register")
async def register(
    user_data: UserDto.Create,
    users_list = Depends(check_user_in_db)
):

    logger.info(f"Users List: {users_list}\n\n")
    user_dump = users_list[0] if users_list else None
    
    if user_dump:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    hashed_password = sha3_512(user_data.password.encode("utf-8")).hexdigest()
    res_user = await add_user_to_db(user_data.email, hashed_password, user_data.username)
    logger.info(f"Inserted user data: {res_user}")

    return HTTPException(status_code=status.HTTP_201_CREATED)


@auth_router.post("/login")
async def login(
    user_data: UserDto.Create,
    users_list = Depends(check_user_in_db),
    cache: RedisCache = Depends(get_cache)
):
    logger.info(f"Users List: {users_list}\n\n")
    user_dump = users_list[0] if users_list else None
    
    if not user_dump:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    token_storage = TokenStorage(cache)

    # создаём два токена
    access_token = await token_storage.create_token(
        user_dump.get("id"), "access", ttl_seconds=1800  # 30 минут
    )
    refresh_token = await token_storage.create_token(
        user_dump.get("id"), "refresh", ttl_seconds=604800  # 7 дней
    )
    
    return JSONResponse(
        content={"access_token": access_token, "refresh_token": refresh_token},
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/logout")
async def logout(current_user: int = Depends(get_current_user)):
    # проблемка: у нас нет самого токена в get_current_user!
    # нужно модифицировать get_current_user, чтобы возвращал и токен
    pass