from pydantic import BaseModel, Field

class ParticipantAccess(BaseModel):
    id_participant: int = Field(..., description="id de l'utilisateur")