from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    # Can return a max of 20 items.

    with db.engine.begin() as connection:
        potions = connection.execute(sqlalchemy.text("SELECT * FROM potions"))
        a = [] 
        for potion in potions:
            if potion.quantity > 0:
                a.append({
                        "sku": potion.item_sku,           # must change 
                        "name": potion.name,
                        "quantity": potion.quantity,
                        "price": potion.price,
                        "potion_type": potion.type,
                    })
    # only if there is more than one

    return a