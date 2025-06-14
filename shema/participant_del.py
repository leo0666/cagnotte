from pydantic import BaseModel, Field

class ParticipantDel(BaseModel):
    id_participant: int = Field(..., description="id du participant")