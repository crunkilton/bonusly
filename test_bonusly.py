import requests
from bonusly.bonusly import BonuslyClient, get_all_bonuses
import pandas as pd
from secrets import access_token

# list of endpoints to look at
# to_test = [
#     "users",
#     "achievements",
#     "trends",
#     "redemptions",
#     "rewards",
#     "leaderboards",
#     "bonuses",
#     "company",
#     "webhooks",
#     "api_keys",
# ]


def good_resp(resp):
    return all(x in resp.json().keys() for x in ["success", "result"])


class TestEndpoints:
    def setup_method(self):
        self.b = BonuslyClient(access_token=access_token)

    def test_setup(self):
        assert isinstance(self.b, BonuslyClient)
        assert isinstance(self.b.session, requests.sessions.Session)

    def test_bad_auth(self):
        b = BonuslyClient(access_token="wrong_access_token")
        resp = b.users().get("raw")
        assert resp.status_code == 401

    def test_bad_endpoint(self):
        resp = self.b.users().users().achievements().get("raw")
        assert resp.status_code == 404

    def test_users(self):
        resp = self.b.users().get("raw")
        assert good_resp(resp)

    def test_bonuses(self):
        resp = self.b.bonuses().get("raw")
        assert good_resp(resp)

    def test_achievements(self):
        resp = self.b.achievements().get("raw")
        assert good_resp(resp)

    # etc. later add more, include compound ones like users().bonuses() we expect to work


# make fixtures for this later, also make them for post/put/delete. use responses package?
class TestGet:
    def setup_method(self):
        self.b = BonuslyClient(access_token=access_token)

    def test_df(self):
        df = self.b.users().get("df")
        assert isinstance(df, pd.DataFrame)
        assert df.empty is False

    def test_json(self):
        js = self.b.users().get("json")
        assert isinstance(js, dict)
        assert js

    def test_get_all_bonuses(self):
        df = get_all_bonuses(self.b, skip_limit=200)
        assert isinstance(df, pd.DataFrame)
        assert df.shape[0] >= 200
