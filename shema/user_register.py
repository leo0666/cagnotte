from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    first_name: str = Field(..., description="nom d'utilisateur")
    last_name: str = Field(..., description="Mot de passe de l'utilisateur")
    email: EmailStr = Field(..., description="Adresse mail de l'utilisateur")
    username: str = Field(..., description="nom d'utilisateur")
    pwd: str = Field(..., description="Mot de passe de l'utilisateur")