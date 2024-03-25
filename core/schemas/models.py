from pydantic import BaseModel, constr

class User(BaseModel):
    document: str
    email: str

    class Config:
        extra = "forbid"
        
class Transactions(BaseModel):
    payer: int
    payee: int
    value: float
    
    class Config:
        extra = "forbid"
        