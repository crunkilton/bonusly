import requests
import pandas as pd
from pprint import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

# to do:
# 1) tidy up and get on github
# 2) get_all_bonuses - parse all receivers not just the one bonusly specifies
# 3) make a package
# 4) better tests


class BonuslyClient:
    def __init__(self, access_token, total_retries=10, retry_backoff_factor=10):
        self.access_token = f"bearer {access_token}"
        self.url = "https://bonus.ly/api/v1/"
        self.total_retries = total_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.session = self.create_session()
        self.params = None

    def create_session(self):
        s = requests.Session()

        s.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": self.access_token,
            }
        )

        retries = Retry(
            total=self.total_retries,
            backoff_factor=self.retry_backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=frozenset(
                ["GET"]
            ),  # allowed_methods will replace this at some point
        )
        s.mount("https://bonus.ly/api/v1/", HTTPAdapter(max_retries=retries))

        return s

    def reset_url(self):
        self.url = "https://bonus.ly/api/v1/"

    def get(self, format="df"):
        r = self.session.get(self.url, params=self.params)
        self.reset_url()
        # if not r.ok:
        #     raise Exception(f"request failed: {r.status_code}, {r.message}")
        # returning based on format:
        if format.lower() == "df":
            ans = pd.json_normalize(
                r.json()["result"], sep="_"
            )  # pd.DataFrame.from_dict(self.json["result"])
        elif format.lower() == "json":
            ans = r.json()
        elif format.lower() == "json_pretty":
            pprint(r.json())
            ans = self
        else:
            ans = r

        return ans

    def post(self, **data):
        """LESS TESTED BE WARY"""
        p = self.session.post(self.url, data=json.dumps(data))
        self.reset_url()
        # if p.ok:
        #     return p.json()
        # else:
        #     raise Exception(f"request failed: {r.status_code}, {r.message}")
        return p
        # MAYBE just return p here - you'll see if it works and can inspect it more later if you want

    def put(self, **data):
        """LESS TESTED BE WARY"""
        p = self.session.put(self.url, data=json.dumps(data))
        self.reset_url()
        # if p.ok:
        #     return p.json()
        # else:
        #     raise Exception(f"request failed: {r.status_code}, {r.message}")
        return p

    def delete(self):
        """LESS TESTED BE WARY"""
        p = self.session.delete(self.url)
        self.reset_url()
        # if p.ok:
        #     return p.json()
        # else:
        #     raise Exception(f"request failed: {r.status_code}, {r.message}")
        return p

    ## ENDPOINT FUNCTIONS START HERE
    def users(self, id=None, **params):
        """
        id=bonusly id or "me"

        params:
        limit: Number of users to retrieve (min: 1, max: 100) Default: 20.
        skip: Number of users to skip (for pagination, min: 0) Default: 0.
        email: Example: blumbergh%40initech.com
        custom_property_name: You can set any custom property name and value pair here (for example department=marketing)
        sort: created_at, last_active_at, display_name, first_name, last_name, email, country, time_zone. Default order is 'Ascending', prefix an option with '-' to specify 'Descending'
        include_archived: Include archived/deactivated users Default: false.
        show_financial_data: Whether or not to include financial data (giving balance, etc.) (admin only)
        user_mode: comma separated list of user_modes (valid user modes are normal, observer, receiver, benefactor, bot)
        """
        self.url += "users/" if id is None else "users/" + id + "/"
        self.params = params
        return self

    def autocomplete(self, **params):
        """ only for users, params is "search: <string>"""
        self.url += "autocomplete"
        self.params = params
        return self

    def achievements(self):
        self.url += "achievements/"
        return self

    def trends(self):
        self.url += "analytics/trends/"
        return self

    def redemptions(self, id=None, **params):
        self.url += "redemptions/" if id is None else "redemptions/" + id + "/"
        self.params = params

        return self

    def rewards(self, id, **params):
        self.url += (
            "rewards/" if id is None else "reward/" + id + "/"
        )  # I know this is technically "reward" vs "rewards" - but I think it makes more sense to put this here
        self.params = params

    def leaderboards(self, **params):
        """
        params: {
            "direction": "recieved" or "given"
            "hashtag": string
            "scope": manager ID or custom dict'
            "start_date": e.g. "19 Mar 2019"
            "end_date": e.g. "20 Feb 2021"
        }
        """
        # returns a list of dicts. Doesn't play nice with df
        self.url += "analytics/leaderboards/"
        self.params = params
        return self

    def bonuses(self, id=None, **params):
        self.url += "bonuses/" if id is None else "bonuses/" + id + "/"
        self.params = params
        return self

    def company(self):
        self.url += "companies/show/"
        return self

    def webhooks(self, id=None):
        self.url += "webhooks/" if id is None else "webhooks/" + id + "/"
        return self

    def api_keys(self, **params):
        self.url += "api_keys"
        self.params = params
        return self


def get_all_bonuses(bonusly_client, include_children=True, skip_limit=float("inf")):
    """collects all bonuses given in 100-bonus segments, optionally appends child
    bonuses to the bottom of the df"""
    biglist = []
    skip = 0
    while skip < skip_limit:
        df = bonusly_client.bonuses(
            skip=skip, limit=100, include_children=include_children
        ).get("df")
        if df.empty is False:
            # bigdf = bigdf.append(df, ignore_index=True)
            biglist.append(df)
            skip += 100
            print(f"retrieved first {skip} bonuses")
        else:
            break
    bigdf = pd.concat(biglist, ignore_index=True)

    # this below bit appends child bonuses instead of leaving them as json in column
    if not include_children:
        return bigdf

    # limit to only bonuses with child gifts:
    newlst = [elem for elem in bigdf["child_bonuses"].tolist() if elem]
    # pd.json_normalize for everything in newlst
    n2 = [pd.json_normalize(elem, sep="_") for elem in newlst]
    # bringing it all together
    child_df = pd.concat(n2, ignore_index=True)
    # appending children to prior df
    new = bigdf.append(child_df)
    # dropping child_bonuses column (parent_bonus_id indicates if a child)
    new = new.drop("child_bonuses", axis=1)
    return new
