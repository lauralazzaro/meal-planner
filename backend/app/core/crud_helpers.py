from app.core.pagination import paginate_query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from collections.abc import Sequence


def get_owned_record(
    model,
    record_id,
    user_id: int,
    db: Session,
    check_deleted: bool = True,
    lookup_field: str = "id",
    options: Sequence = (),
):
    """Generic helper to fetch a record by id (or another unique field,
    e.g. public_id), scoped to the owning user.
    Returns None if not found, not owned, or (optionally) soft-deleted."""
    filters = [getattr(model, lookup_field) == record_id, model.user_id == user_id]

    if check_deleted and hasattr(model, "is_deleted"):
        filters.append(model.is_deleted == False)

    query = db.query(model).filter(and_(*filters))

    if options:
        query = query.options(*options)

    return query.first()


def get_owned_paginated_records(
    model,
    user_id: int,
    db: Session,
    params,
    sort_field,
    check_deleted: bool = True,
    options: Sequence = (),
):
    """Generic helper to fetch records owned by the given user.

    `options` accepts SQLAlchemy loader options (selectinload, joinedload...)
    so each module can eager-load its own relationships and avoid N+1.
    """
    query = db.query(model).filter(model.user_id == user_id)

    if check_deleted and hasattr(model, "is_deleted"):
        query = query.filter(model.is_deleted == False)

    if options:
        query = query.options(*options)

    return paginate_query(query, model, sort_field, params)
