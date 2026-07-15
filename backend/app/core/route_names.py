from enum import StrEnum


class RouteName(StrEnum):
    """Single source of truth for route *names*, used for reverse routing.

    Every route declares its own path once (on the router) and its name from
    this enum. Everywhere else -- tests, redirects, internal links -- refers to
    the route by name via app.url_path_for(RouteName.X), never by a literal
    path string. Renaming a path on the router then requires no changes here.
    """

    # --- auth ---
    AUTH_REGISTER = "auth:register"
    AUTH_LOGIN = "auth:login"

    # --- dishes ---
    DISH_LIST = "dishes:list"
    DISH_CREATE = "dishes:create"
    DISH_DETAIL = "dishes:detail"
    DISH_UPDATE = "dishes:update"
    DISH_DELETE = "dishes:delete"

    # --- ingredients ---
    INGREDIENT_LIST = "ingredients:list"
    INGREDIENT_CREATE = "ingredients:create"
    INGREDIENT_DETAIL = "ingredients:detail"
    INGREDIENT_UPDATE = "ingredients:update"
    INGREDIENT_DELETE = "ingredients:delete"

    # --- weekly plans ---
    WEEKLY_PLAN_LIST = "weekly_plans:list"
    WEEKLY_PLAN_CREATE = "weekly_plans:create"
    WEEKLY_PLAN_DETAIL = "weekly_plans:detail"
    WEEKLY_PLAN_UPDATE = "weekly_plans:update"
    WEEKLY_PLAN_DELETE = "weekly_plans:delete"

    # --- shopping lists ---
    SHOPPING_LIST_LIST = "shopping_lists:list"
    SHOPPING_LIST_CREATE = "shopping_lists:create"
    SHOPPING_LIST_DETAIL = "shopping_lists:detail"
    SHOPPING_LIST_UPDATE = "shopping_lists:update"
    SHOPPING_LIST_DELETE = "shopping_lists:delete"
    SHOPPING_LIST_ADD_ITEM = "shopping_lists:add_item"
    SHOPPING_LIST_UPDATE_ITEM = "shopping_lists:update_item"
    SHOPPING_LIST_DELETE_ITEM = "shopping_lists:delete_item"
