from pydantic import BaseModel, ConfigDict, ValidationError, model_validator
from pydantic.functional_validators import field_validator
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from microservice.db.engine import create_tables, get_session
from microservice.db.models import Workflow, Component
from typing import Dict, Union, Optional

app = FastAPI()

allowed_type_values = ["import", "shadow", "crop", "export"]

@app.on_event("startup")
def start_db():
    create_tables()

class ComponentsSchema(BaseModel):
    type: str
    settings: Optional[Dict[str, Union[int, float, str, bool]]] = None

    @field_validator("type")
    def validate_type(cls, v):
        if v not in allowed_type_values:
            raise ValueError(f"Invalid value of type: {v}")
        return v

class WorkflowSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    components: Optional[list[ComponentsSchema]] = None

    @model_validator(mode='after')
    def check_component_type(self) -> 'WorkflowSchema':
        cpnts = self.components
        if cpnts is not None:
            types_list = [cs.type for cs in cpnts]
            settings_list = [cs.settings for cs in cpnts if cs.settings is not None]
            # Check duplicate Types
            duplicate_types = [x for x in types_list if types_list.count(x) > 1]
            if len(duplicate_types) > 0:
                raise ValueError(f"There should be only one occurence of each type: {duplicate_types}")
            # Check Import is first in list
            if "import" in types_list and cpnts[0].type != "import":
                raise ValueError("import should be first in the list of settings")
            # Check Export is last in list
            if "export" in types_list and cpnts[-1].type != "export":
                raise ValueError("export should be last in the list of settings")
            # Check that all or none components have settings
            if len(settings_list) > 0 and len(settings_list) != len(cpnts):
                raise ValueError("All component should either contain the settings fields or none shall contain it")
        return self
        


@app.post("/workflow")
def create_workflow(
        request: WorkflowSchema,
        session: Session = Depends(get_session)

):
    try:
        workflow_db = Workflow(name=request.name)
        if request.components is not None:
            for order, component in enumerate(request.components):
                component_db = Component(order=order, component_type=component.type, component_settings=component.settings, workflow=workflow_db)
                session.add(component_db)
        session.add(workflow_db)
        session.commit()
        session.refresh(workflow_db)
        return workflow_db.id
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid Parameters: : {str(e)}")
