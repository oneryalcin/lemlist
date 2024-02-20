
import base64
import json
from typing import Optional

import requests
from pydantic import BaseModel


class Lead(BaseModel):
    email: str
    firstName: str
    lastName: str
    companyName: Optional[str]
    icebreaker: Optional[str]
    phone: Optional[str]
    picture: Optional[str]
    linkedinUrl: Optional[str]
    companyDomain: Optional[str]
    g2_main_sector: Optional[str]
    g2_sub_sector: Optional[str]
    sender_name: Optional[str]


class Client:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.lemlist.com/api"

    @property
    def headers(self):
        auth_val = base64.b64encode(f":{self.api_key}".encode()).decode()

        return {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + auth_val
        }

    def send_request(self, method, endpoint, params=None, payload=None):
        url = self.base_url + endpoint

        payload = json.dumps(payload) if payload else None
        response = requests.request(method, url, headers=self.headers, params=params, data=payload)
        response.raise_for_status()

        return response.json()


class Campaigns:

    def __init__(self, client: Client):
        self.client = client

    def get_campaigns(self):
        return self.client.send_request("GET", "/campaigns")

    def get_campaign(self, campaign_id=None, campaign_name=None):

        if campaign_id:
            return self.client.send_request("GET", f"/campaigns/{campaign_id}")

        elif campaign_name:
            campaigns = self.get_campaigns()
            for campaign in campaigns:
                if campaign["name"] == campaign_name:
                    return campaign

        else:
            raise ValueError("Either campaign_id or campaign_name must be provided.")

    def add_a_lead(self, campaign_id, lead: dict, deduplicate=True, find_email=False, linkedin_enrichment=False, verify_email=False):

        email = lead.pop("email")
        if not email:
            raise ValueError("Email is required for a lead")

        params = {
            "deduplicate": deduplicate,
            "findEmail": find_email,
            "linkedinEnrichment": linkedin_enrichment,
            "verifyEmail": verify_email
        }

        return self.client.send_request(
            method="POST",
            endpoint=f"/campaigns/{campaign_id}/leads",
            params=params,
            payload=lead
        )


# if __name__ == '__main__':
#     client = Client(api_key="API_KEY_HERE")
#     lemlist_campaigns = Campaigns(client=client)
#     # c_list = lemlist_campaigns.get_campaigns()
#     # # print(c_list)
#
#     campaign = lemlist_campaigns.get_campaign(campaign_name="Copilot Outbound Reach")
#     print(campaign)
#
#     l = {
#         "email": "jdoe@acmeinc.com",
#         "firstName": "John",
#         "lastName": "Doe",
#         "companyName": "Acme Inc.",
#         "icebreaker": "Hey how do you do?",
#         "phone": None,
#         "picture": None,
#         "linkedinUrl": "https://www.linkedin.com/jdoe",
#         "companyDomain": "acmeinc.com",
#         "g2_main_sector": "Cartoons",
#         "g2_sub_sector": "Looney Tunes",
#         "sender_name": "Alba"
#     }
#
#     lead = Lead(**l)
#
#     response = lemlist_campaigns.add_a_lead(campaign_id=campaign["_id"], lead=lead.dict())
#
#     print(response)

