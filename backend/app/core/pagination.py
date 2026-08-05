import base64
import json
from typing import Generic, TypeVar

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query as SAQuery
from typing import Annotated

import uuid
from datetime import datetime

# ---------------------------------------------------------------------------
# Opaque cursor encode/decode
# ---------------------------------------------------------------------------
# The cursor carries the ordering values of the LAST row of the current page:
# the chosen sort field plus the id as tie-breaker. We serialise that dict to
# JSON, then base64-encode it so the client treats it as an opaque token and
# never depends on its internal shape.


def _json_default(value):
    """Render values that JSON cannot represent natively."""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def encode_cursor(sort_value, tiebreaker_value) -> str:
    """Encode the last row's (sort_value, tiebreaker) into an opaque cursor."""
    payload = json.dumps(
        {"s": sort_value, "t": tiebreaker_value}, default=_json_default
    )
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> dict:
    """Decode an opaque cursor back into {'s': ..., 't': ...}."""
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        data = json.loads(raw)
        if "s" not in data or "t" not in data:
            raise ValueError("missing keys")
        return data
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pagination cursor")


def _coerce(value, column):
    """Rebuild the Python type the column expects from the JSON scalar.

    Without this a datetime column would be compared against a string, and a
    UUID column against text: Postgres would either reject the query or, worse,
    compare them as text and silently return the wrong page.
    """
    if value is None:
        return None
    python_type = column.type.python_type
    try:
        if python_type is datetime:
            return datetime.fromisoformat(value)
        if python_type is uuid.UUID:
            return uuid.UUID(value)
        return python_type(value)
    except (TypeError, ValueError):
        # A cursor built for a different sort field, e.g. 'MONDAY' arriving
        # where a timestamp is expected. Client error, not a crash.
        raise HTTPException(status_code=400, detail="Invalid pagination cursor")


# ---------------------------------------------------------------------------
# Pagination parameters (FastAPI dependency)
# ---------------------------------------------------------------------------

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


class PaginationParams(BaseModel):
    limit: int
    after: str | None


def pagination_params(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    after: str | None = Query(None),
) -> PaginationParams:
    """Extract and validate pagination query params.

    limit is bounded to [1, MAX_LIMIT] by FastAPI's Query validators, so a
    client cannot ask for a million rows.
    """
    return PaginationParams(limit=limit, after=after)


# ---------------------------------------------------------------------------
# Paginated response schema (generic over the item type)
# ---------------------------------------------------------------------------

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated response: Page[IngredientOut], Page[DishOut], ..."""

    items: list[T]
    next_cursor: str | None
    has_next: bool


# ---------------------------------------------------------------------------
# The keyset paginator
# ---------------------------------------------------------------------------


def paginate_query(
    query: SAQuery,
    model,
    sort_field: str,
    params: PaginationParams,
    tiebreaker_field: str = "public_id",
    descending: bool = False,
) -> tuple[list, str | None, bool]:
    """Apply composite-keyset pagination to an existing query.

    Orders by (sort_field, tiebreaker_field). The tie-breaker is what makes the
    ordering total, and therefore the cursor unambiguous. It defaults to
    public_id rather than the primary key so that no internal identifier ever
    reaches the client: a base64 cursor is opaque by convention, not by design.
    """
    sort_col = getattr(model, sort_field)
    tie_col = getattr(model, tiebreaker_field)

    if descending:
        query = query.order_by(sort_col.desc(), tie_col.desc())
    else:
        query = query.order_by(sort_col.asc(), tie_col.asc())

    if params.after is not None:
        cursor = decode_cursor(params.after)
        last_sort = _coerce(cursor["s"], sort_col)
        last_tie = _coerce(cursor["t"], tie_col)

        # (sort, tie) strictly after the last row of the previous page,
        # with the comparison flipped when the ordering is descending.
        if descending:
            keyset = or_(
                sort_col < last_sort,
                and_(sort_col == last_sort, tie_col < last_tie),
            )
        else:
            keyset = or_(
                sort_col > last_sort,
                and_(sort_col == last_sort, tie_col > last_tie),
            )
        query = query.filter(keyset)

    rows = query.limit(params.limit + 1).all()

    has_next = len(rows) > params.limit
    items = rows[: params.limit]

    next_cursor = None
    if has_next and items:
        last = items[-1]
        next_cursor = encode_cursor(
            getattr(last, sort_field), getattr(last, tiebreaker_field)
        )

    return items, next_cursor, has_next


PaginationQuery = Annotated[PaginationParams, Depends(pagination_params)]
