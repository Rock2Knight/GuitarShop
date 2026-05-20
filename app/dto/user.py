from pydantic import BaseModel, Field

class UserDto:

    class Create(BaseModel):
        email: str = Field(min_length=12, pattern=r'[a-zA-Z0-9_]{1,20}@[a-z]+\.[a-z]{2,3}')
        password: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!@#$%^&*()\[\]\\\/\|\-\_=+]{8,50}')
        username: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!_]{8,50}')

        class Config:
            title = "UserCreate"

    class Update(BaseModel):
        email: str | None = Field(min_length=12, pattern=r'[a-zA-Z0-9_]{1,20}@[a-z]+\.[a-z]{2,3}', default=None)
        password: str | None = Field(pattern=r'[a-zA-Zа-яА-Я0-9!@#$%^&*()\[\]\\\/\|\-\_=+]{8,50}', default=None)
        username: str | None = Field(pattern=r'[a-zA-Zа-яА-Я0-9!_]{8,50}', default=None)

        class Config:
            title = "UserUpdate"