# bonusly
A (partially finished) python wrapper for the Bonusly API

API docs here: https://bonusly.docs.apiary.io/#


#### Basic usage looks like:
```
b = BonuslyClient(access_token="token_here")

# you build the endpoint you want like so
b.users('user_id_here').bonuses() -> 'https://bonus.ly/api/v1/users/user_id_here/bonuses/'

# can check url with
b.users('user_id_here').bonuses().url

```

#### GET examples
```
# get users as dataframe (default)
df = b.users().get("df")

# get users as json (dictionary)
js = b.users().get("json")

# get users as raw requests response object
resp = b.users().get("raw")

# if you want to include params, put them in the appropriate endpoint
top_5_only = b.bonuses(limit=5, start_time='2020-01-01T00:00:00Z').get('df')
```

#### POST/PUT/DELETE examples
```
# create a new bonus: 
post = b.bonuses().post(reason="+10 @speck telling me about the bonus API #teamwork #bonusly #apis")

# edit a bonus
put = b.bonuses('605d1d984db78300a7befb7e').put(reason="+5 @speck not quite as impressive as I thought #teamwork #bonusly #apis #data-matters")
# (note: this changes the bonus but will not trigger slack notifications)

# add on to a bonus:
addon = b.bonuses().post(reason='+2 good work', parent_bonus_id='605babeeee6b5a009b4ab12c')

# delete a bonus
delete_me = b.bonuses('605d1d984db78300a7befb7e').delete()
```

#### Get all bonuses
To get every bonus ever, use the `get_all_bonuses` function:

```df = get_all_bonuses(b, include_children=True, skip_limit=float("inf"))```

- note that if someone gives a bonus to two people (i.e. '+10 @cody @sarah') the `receiver_*` columns are only for one of the receivers, which bonusly seems to pick randomly. If you look in the `receivers` column you should get a list of dicts of all recipients. I should fix this later.

#### Further afield: making a network viz of bonuses using the igraph package:
```import igraph as ig

df = get_all_bonuses(b)

small = df[["giver_full_name", "receiver_full_name", "amount", "created_at"]]

el = (
    small.groupby(["giver_full_name", "receiver_full_name"])["amount"]
    .agg(["sum", "count"])
    .sort_values(["count"], ascending=False)
)

g = ig.Graph.TupleList(
    el.reset_index().itertuples(index=False), directed=True, edge_attrs=["sum", "count"]
)

g.vs["label"] = g.vs["name"]
layout = g.layout("kk")

ig.plot(g, "test_plot.png", layout=layout, vertex_size=g.degree(mode="in"))
```
