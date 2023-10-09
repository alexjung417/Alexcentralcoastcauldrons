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

cart = {}
@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    return {"cart_id": 1}


@router.get("/{cart_id}")
def get_cart(cart_id: int):
    """ """

    return {}


class CartItem(BaseModel):
    quantity: int


@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """

    cart[cart_id][item_sku] = cart_item.quantity
    # need to put this in my database
    # to grab the right amount of items 
    return "OK"


class CartCheckout(BaseModel):
    payment: str

@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """ """     # this is wrong 
    with db.engine.begin() as connection:
        table = connection.execute(sqlalchemy.text("SELECT * FROM global_inventory"))

        first = table.first()
        gold = first.gold
        red = first.num_red_potions

    cur_cart = cart[cart_id]
    #for items in cur_cart: 
    gold +=1
    red +=50
    red = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = {red}"))
    gold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = {gold}")) 
    return {"total_potions_bought": 1, "total_gold_paid": 50}
