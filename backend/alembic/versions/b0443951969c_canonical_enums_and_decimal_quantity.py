"""canonical enums and decimal quantity

Revision ID: b0443951969c
Revises: 38a70f4f8fce
Create Date: 2026-08-03 13:59:20.002595

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b0443951969c"
down_revision: Union[str, Sequence[str], None] = "38a70f4f8fce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# These values are deliberately hardcoded rather than imported from
# app.core.enums: a migration is a snapshot of one moment in time. If it read
# the live enum, replaying the history after the enum changes would produce a
# different database than the one this revision originally created.

DAY_MAP = {
    "lunedì": "MONDAY",
    "martedì": "TUESDAY",
    "mercoledì": "WEDNESDAY",
    "giovedì": "THURSDAY",
    "venerdì": "FRIDAY",
    "sabato": "SATURDAY",
    "domenica": "SUNDAY",
}
MEAL_MAP = {"colazione": "BREAKFAST", "pranzo": "LUNCH", "cena": "DINNER"}
CATEGORY_MAP = {
    "Verdura": "VEGETABLES",
    "Frutta": "FRUIT",
    "Carne e pesce": "MEAT_AND_FISH",
    "Pasta e cereali": "PASTA_AND_GRAINS",
}

DAY_VALUES = tuple(DAY_MAP.values())
MEAL_VALUES = tuple(MEAL_MAP.values())
CATEGORY_VALUES = (
    "VEGETABLES",
    "FRUIT",
    "MEAT_AND_FISH",
    "PASTA_AND_GRAINS",
    "DAIRY",
    "PANTRY",
    "BEVERAGES",
    "HOUSEHOLD",
    "OTHER",
)

CATEGORY_TABLES = ("ingredients", "shopping_list_items")


def _in_clause(values) -> str:
    """Render a tuple of strings as a SQL IN list."""
    return ", ".join(f"'{value}'" for value in values)


def _translate(table: str, column: str, mapping: dict) -> None:
    """Rewrite every old value of `column` into its canonical counterpart."""
    for old, new in mapping.items():
        op.execute(
            sa.text(
                f"UPDATE {table} SET {column} = :new WHERE {column} = :old"
            ).bindparams(new=new, old=old)
        )


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Translate the data first. The CHECK constraints added in step 3 would
    #    be rejected outright by any row still holding an Italian value.
    _translate("weekly_plan_dishes", "day_of_week", DAY_MAP)
    _translate("weekly_plan_dishes", "meal_type", MEAL_MAP)

    for table in CATEGORY_TABLES:
        _translate(table, "shopping_category", CATEGORY_MAP)
        # Safety net: shopping_category used to be free text, so a database
        # that was not seeded from our JSON files may hold anything at all.
        # Anything unrecognised becomes OTHER instead of blocking the upgrade.
        op.execute(
            f"UPDATE {table} SET shopping_category = 'OTHER' "
            f"WHERE shopping_category NOT IN ({_in_clause(CATEGORY_VALUES)})"
        )

    # 2. Widen quantity so fractional amounts (0.5 kg) become expressible.
    op.alter_column(
        "shopping_list_items",
        "quantity",
        type_=sa.Numeric(10, 3),
        existing_type=sa.Integer(),
        existing_nullable=True,
    )

    # 3. Lock the vocabulary in at the database level. Autogenerate does not
    #    detect CHECK constraints, so these are written by hand.
    op.create_check_constraint(
        "ck_weekly_plan_dishes_day_of_week",
        "weekly_plan_dishes",
        f"day_of_week IN ({_in_clause(DAY_VALUES)})",
    )
    op.create_check_constraint(
        "ck_weekly_plan_dishes_meal_type",
        "weekly_plan_dishes",
        f"meal_type IN ({_in_clause(MEAL_VALUES)})",
    )
    op.create_check_constraint(
        "ck_ingredients_shopping_category",
        "ingredients",
        f"shopping_category IN ({_in_clause(CATEGORY_VALUES)})",
    )
    op.create_check_constraint(
        "ck_shopping_list_items_shopping_category",
        "shopping_list_items",
        f"shopping_category IN ({_in_clause(CATEGORY_VALUES)})",
    )


def downgrade() -> None:
    """Downgrade schema.

    Not perfectly lossless: rows that the safety net above collapsed into
    OTHER cannot be restored to their original free text, and fractional
    quantities are rounded when the column narrows back to an integer.
    """
    # 1. Drop the constraints first, or the reverse translation below would
    #    violate them on its very first row.
    op.drop_constraint(
        "ck_shopping_list_items_shopping_category",
        "shopping_list_items",
        type_="check",
    )
    op.drop_constraint("ck_ingredients_shopping_category", "ingredients", type_="check")
    op.drop_constraint(
        "ck_weekly_plan_dishes_meal_type", "weekly_plan_dishes", type_="check"
    )
    op.drop_constraint(
        "ck_weekly_plan_dishes_day_of_week", "weekly_plan_dishes", type_="check"
    )

    # 2. Narrow quantity back. Postgres would apply its assignment cast on its
    #    own; USING is spelled out so the rounding is visible in the migration
    #    rather than implied.
    op.alter_column(
        "shopping_list_items",
        "quantity",
        type_=sa.Integer(),
        existing_type=sa.Numeric(10, 3),
        existing_nullable=True,
        postgresql_using="quantity::integer",
    )

    # 3. Translate the data back into the original Italian values.
    _translate("weekly_plan_dishes", "day_of_week", {v: k for k, v in DAY_MAP.items()})
    _translate("weekly_plan_dishes", "meal_type", {v: k for k, v in MEAL_MAP.items()})
    for table in CATEGORY_TABLES:
        _translate(table, "shopping_category", {v: k for k, v in CATEGORY_MAP.items()})
