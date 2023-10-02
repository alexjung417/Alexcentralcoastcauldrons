from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver")
def post_deliver_barrels(barrels_delivered: list[Barrel]):
    """ """
    print(barrels_delivered)
        
        # buys the stuff
    with db.engine.begin() as connection:
        red = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
    for Barrel in barrels_delivered:
        gold -= Barrel.price
        red += Barrel.ml_per_barrel 
    

        red = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {red}"))
        gold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}"))  
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
        
        # reads my data 
    with db.engine.begin() as connection:
        red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))
    for Barrel in wholesale_catalog:
        if red < 10 and gold > Barrel.price and Barrel.sku == "SMALL_RED_BARREL":
            return [
                {
                    "sku": "SMALL_RED_BARREL",
                    "quantity": 1
                }
            ]
        else:
            return [
            ]




