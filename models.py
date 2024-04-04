from pydantic import BaseModel
from datetime import datetime



class ProductWithStock(BaseModel):
    ProductID: int
    Name: str
    SpecialOfferID: int
    Description: str
    ListPrice: float
    Quantity: int  

class Item(BaseModel):
    name: str
    description: str
    price: float
    
class Department(BaseModel):
    Name: str
    GroupName: str
    
