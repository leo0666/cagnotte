from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class ParticipantEdit(BaseModel):
    id_participant: int = Field(..., description="id du participant")
    first_name: Optional[str] = Field(None, description="nom d'utilisateur")
    last_name: Optional[str] = Field(None, description="Mot de passe de l'utilisateur")
    email: Optional[EmailStr] = Field(None, description="Adresse mail de l'utilisateur")
    amount: Optional[float] = Field(None, description="Montant mis par le participant dans la cagnotte")
    id_cagnotte: Optional[int] = Field(None, description="l'id de la cagnotte")