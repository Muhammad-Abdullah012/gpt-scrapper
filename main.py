import json
from typing import List, Optional, Any, Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from validators import is_valid_url
from scrap import scrape_with_playwright

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

schema_example = {
    "properties": {
        "type_of_property": {"type": "string"}
    },
    "required": ["type_of_property"]
}


class ReqBody(BaseModel):
    open_ai_api_key: str = Field(
        default="", description="Open Ai API Key provided by user in request!")
    urls: List[str] = Field(
        default=[], description="A List of URLs to scrape!")
    schema_to_extract: dict = Field(
        default={
            "properties": {
                "type_of_property": {"type": "string"},
                "price_of_property_listing": {"type": "string"},
                "location_of_property_listed": {"type": "string"},

                "area_of_property_listed": {"type": "string"},
                "purpose_of_listing": {"type": "string"}

            },
            "required": ["type_of_property", "price_of_property_listing", "location_of_property_listed", "area_of_property_listed", "purpose_of_listing"]
        }, description="Schema of properties to extract from URLs")


class PingResponse(BaseModel):
    status: str


class ScrapResponse(BaseModel):
    data: Union[List[dict[str, Any]], None]
    error: Optional[str] = None


@app.get("/", response_model=PingResponse)
def ping():
    return {"status": "Ok"}


@app.get("/ping", response_model=PingResponse)
def ping():
    return {"status": "Ok"}


@app.post("/scrap", response_model=ScrapResponse)
def scrap(urls: str, body: ReqBody, request: Request):
    print("Headers ==> ", request.headers)

    try:
        # if len(body.open_ai_api_key or request.headers.get("open_ai_api_key")) == 0:
        #     raise Exception("open_ai_api_key is required in request body!")
        # if len(body.urls) == 0:
        #     raise Exception("urls is required and must be non-empty array!")
        # if len(body.schema_to_extract.keys()) == 0:
        #     raise Exception(
        #         f"schema_to_extract must be a valid object describing data to extract! e.g {json.dumps(schema_example)}")
        print("Request body => ", body)
        # for url in body.urls:
        #     if not is_valid_url(url):
        #         raise Exception(f"Invalid url found: {url} in urls list!")
        scraped_data = scrape_with_playwright(
            urls=body.urls, schema=body.schema_to_extract, api_key=body.open_ai_api_key or request.headers.get("open_ai_api_key"))
        return {"data": scraped_data, "error": None}
    except Exception as e:
        return JSONResponse(content={"error": f"{e}", "data": None}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/scrap", response_model=ScrapResponse)
def scrap(open_ai_api_key: str = "", urls: List[str] = [], schema_to_extract: dict = {}):
    try:
        if len(open_ai_api_key) == 0:
            raise Exception("open_ai_api_key is required in query parameter!")
        if len(urls) == 0:
            raise Exception("urls is required and must be non-empty array!")
        if len(schema_to_extract.keys()) == 0:
            raise Exception(
                f"schema_to_extract must be a valid object describing data to extract! e.g {json.dumps(schema_example)}")
        scraped_data = scrape_with_playwright(
            urls=urls, schema=schema_to_extract, api_key=open_ai_api_key)
        return {"data": scraped_data, "error": None}
    except Exception as e:
        return JSONResponse(content={"error": f"{e}", "data": None}, status_code=status.HTTP_400_BAD_REQUEST)
