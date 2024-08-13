import base64
import json
import csv
from typing import Optional
from hashlib import md5

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

        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text


class Campaigns:

    def __init__(self, client: Client, version_id: int = 2):
        self.client = client
        self.version_id = version_id

    def get_campaigns(self, offset:int = 0, limit: int = 10, page: int = 1):
        return self.client.send_request("GET", "/campaigns", {
            "version": f"v{self.version_id}",
            "offset": offset,
            "limit": limit,
            "page": page,
        })

    def get_campaign(self, campaign_id=None, campaign_name=None):

        if campaign_id:
            return self.client.send_request("GET", f"/campaigns/{campaign_id}")

        elif campaign_name:
            offset = 0
            page = 1
            while True:
                get_campaigns_resp = self.get_campaigns(offset=offset, page=page)
                for campaign in get_campaigns_resp['campaigns']:
                    offset += 1
                    if campaign["name"] == campaign_name:
                        return campaign
                page+=1
                pagination = get_campaigns_resp['campaigns']
                if not 'nextPage' in pagination:
                    break

        else:
            raise ValueError("Either campaign_id or campaign_name must be provided.")

    def get_leads(self, campaign_id):
        """Get leads for a campaign.

        GET https://api.lemlist.com/api/campaigns/:campaignId/export/leads?state=all
        """
        leads = self.client.send_request("GET", f"/campaigns/{campaign_id}/export/leads?state=all")

        lines = leads.strip().split('\r\n')

        # Create a CSV reader to process the lines, assuming the first line contains headers
        reader = csv.reader(lines)

        # Extract headers (column names)
        headers = next(reader)

        # Initialize a list to hold dictionaries created from rows
        json_list = []

        # Iterate over the remaining lines in the reader to construct dictionaries
        # Each dictionary maps headers (column names) to the corresponding row values
        for row in reader:
            row_dict = {headers[i]: row[i] for i in range(len(headers))}

            vals_for_hash = [v for k, v in row_dict.items() if k not in ('hash', 'emailStatus')]
            # create a hash field for each row, takes all values and creates a md5 hash
            row_dict['hash'] = md5(json.dumps(vals_for_hash).encode()).hexdigest()

            _ = row_dict.pop('emailStatus')

            json_list.append(row_dict)

        return json_list

    def update_lead(self, campaign_id: str, email: str, lead: dict):
        """
        This endpoint updates a lead in a specific campaign.

        If the lead doesn't exist a 404 error will be returned.
        HTTP Request

        PATCH https://api.lemlist.com/api/campaigns/:campaignId/leads/:email
        URL Parameters
        Parameter 	Description
        campaignId 	The ID of the campaign to add the lead.
        email 	email address of the lead
        Body Parameters

        Body is mandatory. It must be a JSON object with any information you want to update on the lead.

        If no body is specified a 400 error will be returned.

            curl -X PATCH https://api.lemlist.com/api/campaigns/cam_aa7uvyxECcni5KXBM/leads/richard@piedpiper.com \
          -H "Content-Type: application/json" \
          --data '{"companyName":"Pied Piper"}' \
          --user ":YourApiKey"


        The above command returns JSON structured like this:

        {
          "campaignId": "cam_aa7uvyxECcni5KXBM",
          "campaignName": "Campaign1",
          "leadUrl":"https://api.lemlist.com/api/leads/richard%40piedpiper.com",
          "_id":"lea_aaNfSAHJoa4gj86Px",
          "email":"richard@piedpiper.com",
          "firstName":"Richard",
          "lastName":"Hendricks",
          "companyName": "Pied Piper"
        }
        """

        # do the patch and check if return is 200 otherwise raise error
        response = self.client.send_request(
            method="PATCH",
            endpoint=f"/campaigns/{campaign_id}/leads/{email}",
            payload=lead
        )

        return response


    def delete_lead(self, campaign_id: str, email: str):
        """
        This endpoint delete a lead from a specific campaign.
        All information, including statistics, will be deleted.
        HTTP Request

        DELETE https://api.lemlist.com/api/campaigns/:campaignId/leads/:email?action=remove
        URL Parameters
        Parameter 	Description
        campaignId 	The ID of the campaign to add the lead.
        email 	email address of the lead
        Query Parameters
        Parameter 	Value 	Description
        action 	remove 	Force the deletion of the lead

        > curl -X DELETE https://api.lemlist.com/api/campaigns/cam_aa7uvyxECcni5KXBM/leads/richard@piedpiper.com?action=remove --user ":YourApiKey"
        > {
              "_id": "lea_aaNfSAHJoa4gj86Px",
              "email": "richard@piedpiper.com"
            }
        """

        return self.client.send_request(
            method="DELETE",
            endpoint=f"/campaigns/{campaign_id}/leads/{email}",
            params={"action": "remove"}
        )

    def delete_campaign(self, campaign_id):
        return self.client.send_request("DELETE", f"/campaigns/{campaign_id}")

    def add_a_lead(self, campaign_id, lead: dict, deduplicate=True, find_email=False, linkedin_enrichment=False,
                   verify_email=False):

        email = lead.get('email')
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
#     api_key = os.getenv("LEMLIST_API_KEY")
#     client = Client(api_key=api_key)
#     lemlist_campaigns = Campaigns(client=client)
#     # c_list = lemlist_campaigns.get_campaigns()
#     # # print(c_list)
#
#     campaign = lemlist_campaigns.get_campaign(campaign_name="Copilot Outbound Test")
#     print(campaign)
#
#     leads = lemlist_campaigns.get_leads(campaign_id=campaign['_id'])
#     print
#     #
#     # l = {
#     #     "email": "jdoe@acmeinc.com",
#     #     "firstName": "John",
#     #     "lastName": "Doe",
#     #     "companyName": "Acme Inc.",
#     #     "icebreaker": "Hey how do you do?",
#     #     "phone": None,
#     #     "picture": None,
#     #     "linkedinUrl": "https://www.linkedin.com/jdoe",
#     #     "companyDomain": "acmeinc.com",
#     #     "g2_main_sector": "Cartoons",
#     #     "g2_sub_sector": "Looney Tunes",
#     #     "sender_name": "Alba"
#     # }
#     #
#     # lead = Lead(**l)
#     #
#     # response = lemlist_campaigns.add_a_lead(campaign_id=campaign["_id"], lead=lead.dict())
#
#     print(response)

