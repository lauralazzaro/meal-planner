import uuid
from pydantic import BaseModel, Field


class ORMSchema(BaseModel):
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "ser_json_by_alias": True,
    }


class PublicIdSchema(ORMSchema):
    id: uuid.UUID = Field(alias="public_id")
