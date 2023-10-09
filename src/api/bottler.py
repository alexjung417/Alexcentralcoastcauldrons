from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

# decrease teh red ml and increases poitons

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver")
def post_deliver_bottles(potions_delivered: list[PotionInventory]):
    """ """
    print(potions_delivered)
    with db.engine.begin() as connection:
        num_r_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).first().num_red_ml
        new_red = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).first().num_red_potions
        num_g_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).first().num_green_ml
        new_green = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).first().num_green_potions
        num_b_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).first().num_blue_ml
        new_blue = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).first().num_blue_potions


    # changes above
    
    for PotionInventory in potions_delivered:
        if PotionInventory.potion_type == [100,0,0,0] :
            num_r_ml -= 100 * PotionInventory.quantity
            new_red += PotionInventory.quantity
        if PotionInventory.potion_type == [0,100,0,0]:
            num_g_ml -= 100 * PotionInventory.quantity
            new_green += PotionInventory.quantity
        if PotionInventory.potion_type == [0,0,100,0]:
            num_b_ml -= 100 * PotionInventory.quantity
            new_blue += PotionInventory.quantity

    with db.engine.begin() as connection:
        mlr = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {num_r_ml}"))
        rpotions = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_potions = {new_red}"))
        mlb = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = {num_b_ml}"))
        bpotions = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_potions = {new_blue}"))
        mlg = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = {num_g_ml}"))
        gpotions = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_potions = {new_green}"))
    return "OK", new_red, "red potions"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        num_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).first().num_red_ml
        num_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).first().num_green_ml
        num_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).first().num_blue_ml
    r = 0
    b = 0
    g = 0    

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    if int(num_red_ml) >= 500:
        r = 5
    if int(num_blue_ml) >= 500:
        b = 5
    if int(num_green_ml) >= 500:
        g = 5
    return [{
                "potion_type": [100, 0, 0, 0],
                "quantity": r,
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": b,
            },
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": g,
            }] 