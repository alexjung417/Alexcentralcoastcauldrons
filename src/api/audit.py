from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math

import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/audit",
    tags=["audit"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/inventory")
def get_inventory():        #need to change when I start pulling from the 
    """ """
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("""SELECT
                                                    SUM(num_red_ml) as red_ml,
                                                    SUM(num_blue_ml) as blue_ml, 
                                                    SUM(num_green_ml) as green_ml,
                                                    SUM(gold) as gold  
                                                    FROM inventory_ledger
                                                    """)).first()       # need this for each
        red_ml = result.red_ml
        blue_ml = result.blue_ml
        green_ml = result.green_ml
        result = result.gold
        # potions = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        # for potion in potions:
        #     pots = connection.execute(sqlalchemy.text("""SELECT SUM(new_potion) as pots
        #                                                     FROM potion_ledger
        #                                                     WHERE potion_id = :id
        #                                                 """), 
        #                                                 [{"id": potion.id}]).first().new_potion
        
    
    return {
    # "red_potions": red,
    #         "blue_potions": blue,
    #         "green_potions": green,
    #         #"dark_potions": dark,
    #         "yellow_potions": yellow, 
            "red_ml": red_ml, 
            "blue_ml": blue_ml,
            "green_ml": green_ml,
            #"dark_ml": dark_ml,
            "gold": gold}

class Result(BaseModel):
    gold_match: bool
    barrels_match: bool
    potions_match: bool

# Gets called once a day
@router.post("/results")
def post_audit_results(audit_explanation: Result):
    """ """
    print(audit_explanation)

    return "OK"
