from lemlist import Campaigns


def test_list_campaigns(client):
    campaigns = Campaigns(client=client)
    assert isinstance(campaigns.get_campaigns(), list)


def test_get_campaign_by_id(client):
    campaigns = Campaigns(client=client)
    campaign_id = campaigns.get_campaigns()[0]["_id"]
    assert isinstance(campaigns.get_campaign(campaign_id=campaign_id), dict)


def test_get_campaign_by_name(client):
    campaigns = Campaigns(client=client)
    campaign_name = campaigns.get_campaigns()[0]["name"]
    assert isinstance(campaigns.get_campaign(campaign_name=campaign_name), dict)