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
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).first().num_red_ml
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).first().num_green_ml
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).first().num_blue_ml
        #dark_ml = connection.execute(sqlalchemy.text("SELECT num_dark_ml FROM global_inventory")).first().num_dark_ml
        gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).first().gold
        red = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE name = 'RED'")).first().quantity 
        blue = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE name = 'BLUE'")).first().quantity 
        green = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE name = 'GREEN'")).first().quantity
        #dark = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,0,100]'")).first().quantity
        yellow = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE name = 'teal'")).first().quantity
        
    
    return {"red_potions": red,
            "blue_potions": blue,
            "green_potions": green,
            #"dark_potions": dark,
            "yellow_potions": yellow, 
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
