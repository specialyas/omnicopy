from datetime import datetime
from typing import Any
from fastapi import HTTPException
from random import randint
from fastapi import FastAPI
from fastapi import Response


app = FastAPI(root_path="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello World"}

"""
Campaigns
- campaign_id
- name
- due_date
- created_at
"""

data = [
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
    {}
]

@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}


@app.get("/campaigns/{campaign_id}")
async def read_campaigns(campaign_id: int):
    for campaign in data:
        if campaign.get("campaign_id") == campaign_id:
            return {"campaigns": campaign }
    raise HTTPException(status_code=404)

@app.post("/campaigns", status_code=201)
async def create_campaign(body: dict[str, Any]):

    new : Any = {
        "campaign_id": randint(100, 1000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now(),
    }

    data.append(new)
    return {"campaigns": new } 


@app.put("/campaigns/{campaign_id}")
async def update_campaigns(campaign_id: int, body: dict[ str, Any]):

    """update campaigns using the campaign id"""

    for index, campaign in enumerate(data):
        if campaign.get("campaign_id") == campaign_id:

            updated : Any = {
                "campaign_id": campaign_id,
                "name": body.get("name"),
                "due_date": body.get("due_date"), 
                "created_at": campaign.get("created_at")
            }
            data[index] = updated
            return {"campaigns": updated }
    raise HTTPException(status_code=404)


@app.delete("/campaigns/{campaign_id}")
async def delete_campaigns(campaign_id: int):

    for index, campaign in enumerate(data):
        if campaign.get("campaign_id") == campaign_id:
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404)

