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
            pots = connection.execute(sqlalchemy.text("""SELECT SUM(new_potion) as new_potion
                                                            FROM potion_ledger
                                                            WHERE potion_id = :id
                                                        """), 
                                                        [{"id": potion.id}]).first()
            pots = pots.new_potion
            if pots is not None and pots > 0 :
                a.append({
                        "sku": potion.item_sku,           # must change 
                        "name": potion.name,
                        "quantity": pots,
                        "price": potion.price,
                        "potion_type": potion.type,
                    })
    # only if there is more than one
    return a