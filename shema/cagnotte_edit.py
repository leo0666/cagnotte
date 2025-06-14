from pydantic import BaseModel, Field
from typing import Optional

class CagnotteEdit(BaseModel):
    id_cagnotte: int = Field(..., description="id de la cagnotte")
    name: Optional[str] = Field(None, description="nom de la cagnotte")
    description: Optional[str] = Field(None, description="description de la cagnotte")