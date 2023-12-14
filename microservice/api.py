from pydantic import BaseModel
from fastapi import FastAPI, Depends
from sqlmodel import Session
from microservice.db.engine import create_tables, get_session
from microservice.db.models import Workflow

app = FastAPI()


@app.on_event("startup")
def start_db():
    create_tables()

# TODO: add list of components with `type` and `settings` fields to the request


class WorkflowSchema(BaseModel):
    name: str


@app.post("/workflow")
def create_workflow(
        request: WorkflowSchema,
        session: Session = Depends(get_session)

):
    # TODO: validate and store components
    workflow_db = Workflow(name=request.name)
    session.add(workflow_db)
    session.commit()
    session.refresh(workflow_db)
    return workflow_db.id
