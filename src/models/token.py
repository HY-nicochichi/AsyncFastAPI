from pydantic import (
    BaseModel,
    Field
)

class CreateToken:
    class Request(BaseModel):
        email: str = Field(..., min_length=10, max_length=50, examples=['taro@email.com'])
        password: str = Field(..., min_length=8, max_length=20, examples=['Taro1234'])

    class Response(BaseModel):
        access_token: str = Field(..., min_length=5, examples=['Json.Web.Token'])
