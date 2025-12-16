from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Annotated, Generic, TypeVar
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import create_engine, SQLModel, Field, Session, select

class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)

class CampaignCreate(SQLModel):
    name: str
    due_date: datetime | None = None

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.now()),
                Campaign(name="Breaking Bad", due_date=datetime.now())
            ])
            session.commit()
    yield


app = FastAPI(root_path="/api/v1", lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


data: Any = [
    {
        "campaign_id": 1,
         "name": "Winter  Solstice",
         "due_date": datetime.today(),
         "created_at": datetime.today(),
    },
    {
        "campaign_id": 2,
        "name": "Solar eclipse",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    },

]
"""
Campaigns
- campaign_id
- name
- due_date
- created_at
"""


T = TypeVar("T")

class Response(BaseModel, Generic[T]):
    data: T


@app.get("/campaigns", response_model=Response[list[Campaign]])
async def read_campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    print("RETURNING:", {"campaigns": data})

    return {"data": data}


@app.get("/campaigns/{id}", response_model=Response[Campaign])
async def read_campaign(id: int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"data": data}


@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)

    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}

@app.put("/campaigns/{id}", response_model=Response[Campaign])
async def update_campaign(campaign_id: int, campaign: CampaignCreate, session: SessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}




@app.delete("/campaign/{campaign_id}", response_model=Response[Campaign])
def delete_campaign(campaign_id: int, session: SessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")

    session.delete(data)
    session.commit()
    return {"data": data}