import base64
import json
from typing import Generic, TypeVar

from fastapi import Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query as SAQuery

# ---------------------------------------------------------------------------
# Opaque cursor encode/decode
# ---------------------------------------------------------------------------
# The cursor carries the ordering values of the LAST row of the current page:
# the chosen sort field plus the id as tie-breaker. We serialise that dict to
# JSON, then base64-encode it so the client treats it as an opaque token and
# never depends on its internal shape.


def encode_cursor(sort_value, id_value: int) -> str:
    """Encode the last row's (sort_value, id) into an opaque base64 cursor."""
    payload = json.dumps({"s": sort_value, "id": id_value})
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> dict:
    """Decode an opaque cursor back into {'s': sort_value, 'id': id_value}.

    Raises HTTP 400 if the cursor is malformed -- a client sending garbage
    must get a clean client error, never a 500.
    """
    try:
        raw = base64.urlsafe_b64decode(cursor.encode("utf-8"))
        data = json.loads(raw)
        # minimal shape validation
        if "s" not in data or "id" not in data:
            raise ValueError("missing keys")
        return data
    except Exception:
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
) -> tuple[list, str | None, bool]:
    """Apply composite-keyset pagination to an existing SQLAlchemy query.

    Orders by (sort_field, id) ascending -- id is the tie-breaker that makes
    the ordering total, which is what keeps the cursor unambiguous.

    Returns (items, next_cursor, has_next). Fetches limit+1 rows to detect a
    following page without a separate COUNT query.
    """
    sort_col = getattr(model, sort_field)
    id_col = model.id

    # deterministic, total ordering
    query = query.order_by(sort_col.asc(), id_col.asc())

    # keyset WHERE, only when a cursor is supplied
    if params.after is not None:
        cursor = decode_cursor(params.after)
        last_sort = cursor["s"]
        last_id = cursor["id"]
        # (sort, id) > (last_sort, last_id) as a row comparison:
        #   sort > last_sort  OR  (sort == last_sort AND id > last_id)
        query = query.filter(
            or_(
                sort_col > last_sort,
                and_(sort_col == last_sort, id_col > last_id),
            )
        )

    # fetch one extra to know whether there's a next page
    rows = query.limit(params.limit + 1).all()

    has_next = len(rows) > params.limit
    items = rows[: params.limit]

    next_cursor = None
    if has_next and items:
        last = items[-1]
        next_cursor = encode_cursor(getattr(last, sort_field), last.id)

    return items, next_cursor, has_next
