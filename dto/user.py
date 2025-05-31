from pydantic import BaseModel, Field

class UserDto:

    class Create(BaseModel):
        email: str = Field(min_length=15, pattern=r'[a-zA-Z0-9_]{1,20}@[a-z]+\.[a-z]{2,3}')
        password: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!@#$%^&*()\[\]\\\/\|\-\_=+]{8,50}')
        username: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!_]{8,50}')

    class Update(BaseModel):
        email: str = Field(min_length=15, pattern=r'[a-zA-Z0-9_]{1,20}@[a-z]+\.[a-z]{2,3}', default=None)
        password: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!@#$%^&*()\[\]\\\/\|\-\_=+]{8,50}', default=None)
        username: str = Field(pattern=r'[a-zA-Zа-яА-Я0-9!_]{8,50}', default=None)