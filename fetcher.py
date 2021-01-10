import subprocess
import os
from mezmorize import Cache
import pandas as pd
import json
import requests
cache = Cache(CACHE_TYPE='filesystem', CACHE_DIR='cache')


def get_products(query, count=50):
    params = ["products", "--keyword=" + query, "-n=" + str(count)]
    products_dict = run_scraper(params)
    products_df = pd.json_normalize(products_dict)
    adjust_reviews(products_df)
    products_df['title'] = products_df['title'].str.lstrip("Sponsored Ad - ")
    return products_df


@cache.memoize()
def run_scraper(parameters):
    default_param = ["node", "amazon-product-api/bin/cli.js", "--random-ua", "--filetype=json"]
    output = subprocess.check_output(default_param + parameters, universal_newlines=True)
    filename = output.split("was saved to: ")[1].rstrip() + ".json"
    with open(filename) as f:
        result = json.load(f)
    os.remove(filename)
    return result

def adjust_reviews(products_df):
    review_meta_dict = {asin : fetch_review_meta(asin) for asin in products_df["asin"]}
    has_reviews = [k for k,v in review_meta_dict.items() if v['rating'] != '']
    products_df.loc[products_df["asin"].isin(has_reviews), "reviews.rating"] = products_df["asin"].map({k : v["rating"] for k, v in review_meta_dict.items()})
    products_df['reviews.rating'] = products_df['reviews.rating'].astype(float)
    products_df.loc[products_df["asin"].isin(has_reviews), "reviews.total_reviews"] = products_df["asin"].map({k : v["count"] for k, v in review_meta_dict.items()})
    products_df['reviews.total_reviews'] = products_df['reviews.total_reviews'].astype(int)

@cache.memoize()
def fetch_review_meta(asin):
    return requests.get("https://reviewmeta.com/api/amazon/" + asin).json()