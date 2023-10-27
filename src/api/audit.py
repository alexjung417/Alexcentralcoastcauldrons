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
                                                    SUM(num_red_ml + num_blue_ml + num_green_ml) as ml,
                                                    SUM(gold) as gold  
                                                    FROM inventory_ledger
                                                    """)).first()       # need this for each
        ml = result.ml
        gold = result.gold
        pots = connection.execute(sqlalchemy.text("""SELECT SUM(new_potion) as new_potions
                                                        FROM potion_ledger
                                                    """)).first().new_potions
        if pots is None:
            pots = 0
        
    
    return {
            "ml": ml,
            "potions": pots,
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
