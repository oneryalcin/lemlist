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
    campaign_id = get_campaigns_resp['campaigns'][0]["_id"]
    assert isinstance(campaigns.get_campaign(campaign_id=campaign_id), dict)


def test_get_campaign_by_name(client):
    campaigns = Campaigns(client=client)
    get_campaigns_resp = campaigns.get_campaigns(offset=0, limit=1)
    campaign_name = get_campaigns_resp['campaigns'][0]["name"]
    assert isinstance(campaigns.get_campaign(campaign_name=campaign_name), dict)