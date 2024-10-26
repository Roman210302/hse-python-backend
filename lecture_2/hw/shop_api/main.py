from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import PositiveInt, NonNegativeFloat, NonNegativeInt 
from typing import List, Optional, Iterable, Annotated
from http import HTTPStatus
from lecture_2.hw.shop_api.models import Item, ItemInCart, Cart

app = FastAPI(title = 'Shop API')

def cart_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

def item_id_generator() -> Iterable[int]:
    i = 0
    while True:
        yield i
        i += 1

my_cart_id_generator = cart_id_generator()
my_item_id_generator = item_id_generator()

carts = []

items = []

#done
@app.post('/cart')
def create_cart(response: Response):
    current_cart_id = next(my_cart_id_generator)
    current_cart = Cart(id=current_cart_id, items=[], price=0.0)
    carts.append(current_cart)
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = f'/cart/{current_cart_id}'
    return {"id": current_cart_id}

#done
@app.get('/cart/{id}')
def get_cart(id: int):    
    cart = list(filter(lambda cart: cart.id == id, carts))
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    return cart[0]

#done
@app.get('/cart')
async def list_carts(offset: Annotated[NonNegativeInt, Query()] = 0,
               limit: Annotated[PositiveInt, Query()] = 10,
               min_price: Annotated[NonNegativeFloat, Query()] = None,
               max_price: Annotated[NonNegativeFloat, Query()] = None,
               min_quantity: Annotated[NonNegativeInt, Query()] = None,
               max_quantity: Annotated[NonNegativeInt, Query()] = None):
    
    current_carts = carts[offset:offset+limit]
    if min_price is not None:
        current_carts = [cart for cart in current_carts if cart.price >= min_price]
    if max_price is not None:
        current_carts = [cart for cart in current_carts if cart.price <= max_price]
    if min_quantity is not None:
        current_carts = [cart for cart in current_carts if sum(item.quantity for item in cart.items) >= min_quantity]
    if max_quantity is not None:
        current_carts = [cart for cart in current_carts if sum(item.quantity for item in cart.items) <= max_quantity]
    return current_carts

#done
@app.post('/cart/{cart_id}/add/{item_id}')
def add_item_to_cart(cart_id: int, item_id: int):

    current_cart = list(filter(lambda cart: cart.id == cart_id, carts))

    if not current_cart:
        raise HTTPException(status_code=404,
                            detail="Cart not found")
    
    cart = current_cart[0]

    current_item = list(filter(lambda item: item.id == item_id, items))
    if not current_item:
        raise HTTPException(status_code=404,
                            detail="Item not found or deleted")
    
    item = current_item[0]
    
    for cart_item in cart.items:
        if cart_item.id == item_id:
            cart_item.quantity += 1
            break
    else:
        cart.items.append(ItemInCart(id=item.id,
                                    name=item.name,
                                    quantity=1,
                                    available=True))
    cart.price += item.price
    return {"status": "Item added"}

#done
@app.post('/item')
def create_item(response: Response, item: Item):
    current_item_id = next(my_item_id_generator)
    item.id = current_item_id
    items.append(item)
    response.status_code = status.HTTP_201_CREATED
    response.headers["Location"] = f'/item/{current_item_id}'
    return item

#done    
@app.get('/item/{id}')
async def get_cart(id: int):    
    item = list(filter(lambda item: item.id == id, items))[0]
    if not item or item.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return item


#done
@app.get('/item')
def list_carts(offset: Annotated[NonNegativeInt, Query()] = 0,
               limit: Annotated[PositiveInt, Query()] = 10,
               min_price: Annotated[NonNegativeFloat, Query()] = None,
               max_price: Annotated[NonNegativeFloat, Query()] = None,
               show_deleted: Annotated[bool, Query()] = False):
    current_items = items[offset:offset+limit]
    if min_price is not None:
        current_items = [item for item in current_items if item.price >= min_price]
    if max_price is not None:
        current_items = [item for item in current_items if item.price <= max_price]
    if not show_deleted:
        current_items = [item for item in current_items if not item.deleted]        
    return current_items

#done
@app.put('/item/{id}')
def update_item(id: int, item: Item):
    item_to_edit = list(filter(lambda item: item.id == id, items))[0]
    if not item_to_edit or item_to_edit.deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    index = items.index(item_to_edit)
    item.id = id
    items[index] = item
    return item

#done
@app.patch('/item/{id}')
def patch_item(id: int, item: dict):
    item_to_patch = list(filter(lambda item: item.id == id, items))[0]
    if not item_to_patch or item_to_patch.deleted:
        raise HTTPException(status_code=304, detail="Item not found")
    for key, value in item.items():
        if key == "deleted" and value:
            raise HTTPException(status_code=422, detail="Cannot modify attribute deleted")
        if key not in item_to_patch.__fields__:
            raise HTTPException(status_code=422,
                                detail=f"Attribute '{key}' not found")
        setattr(item_to_patch, key, value)
    return item_to_patch

#done
@app.delete('/item/{id}')
def delete_item(id: int):
    item = list(filter(lambda item: item.id == id, items))[0]
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    index = items.index(item)
    items[index].deleted = True
    return items[index]
