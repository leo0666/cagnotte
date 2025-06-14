from pydantic import BaseModel, Field

class AmountEdit(BaseModel):
    id_participant: int = Field(..., description="id du participant")
    amount: float = Field(..., description="Montant mis par le participant dans la cagnotte")