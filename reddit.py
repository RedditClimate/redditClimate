import requests, json
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import time
import random

plt.clf()
plt.cla()

sns.set(style="ticks", color_codes=True)

BIG_LIST = ["350",
"activism",
"agriculture",
"agronomy",
"airquality",
"animalbehavior",
"animalrights",
"animals",
"anticonsumption",
"aquaponics",
"aquaticecology",
"askscience",
"australia",
"backyardchickens",
"badeconomics",
"basins",
"beekeeping",
"bicycling",
"biochemistry",
"biology",
"biomass",
"botany",
"canada",
"canning",
"changemyview",
"cleanenergy",
"climate",
"climate_science",
"climateactionplan",
"climatechange",
"climatenews",
"climateoffensive",
"climateskeptics",
"collapse",
"collegeconservatives",
"collegerepublicans",
"composting",
"conservation",
"conservative",
"conservativeladies",
"conservativelounge",
"conservativeminds",
"conservatives",
"conservatives_r_us",
"conservativesonly",
"conspiracy",
"cringeanarchy",
"cycling",
"darksky",
"democrats",
"detrashed",
"directaction",
# "discussrightwing", forbidden
"divestment",
"diy",
"domes",
"drought",
"earthporn",
"earthquakes",
"earthscience",
"earthstrike",
"ecoevents",
"ecology",
"economics",
"edibleplants",
"efficiency",
"endangeredspecies",
"energy",
"energyefficiency",
"energystorage",
"enviroaction",
"environment",
"environmental_policy",
"environmental_science",
"envirotech",
"ethical_living",
"everythingscience",
"extinctionrebellion",
"familyplanning",
"financialindependence",
"fiscalconservative",
"food2",
"foodsovereignty",
"foraging",
"forconservativesonly",
"foresthealth",
"forestry",
"fossilid",
"freeconservative",
"fridaysforfuture",
"frugal",
"futurology",
"gardening",
"geography",
"geology",
"geospatial",
"gis",
"globalclimatechange",
"globalwarming",
"goats",
"gop",
"grandoldparty",
"green",
"greenhouses",
"greenpeace",
"groundwater",
"guerrillagardening",
"hardenergy",
"highspeedrail",
"homestead",
"homesteading",
"hydrology",
"infocon",
"infrastructure",
"infrastructurist",
"invasivespecies",
"justicerepublicans",
"kotakuinaction",
"liberal",
"libertarian",
"libertymovement",
"lifeaquatic",
"livestock",
"livingofftheland",
"marinelife",
"mensrights",
"microbiology",
"mycology",
"nature",
"neoconservatism",
"neoconservative",
"news",
"noplastic",
"nuclearpower",
"oceanacidification",
"oceans",
"offgridliving",
"oilspill",
"omniconservative",
"opensourceecology",
"organicfarming",
"organicgardening",
"ornithology",
"overpopulation",
"paleoconservative",
"patriotspub",
"peakoil",
"permaculture",
"philosophyofscience",
"politicaldiscussion",
"politicalright",
"pollution",
"potuswatch",
"poultry",
"progressive",
"publiclands",
"rainforest",
"raisedright",
"realrepublicans",
"recycling",
"redditforest",
"renewable",
"renewableenergy",
"renewabletech",
"republican",
"republicans",
"republicansforamerica",
"resilientcommunities",
"restoration_ecology",
"rooseveltrepublicans",
"science",
"sciencenetwork",
"seedsaving",
"seedstock",
"selfsufficiency",
"skeptic",
"socialconservative",
"socialism",
"softscience",
"soil",
"solar",
"species",
"squarefootgardening",
"stormcoming",
"strawbale",
"suburbanfarming",
"sunrisemovement",
"sustainability",
"tea_party",
"teaparty",
"teaparypatriot",
"terraserenus",
"thehydrogeneconomy",
"thenewright",
"thoriumreactor",
"tinyhouses",
"transportation",
"tropicalweather",
"tumblrinaction",
"uncensorednews",
"unpopularopinion",
"upcycling",
"urbanfarming",
"urbanplanning",
"veg",
"vermiculture",
"waste",
"water",
"weather",
"whatsthisbug",
"wildlife",
"wind",
"worldnews",
"zerowastebaby",
"zoology"]

assert len(BIG_LIST) == len(set(BIG_LIST))

def query(category, params):
    
    params_string = "&".join(f"{param}={val}" for param,val in params.items())
    url = f"https://api.pushshift.io/reddit/search/{category}/?{params_string}"
    print(url)
    r = requests.get(url = url)
    data = r.json()
    return data["data"]

def query_n(category, params, n = 1000):
    params.update({"sort_type": "created_utc", "sort":"desc", "size":n})

    results = []
    while len(results) < n:
        query_res = query(category, {**params, "before": results[-1]["created_utc"] if results else int(time.time()) })
        if not query_res:
            return results
        results.extend(query_res)
        time.sleep(0.5)
    return results

def query_largest_reddits(subreddits, k = None):
    member_counts = {}
    for subreddit in subreddits:
        url = f"https://api.reddit.com/r/{subreddit}/about"
        print(url)
        time.sleep(0.5)
        r = requests.get(url = url, headers = {'User-agent': 'your bot 0.1'})
        data = r.json()
        if "data" in data and "subscribers" in data["data"]:
            member_counts[subreddit] = data["data"]["subscribers"]
        else:
            print(f"Error: Cannot handle returned data: {data}")
            print(f"Failed on subreddit: {subreddit}")

    k_largest = sorted(member_counts.items(), key = lambda x: -x[1])[:k]
    k_largest_df = pd.DataFrame.from_records([{"subreddit": x[0], "members": x[1]} for x in k_largest])
    pd.to_pickle(k_largest_df, "k_largest.pickle")
    return k_largest

#query_largest_reddits(BIG_LIST)

def get_largest_reddits(k=None):
    k_largest_df = pd.read_pickle("k_largest.pickle")
    return list((k_largest_df.head(k) if k is not None else k_largest_df)["subreddit"])


# for subreddit in general:
#     author_count_plot("submission", subreddit)

def query_climate_skeptics():
    submissions = query_n("submission", {"subreddit": "climateskeptics"}, n = float("inf"))
    with open('climateskeptics_submissions.json', 'w') as f:
        json.dump(submissions, f)
    comments = query_n("comment", {"subreddit": "climateskeptics"}, n = float("inf"))
    with open('climateskeptics_comments.json', 'w') as f:
        json.dump(comments, f)
    return submissions, comments

def get_climate_skeptics():
    with open('climateskeptics_submissions.json', 'r') as f:
        submissions = json.load(f)    
    with open('climateskeptics_comments.json', 'r') as f:
        comments = json.load(f)
    return submissions, comments