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
    
class WorkOrder(BaseModel):
    ProductID: int
    OrderQty: int
    StockedQty: int
    ScrappedQty: int
    num_weeks: int
    ScrapReasonID: int

class WorkOrderUpdate(BaseModel):
    WorkOrderID: int
    ProductID: int
    OrderQty: int
    StockedQty: int
    ScrappedQty: int
    num_weeks: int
    ScrapReasonID: int

class CommissionUpdate(BaseModel):
    BusinessEntityID: int
    CommissionPct: float
