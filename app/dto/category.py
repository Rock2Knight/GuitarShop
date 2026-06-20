from pydantic import BaseModel, Field

class CategoryDto:
    
    class Create(BaseModel):
        name: str = Field(max_length=100)
        parent_category_name: str | None = Field(default=None, max_length=100)
        attributes: list[str] = Field(default_factory=list[str])

        class Config:
            title = "CategoryCreate"
        

    class Update(BaseModel):
        name: str | None = Field(max_length=100)
        parent_category_name: str | None = Field(default=None, max_length=100)
        attributes: list[str] | None = Field(default_factory=list[str])

        class Config:
            title = "CategoryUpdate"