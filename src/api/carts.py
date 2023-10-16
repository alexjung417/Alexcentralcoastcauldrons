from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth

import sqlalchemy
from src import database as db

# customers give you gold and decrease potions

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts(name) VALUES(:new_cart)"), [{"name": new_cart}])
        i = connection.execute(sqlalchemy.text("SELECT * FROM carts")).first().id
    return {"cart_id": i}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    num = cart_item.quantity
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""INSERT INTO cart_item (item_sku,quantity,cart_id) 
                                            VALUES (potions.item_sku,  :num, :cart_id)      
                                            FROM potions WHERE potions.item_sku = :item_sku """),
                                            [{"num": num, "cart_id": cart_id, "item_sku": item_sku}])
                                        # there is an syntax error at or near FROM
#     INSERT INTO cart_item (cart_id, quantity, potions_id) 
# SELECT :cart_id, :quantity, potions.id 
# FROM potions WHERE potions.sku = :item_sku
    # need to put this in my database
    # to grab the right amount of items 
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """     # this is wrong 
   #https://observablehq.com/@calpoly-pierce/ddl-dml
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("""UPDATE potions
                                            SET inventory = potions.inventory - cart_item.quantity
                                            FROM cart_item
                                            WHERE potions.item_sku = cart_item.item_sku and cart_item.cart_id = :cart_id"""),
                                            [{"cart_id": cart_id}])

        connection.execute(sqlalchemy.text("""UPDATE global_inventory
                                            SET gold =  global_inventory.gold + (cart_item.quantity * potions.price)
                                            FROM cart_item, potions
                                            WHERE potions.item_sku = cart_item.item_sku and cart_item.cart_id = :cart_id"""),
                                            [{"cart_id": cart_id}])

    #UPDATE global_inventory
    #SET gold = global_inventory.gold + (cart_item.quantity * potions.price)
    #FROM cart_item, potions
    #WHERE potions.item.sku = cart_item.item_sku and cart_item.cart_id = :cart_id;

    # need to update the gold can probably loop through the same way 


    return {"total_potions_bought": 0, "total_gold_paid": 0}
