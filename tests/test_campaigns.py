from lemlist import Campaigns


def test_list_campaigns(client):
    campaigns = Campaigns(client=client)
    get_campaigns_resp = campaigns.get_campaigns(offset=0, limit=10)
    assert isinstance(get_campaigns_resp, dict)
    assert "pagination" in get_campaigns_resp
    assert "campaigns" in get_campaigns_resp


def test_get_campaign_by_id(client):
    campaigns = Campaigns(client=client)
    get_campaigns_resp = campaigns.get_campaigns(offset=0, limit=1)
    campaign_id = get_campaigns_resp["campaigns"][0]["_id"]
    assert isinstance(campaigns.get_campaign(campaign_id=campaign_id), dict)


def test_get_campaign_by_name(client):
    campaigns = Campaigns(client=client)
    get_campaigns_resp = campaigns.get_campaigns(offset=0, limit=1)
    campaign_name = get_campaigns_resp["campaigns"][0]["name"]
    assert isinstance(campaigns.get_campaign(campaign_name=campaign_name), dict)


def test_manage_lead_variables(client):
    campaigns = Campaigns(client=client)
    get_campaigns_resp = campaigns.get_campaigns(offset=0, limit=1)
    campaign_id = get_campaigns_resp["campaigns"][0]["_id"]

    leads = campaigns.get_leads(campaign_id=campaign_id)
    assert len(leads) > 0
    assert isinstance(leads[0], dict)

    variables = {
        "key": "value",
    }

    add_resp = campaigns.add_lead_variables(
        lead_id=leads[0]["_id"],
        variables=variables,
    )
    assert add_resp["ok"] is True

    update_resp = campaigns.update_lead_variables(
        lead_id=leads[0]["_id"],
        variables=variables,
    )
    assert update_resp["ok"] is True

    delete_resp = campaigns.delete_lead_variables(
        lead_id=leads[0]["_id"],
        variables=variables,
    )
    assert delete_resp["ok"] is True
