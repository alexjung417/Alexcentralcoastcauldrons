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
        red = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[100,0,0,0]'")).first().inventory
        rprice  = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[100,0,0,0]'")).first().price
        blue = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,100,0]'")).first().inventory
        bprice = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,100,0]'")).first().price  
        green = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,100,0,0]'")).first().inventory
        gprice = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,100,0,0]'")).first().price
        teal = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,50,50,0]'")).first().inventory
        tprice = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,50,50,0]'")).first().price
        rtype = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[100,0,0,0]'")).first().type
        gtype = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,100,0,0]'")).first().type
        btype = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,100,0]'")).first().type
        ttype = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,50,50,0]'")).first().type
        # rname = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[100,0,0,0]'")).first().name
        # gname = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,100,0,0]'")).first().name
        # bname = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,100,0]'")).first().name
        # tname = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,50,50,0]'")).first().name
        # rsku = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[100,0,0,0]'")).first().item_sku
        # gsku = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,100,0,0]'")).first().item_sku
        # bsku = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,0,100,0]'")).first().item_sku
        # tsku = connection.execute(sqlalchemy.text("SELECT * FROM potions WHERE type = '[0,50,50,0]'")).first().item_sku

    # only if there is more than one
    a = []
    if red > 1:
        a.append({
                "sku": "RED",           # must change 
                "name": "red potion",
                "quantity": red,
                "price": rprice,
                "potion_type": rtype,
            })
    elif blue > 1:
        a.append({
                "sku": "BLUE",
                "name": "blue potion",
                "quantity": blue,
                "price": bprice,
                "potion_type": btype, 
            })
    elif green >1:
        a.append({
                "sku": "GREEN",
                "name": "green potion",
                "quantity": green,
                "price": gprice,
                "potion_type": gtype, 
            })
    elif teal >1:
        a.append({
                "sku": "TEAL",
                "name": "yellow potion",
                "quantity": teal,
                "price": tprice,
                "potion_type": ttype, 
            })
    return a