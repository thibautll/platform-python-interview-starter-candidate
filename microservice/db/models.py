from uuid import uuid4, UUID
from sqlmodel import Field, SQLModel


class Workflow(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str

# TODO: add tables for `Component` and `Settings`
