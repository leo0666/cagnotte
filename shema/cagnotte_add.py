from pydantic import BaseModel, Field
from typing import Optional

class CagnotteAdd(BaseModel):
    name: str = Field(..., description="nom de la cagnotte")
    description: Optional[str] = Field(None, description="description de la cagnotte")