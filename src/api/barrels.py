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

    goldg = 0
    redm = 0
    bluem = 0
    greenm = 0
    #dm = 0

        # buys the stuff
    for Barrel in barrels_delivered:
        goldg = goldg + (Barrel.price * Barrel.quantity)
        if Barrel.potion_type == [1,0,0,0]:
            redm += Barrel.ml_per_barrel * Barrel.quantity
        elif Barrel.potion_type ==  [0,0,1,0]:
            bluem += Barrel.ml_per_barrel * Barrel.quantity
        elif Barrel.potion_type == [0,1,0,0]:
            greenm += Barrel.ml_per_barrel * Barrel.quantity
        #elif Barrel.potion_type == [0,0,0,1]:
        #    dm = Barrel.ml_per_barrel * Barrel.quantity  #need to add this 
    
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO inventory_ledger(gold,num_red_ml, num_blue_ml, num_green_ml) 
                                            Values(0 - :goldg, :redm, :bluem, :greenm)
                                            """),
                                        [{"goldg": goldg, "redm": redm, "bluem": bluem, "greenm": greenm}])
 
    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)
        # reads my data 
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT sum(gold) as gold FROM inventory_ledger")).first().gold 
        potions = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        a = []
        for potion in potions:
            pots = connection.execute(sqlalchemy.text("""SELECT SUM(new_potion) as new_potion
                                                            FROM potion_ledger
                                                            WHERE potion_id = :id
                                                        """), 
                                                        [{"id": potion.id}]).first()
                                                        # this should be running through all potions and counting the amount of each potion type
            pots = pots.new_potion
            if pots is None: 
                pots = 0   
            for Barrel in wholesale_catalog:
                ptype = [1 if x != 0 else 0 for x in potion.type]
                if (pots < 5) & (gold >= Barrel.price) & (Barrel.potion_type == ptype):
                    a.append({
                                "sku": Barrel.sku,
                                "ml_per_barrel": Barrel.ml_per_barrel,
                                "potion_type": Barrel.potion_type,
                                "price": Barrel.price,
                                "quantity": gold // Barrel.price
                                })
                    gold -= Barrel.price * (gold//Barrel.price)
    print(a)
    return a
# [{"sku": "MEDIUM_RED_BARREL", "ml_per_barrel": 2500, "potion_type": [1, 0, 0, 0], "price": 250, "quantity": 10
#   },{"sku": "SMALL_RED_BARREL", "ml_per_barrel": 500, "potion_type": [1, 0, 0, 0], "price": 100, "quantity": 10
#   },{"sku": "MEDIUM_GREEN_BARREL", "ml_per_barrel": 2500, "potion_type": [0, 1, 0, 0], "price": 250, "quantity": 10
#   },{"sku": "SMALL_GREEN_BARREL", "ml_per_barrel": 500, "potion_type": [0, 1, 0, 0], "price": 100, "quantity": 10
#   },{"sku": "MEDIUM_BLUE_BARREL", "ml_per_barrel": 2500, "potion_type": [0, 0, 1, 0], "price": 300, "quantity": 10
#   },{"sku": "SMALL_BLUE_BARREL", "ml_per_barrel": 500, "potion_type": [0, 0, 1, 0], "price": 120, "quantity": 10
#   },{"sku": "MINI_RED_BARREL", "ml_per_barrel": 200, "potion_type": [1, 0, 0, 0], "price": 60, "quantity": 1
#   },{"sku": "MINI_GREEN_BARREL", "ml_per_barrel": 200, "potion_type": [0, 1, 0, 0], "price": 60, "quantity": 1
#   },{"sku": "MINI_BLUE_BARREL", "ml_per_barrel": 200, "potion_type": [0, 0, 1, 0], "price": 60, "quantity": 1}]