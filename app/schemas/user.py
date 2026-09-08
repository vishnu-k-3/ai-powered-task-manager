from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseModel):
    email: EmailStr | None = None
    username: str | None = None


class ChangePassword(BaseModel):
    current_password: str
    new_password: str