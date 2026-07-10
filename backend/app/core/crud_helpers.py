from sqlalchemy.orm import Session
from sqlalchemy import and_


def get_owned_record(
    model, record_id: int, user_id: int, db: Session, check_deleted: bool = True
):
    """Generic helper to fetch a record by id, scoped to the owning user.
    Returns None if not found, not owned, or (optionally) soft-deleted."""
    filters = [model.id == record_id, model.user_id == user_id]
    if check_deleted and hasattr(model, "is_deleted"):
        filters.append(model.is_deleted == False)

    return db.query(model).filter(and_(*filters)).first()


def get_all_owned_records(model, user_id: int, db: Session, check_deleted: bool = True):
    """Generic helper to fetch all records owned by the given user."""
    query = db.query(model).filter(model.user_id == user_id)
    if check_deleted and hasattr(model, "is_deleted"):
        query = query.filter(model.is_deleted == False)
    return query.all()
