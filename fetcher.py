import subprocess
import os
from mezmorize import Cache
import pandas as pd
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
cache = Cache(DEBUG=True, CACHE_TYPE='filesystem', CACHE_DIR='cache', CACHE_THRESHOLD=1024*1024, CACHE_DEFAULT_TIMEOUT=9999)


def get_products(query, count=50):
    params = ["products", "--keyword=" + query, "-n=" + str(count)]
    products_dict = run_scraper(params)
    products_df = pd.json_normalize(products_dict)
    adjust_reviews(products_df)
    products_df['title'] = products_df['title'].str.lstrip("Sponsored Ad - ")
    return products_df


@cache.memoize()
def run_scraper(parameters):
    print("Running scraper: ", parameters)
    default_param = ["node", "amazon-product-api/bin/cli.js", "--random-ua", "--filetype=json"]
    output = subprocess.check_output(default_param + parameters, universal_newlines=True)
    filename = output.split("was saved to: ")[1].rstrip() + ".json"
    with open(filename) as f:
        result = json.load(f)
    os.remove(filename)
    return result

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False


def adjust_reviews(products_df):
    processes = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for asin in products_df["asin"]:
            processes.append(executor.submit(fetch_review_meta, asin))

    review_meta_dict = {x.result()[0] : x.result()[1] for x in as_completed(processes)}
    has_reviews = [k for k,v in review_meta_dict.items() if isfloat(v['rating'])]
    products_df.loc[products_df["asin"].isin(has_reviews), "reviews.rating"] = products_df["asin"].map({k : v["rating"] for k, v in review_meta_dict.items()})
    products_df['reviews.rating'] = products_df['reviews.rating'].astype(float)
    products_df.loc[products_df["asin"].isin(has_reviews), "reviews.total_reviews"] = products_df["asin"].map({k : v["count"] for k, v in review_meta_dict.items()})
    products_df['reviews.total_reviews'] = products_df['reviews.total_reviews'].astype(int)

@cache.memoize()
def fetch_review_meta(asin):
    print("Fetching: ", asin)
    return (asin, requests.get("https://reviewmeta.com/api/amazon/" + asin).json())