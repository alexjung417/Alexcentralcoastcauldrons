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
    with db.engine.begin() as connection:
        print(potions_delivered)
        additional_potions = sum(potion.quantity for potion in potions_delivered)
        num_red_ml = sum(potion.quantity * potion.potion_type[0] for potion in potions_delivered)
        num_blue_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)
        num_green_ml = sum(potion.quantity * potion.potion_type[1] for potion in potions_delivered)
        #num_dark_ml = sum(potion.quantity * potion.potion_type[3] for potion in potions_delivered)
        #num_teal_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)

    # changes above
    
    for PotionInventory in potions_delivered:
        connection.execute(
            sqlalchemy.text("""UPDATE potions
                            SET inventory = inventory + :additional_potions
                            WHERE type = :potion_type       
                            """)    # in the potions database need to have type as a column
                            [{"additional_potions": potions_delivered.quantity,
                            "potion_type": potions_delivered.potion_type}])

    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET
                                            num_red_ml = num_red_ml - :num_red_ml,
                                            num_blue_ml = num_blue_ml - :num_blue_ml , 
                                            num_green_ml = num_green_ml - :num_green_ml,
                                            num_blue_ml = num_blue_ml - :num_teal_ml , 
                                            num_green_ml = num_green_ml - :num_teal_ml,
                                            """), # need to subtract the amount needed for yellow ml
                                             [{"num_red_ml": num_red_ml, "num_blue_ml": num_blue_ml, "num_green_ml": num_green_ml}])
    return "OK"

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
        # num_dark_ml = connection.execute(sqlalchemy.text("SELECT num_dark_ml FROM global_inventory")).first().num_dark_ml
    
    a = []

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    if num_red_ml >= 200:
        total = num_red_ml //100
        a.append({
                "potion_type": [100, 0, 0, 0],
                "quantity": total
                })
    elif num_green_ml >= 200:
        total = num_green_ml // 100
        a.append({
                "potion_type": [0, 100,0, 0],
                "quantity": total
                })
    elif num_blue_ml >= 200:
        total = num_blue_ml // 100
        a.append({
                "potion_type": [0, 0, 100, 0],
                "quantity": total
                })
    # elif (50 <= num_blue_ml < 200) &(50 <= num_green_ml < 200):
    #     total = num_blue_ml // 50
    #     a.append({
    #         "potion_type": [0,50,50,0],
    #         "quantity": total
    #     })
    return a