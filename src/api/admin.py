from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE inventory_ledger CASCADE"))
        connection.execute(sqlalchemy.text("TRUNCATE potion_ledger CASCADE"))
        transaction_id = connection.execute(sqlalchemy.text("INSERT INTO inventory_ledger(gold) VALUES(100) RETURNING id")).first().id
        connection.execute(sqlalchemy.text("""
            INSERT INTO potion_ledger (transaction)
            VALUES (:transaction_id)
            """), {"transaction_id": transaction_id})
    return "OK"


@router.get("/shop_info/")
def get_shop_info():
    """ """

    # TODO: Change me!
    return {
        "shop_name": "Panda Potions",
        "shop_owner": "Alexander Jung",
    }

