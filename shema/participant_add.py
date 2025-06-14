from pydantic import BaseModel, EmailStr, Field

class ParticipantAdd(BaseModel):
    first_name: str = Field(..., description="nom d'utilisateur")
    last_name: str = Field(..., description="Mot de passe de l'utilisateur")
    email: EmailStr = Field(..., description="Adresse mail de l'utilisateur")
    amount: float = Field(..., description="Montant mis par le participant dans la cagnotte")
    id_cagnotte: int = Field(..., description="l'id de la cagnotte")