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
        num_teal_ml = sum(potion.quantity * potion.potion_type[2] for potion in potions_delivered)

    # changes above
    
        for PotionInventory in potions_delivered:
            connection.execute(
                sqlalchemy.text("""INSERT INTO potion_ledger(potion_id, new_potion)
                                Select potions.id, :additional_potions
                                FROM potions
                                WHERE potions.type = :potion_type       
                                """),    # in the potions database need to have type as a column
                                [{"additional_potions": PotionInventory.quantity,
                                "potion_type": PotionInventory.potion_type}])

        connection.execute(sqlalchemy.text("""INSERT INTO inventory_ledger(num_red_ml, num_blue_ml, num_green_ml) 
                                            Values(0 - :num_red_ml, 0 - :num_blue_ml - :num_teal_ml, 0 - :num_green_ml - :num_teal_ml)
                                            """),
                                        [{"num_red_ml": num_red_ml, "num_blue_ml": num_blue_ml, "num_green_ml": num_green_ml, "num_teal_ml": num_teal_ml}])
    return "OK"

# Gets called 4 times a day
@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    a = []
    min_pot = 5

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT
                                                    SUM(num_red_ml) as red_ml,
                                                    SUM(num_blue_ml) as blue_ml, 
                                                    SUM(num_green_ml) as green_ml  
                                                    FROM inventory_ledger
                                                    """)).first()       # need this for each
        red_ml = result.red_ml
        blue_ml = result.blue_ml
        green_ml = result.green_ml
        potions = connection.execute(sqlalchemy.text( "SELECT * FROM potions"))
        for potion in potions:
            pots = connection.execute(sqlalchemy.text("""SELECT SUM(new_potion) as pots
                                                            FROM potion_ledger
                                                            WHERE potion_id = :id
                                                        """), 
                                                        [{"id": potion.id}]).first()
            pots = pots.pots
            if pots is None:
                pots = 0
            new_pots = 0
            if (pots < min_pot):
                red = potion.type[0]
                green = potion.type[1]
                blue = potion.type[2]
                #dark = potion.type[3]
                    # do for each ml 
                while(red <= red_ml) & (pots < min_pot) & (blue <= blue_ml) & (green <= green_ml):
                    pots += 1
                    red_ml -= red
                    blue_ml -= blue
                    green_ml -= green
                    new_pots += 1
            if(new_pots > 0):
                a.append({
                "potion_type": potion.type,
                "quantity": new_pots
                })
    return a

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
