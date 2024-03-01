from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlmodel import Session
from microservice.db.engine import create_tables, get_session
from microservice.db.models import Workflow, Component
from typing import Dict, Union, Optional

app = FastAPI()


@app.on_event("startup")
def start_db():
    create_tables()

class ComponentsSchema(BaseModel):
    type: str
    settings: Optional[Dict[str, Union[int, float, str, bool]]] = None

class WorkflowSchema(BaseModel):
    name: str
    components: Optional[list[ComponentsSchema]] = None


@app.post("/workflow")
def create_workflow(
        request: WorkflowSchema,
        session: Session = Depends(get_session)

):
    workflow_db = Workflow(name=request.name)
    if request.components is not None:
        for order, component in enumerate(request.components):
            component_db = Component(order=order, component_type=component.type, component_settings=component.settings, workflow=workflow_db)
            session.add(component_db)
    session.add(workflow_db)
    session.commit()
    session.refresh(workflow_db)
    return workflow_db.id
