from fastapi import FastAPI
from requests.menu_requests import menu_router
from requests.submenu_requests import submenu_router
from requests.dish_requests import dish_router


app = FastAPI()

app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)

