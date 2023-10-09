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
        table = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

        first = table.first()
        gold = first.gold
        red = first.num_red_ml
        blue = first.num_blue_ml
        green = first.num_green_ml

    for Barrel in barrels_delivered:
        if Barrel.sku == "MINI_RED_BARREL":
            gold -= Barrel.price
            red += Barrel.ml_per_barrel
        if Barrel.sku ==  "MINI_BLUE_BARREL":
            gold -= Barrel.price
            blue += Barrel.ml_per_barrel
        if Barrel.sku == "MINI_GREEN_BARREL":
            gold -= Barrel.price
            green += Barrel.ml_per_barrel
    
    with db.engine.begin() as connection:
        r = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {red}"))
        g = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}"))
        b = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {blue}"))
        gr = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {green}"))  
    return "OK new gold"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

        
        # reads my data 
    with db.engine.begin() as connection:
        table = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

        first = table.first()
        gold = first.gold
        red = first.num_red_potions
        green = first.num_green_potions
        blue = first.num_blue_potions
        
    a = []
    for Barrel in wholesale_catalog:
        if int(red) < 1 and int(gold) >= Barrel.price and Barrel.sku == "MINI_RED_BARREL":
            gold -=Barrel.price
            a.append({
                    "sku": "MINI_RED_BARREL",
                    "quantity": 1
                    })
        elif int(blue) < 1 and int(gold) >= Barrel.price and Barrel.sku == "MINI_BLUE_BARREL":
            gold -= Barrel.price
            a.append({
                    "sku": "MINI_BLUE_BARREL",
                    "quantity": 1
                    })
        elif int(green) < 1 and int(gold) >= Barrel.price and Barrel.sku == "MINI_GREEN_BARREL":
            gold -= Barrel.price    
            a.append({
                    "sku": "MINI_GREEN_BARREL",
                    "quantity": 1
                    })  
        
    return a
# [Barrel(sku='LARGE_RED_BARREL', ml_per_barrel=10000, potion_type=[1, 0, 0, 0], price=500, quantity=30), 
# Barrel(sku='MEDIUM_RED_BARREL', ml_per_barrel=2500, potion_type=[1, 0, 0, 0], price=250, quantity=10), 
# Barrel(sku='SMALL_RED_BARREL', ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=10), 
# Barrel(sku='MINI_RED_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1)]