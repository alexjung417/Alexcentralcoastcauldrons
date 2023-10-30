from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum

import sqlalchemy
from src import database as db


# test the new search in chrome edit and developer

# customers give you gold and decrease potions

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "asc"
    desc = "desc"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    with db.engine.begin() as connection:
        if (search_page == ""):
            current = 0 
        else:
             int(search_page)
        cart_item = connection.execute(sqlalchemy.text(f"""SELECT
                                                        cart_item.cart_id as line_item_id,
                                                        cart_item.item_sku as item_sku,
                                                        carts.name as customer_name,
                                                        inventory_ledger.gold as line_gold,
                                                        inventory_ledger.created_at as timestamp
                                                        FROM cart_item
                                                        JOIN carts on cart_item.cart_id = carts.id
                                                        JOIN inventory_ledger on carts.transaction = inventory_ledger.id
                                                        JOIN potion_ledger on potion_ledger.transaction = inventory_ledger.id
                                                        ORDER BY {sort_col.value} {sort_order.value}
                                                        LIMIT 6
                                                        OFFSET {str(current)}
                                                        """)).fetchall()
    results = []
    for item in cart_item:
        if len(results) < 5:
            results.append({"line_item_id": item.line_item_id,
        "item_sku": item.item_sku,
        "customer_name": item.customer_name,
        "line_item_total": item.line_gold,
        "timestamp": item.timestamp,})
    previous = current - 5
    previous = "" if previous < 0 else str(previous)
    next = current + 5
    next = "" if len(cart_item) < 6 else str(next) 
    return {
        "previous": previous,
        "next": next,
        "results": results
    }
        

    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

class NewCart(BaseModel):
    customer: str


@router.post("/")
def create_cart(new_cart: NewCart):
    """ """
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("INSERT INTO carts(name) VALUES (:name)"), [{"name": new_cart.customer}])
        i = connection.execute(sqlalchemy.text("SELECT * FROM carts WHERE name = :name"),[{"name": new_cart.customer}]).first().id
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
        connection.execute(sqlalchemy.text("""INSERT INTO cart_item(quantity, cart_id, item_sku) 
                                            SELECT  :num, :cart_id, potions.item_sku      
                                            FROM potions 
                                            WHERE potions.item_sku = :item_sku """),
                                            [{"num": num, "cart_id": cart_id, "item_sku": item_sku}])
                                        # there is an syntax error at or near FROM
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
        result = connection.execute(sqlalchemy.text("""SELECT sum(cart_item.quantity * potions.price) as total_gold,
                                            sum(cart_item.quantity) as total_potions
                                            FROM cart_item 
                                            JOIN potions on potions.item_sku = cart_item.item_sku 
                                            where cart_item.cart_id = :cart_id """),
                                            [{"cart_id": cart_id}])
        total_gold, total_potions = result.first()
        transact = connection.execute(sqlalchemy.text("""INSERT INTO inventory_ledger(gold)
                                            VALUES (:total_gold)
                                            RETURNING id """).first().id
                                            [{"total_gold": total_gold}])
        connection.execute(sqlalchemy.text("""INSERT INTO potion_ledger(potion_id,new_potion,transaction) 
                                                SELECT potion.id, 0 - cart_item.quantity, :transact
                                                FROM cart_item
                                                JOIN potions on potions.item_sku = cart_item.item_sku
                                                WHERE cart_item.cart_id = :cart_id"""),
                                                [{"cart_id": cart_id, "transact":transact}])
        connection.execute(sqlalchemy.text("""UPDATE carts
                                            SET transaction = :transact
                                            WHERE cart.id = :cart_id"""),[{"cart_id": cart_id,"transact":transact}])                                    

    # need to update the gold can probably loop through the same way 
    return {"total_potions_bought": total_potions, "total_gold_paid": total_gold}
