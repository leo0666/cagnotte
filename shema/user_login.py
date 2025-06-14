from pydantic import BaseModel, EmailStr, Field

class UserLogin(BaseModel):
    username: str = Field(..., description="nom d'utilisateur")
    pwd: str = Field(..., description="Mot de passe de l'utilisateur")