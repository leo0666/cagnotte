from pydantic import BaseModel, Field

class CagnotteDel(BaseModel):
    id_cagnotte: int = Field(..., description="id de la cagnotte")