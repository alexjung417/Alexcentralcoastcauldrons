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

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
        
        # reads my data 
    with db.engine.begin() as connection:
        red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory"))
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory"))

    while (red < 10) and (gold > 50):
        red += 1
        gold -= 50
    with db.engine.begin() as connection:
        red = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = red"))
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold"))    

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1
        }
    ]


