from uuid import uuid4, UUID
from typing import Dict, List, Optional
from sqlmodel import Field, SQLModel, JSON, Relationship, Column


class Workflow(SQLModel, table=True):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str

    components: List["Component"] = Relationship(back_populates="workflow")


class Component(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order: int
    component_type: str
    component_settings: Dict = Field(default={}, sa_column=Column(JSON))
    
    workflow_id: UUID = Field(foreign_key="workflow.id")
    workflow: Workflow = Relationship(back_populates="components")

