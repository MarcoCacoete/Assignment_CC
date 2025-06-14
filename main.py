from itertools import product
from fastapi import FastAPI, HTTPException, Depends, status, Query
from pydantic import BaseModel, ValidationError
from typing import List, Optional
from dbConn import conn
from models import *
import uuid
import datetime

    
app = FastAPI()

@app.get("/products/low_stock_items", response_model=list[ProductWithStock])
def get_low_stock_products():
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                p.ProductID, 
                p.Name, 
                so.SpecialOfferID, 
                so.Description, 
                p.ListPrice,
                pi.Quantity  
            FROM 
                production_product p 
            INNER JOIN 
                sales_specialofferproduct spp ON p.ProductID = spp.ProductID 
            INNER JOIN 
                sales_specialoffer so ON spp.SpecialOfferID = so.SpecialOfferID 
            INNER JOIN 
                production_productinventory pi ON p.ProductID = pi.ProductID  
            WHERE 
                pi.Quantity < 50  # Update this line
            AND
                so.Description != 'No Discount'
        """)

        low_stock_products = []  # List to store low stock ProductWithStock entries

        for row in cursor.fetchall():
            low_stock_products.append(ProductWithStock(
                ProductID=row[0],
                Name=row[1],
                SpecialOfferID=row[2],
                Description=row[3],
                ListPrice=row[4],
                Quantity=row[5]  
            ))
        
        cursor.close()

        return low_stock_products

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")



@app.get("/products/low_stock_items/{quantity}", response_model=list[ProductWithStock])
def get_low_stock_products(quantity: int):
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                p.ProductID, 
                p.Name, 
                so.SpecialOfferID, 
                so.Description, 
                p.ListPrice,
                pi.Quantity  
            FROM 
                production_product p 
            INNER JOIN 
                sales_specialofferproduct spp ON p.ProductID = spp.ProductID 
            INNER JOIN 
                sales_specialoffer so ON spp.SpecialOfferID = so.SpecialOfferID 
            INNER JOIN 
                production_productinventory pi ON p.ProductID = pi.ProductID  
            WHERE 
                pi.Quantity < %s  
            AND
                so.Description != 'No Discount'
        """, (quantity,))

        low_stock_products = []  # List to store low stock ProductWithStock entries

        for row in cursor.fetchall():
            low_stock_products.append(ProductWithStock(
                ProductID=row[0],
                Name=row[1],
                SpecialOfferID=row[2],
                Description=row[3],
                ListPrice=row[4],
                Quantity=row[5]  
            ))
        
        cursor.close()

        return low_stock_products

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")





@app.post("/departments/{Name}/{GroupName}")
def create_department(Name: str, GroupName: str):
    try:
        # Validate the path parameters using the Department model
        department = Department(Name=Name, GroupName=GroupName)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    
    
    cursor = conn.cursor()
    try:# Because this table doesn't auto increment DepartmentID, I created this method.
        # Finds the maximum DepartmentID currently in the table
        cursor.execute("SELECT MAX(DepartmentID) FROM humanresources_department")
        max_id = cursor.fetchone()[0]

        # If the table is empty, DepartmentID is 1, otherwise increment the max_id
        DepartmentID = 1 if max_id is None else max_id + 1

        cursor.execute(
            "INSERT INTO humanresources_department (DepartmentID, Name, GroupName, ModifiedDate) VALUES (%s,%s, %s, NOW())", # the modified date field is created using the datetime call of Now() 
            (DepartmentID, Name, GroupName)
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Department created successfully"}





@app.post("/work_order/{ProductID}/{OrderQty}/{StockedQty}/{ScrappedQty}/{ScrapReasonID}")
def create_work_order(ProductID: int, OrderQty: int, StockedQty: int, ScrappedQty: int, num_weeks: int, ScrapReasonID: int):
    try:
        # Validate the path parameters using the WorkOrder model
        workOrder = WorkOrder(ProductID=ProductID,
    OrderQty=OrderQty,
    StockedQty=StockedQty,
    ScrappedQty=ScrappedQty,
    num_weeks=num_weeks,
    ScrapReasonID=ScrapReasonID)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.errors())
    
    cursor = conn.cursor()
    try:
        # Because this table doesn't auto increment WorkOrderID, I created this method.
        # Finds the maximum WorkOrderID currently in the table
        cursor.execute("SELECT MAX(WorkOrderID) FROM production_workorder")
        max_id = cursor.fetchone()[0]

        # If the table is empty, WorkOrderID is 1, otherwise increment the max_id
        WorkOrderID = 1 if max_id is None else max_id + 1

        cursor.execute(
            "INSERT INTO production_workorder (WorkOrderID, ProductID, OrderQty, StockedQty, ScrappedQty, StartDate, DueDate, EndDate, ScrapReasonID) VALUES (%s, %s, %s, %s, %s, NOW(), DATE_ADD(NOW(), INTERVAL %s WEEK), DATE_ADD(DATE_ADD(NOW(), INTERVAL %s WEEK), INTERVAL -1 DAY), %s)", 
            (WorkOrderID, ProductID, OrderQty, StockedQty, ScrappedQty, num_weeks, num_weeks, ScrapReasonID)
        )

        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Workorder created successfully"}


@app.put("/Workorder_update/{WorkOrderID}/{ProductID}/{OrderQty}/{StockedQty}/{ScrappedQty}/{num_weeks}/{ScrapReasonID}")
def update_workorder(WorkOrderID: int, ProductID: int, OrderQty: int, StockedQty: int, ScrappedQty: int, num_weeks: int, ScrapReasonID: int):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE production_workorder SET ProductID = %s, OrderQty = %s, StockedQty = %s, ScrappedQty = %s, StartDate = NOW(), DueDate = DATE_ADD(NOW(), INTERVAL %s WEEK), EndDate = DATE_ADD(DATE_ADD(NOW(), INTERVAL %s WEEK), INTERVAL -1 DAY), ScrapReasonID = %s WHERE WorkOrderID = %s", 
            (ProductID, OrderQty, StockedQty, ScrappedQty, num_weeks, num_weeks, ScrapReasonID, WorkOrderID))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Workorder updated successfully"}

@app.put("/Comission_update/{BusinessEntityID}/{CommissionPct}")
def update_comission(BusinessEntityID: int,CommissionPct: float):
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE sales_salesperson SET CommissionPct = %s WHERE BusinessEntityID = %s", 
            (CommissionPct,BusinessEntityID))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Sales comission updated successfully"}



@app.delete("/workorder/{WorkOrderID}")
def delete_item(WorkOrderID: int):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM production_workorder WHERE WorkOrderID=%s", (WorkOrderID,))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Work Order deleted successfully"}

@app.delete("/inactive_shoppingcartitems/{days}")
def delete_inactive_shoppingcartitems(days: int):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM sales_shoppingcartitem
            WHERE DATEDIFF(CURDATE(), ModifiedDate) > %s
        """, (days,))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting data: {str(e)}")
    finally:
        cursor.close()
    return {"message": "Inactive shopping cart items deleted successfully"}

