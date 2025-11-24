from datetime import datetime
from http.client import HTTPException

from fastapi import FastAPI


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
         "name": "Winter Soltice",
         "due_date": datetime.today(),
         "created_at": datetime.today(),
    },
    {
        "campaign_id": 2,
        "name": "Solar eclipse",
        "due_date": datetime.today(),
        "created_at": datetime.today(),
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
