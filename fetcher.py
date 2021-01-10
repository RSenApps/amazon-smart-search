import subprocess
import os
from mezmorize import Cache
import pandas as pd
import json
cache = Cache(CACHE_TYPE='filesystem', CACHE_DIR='cache')


def get_products(query, count=50):
    params = ["products", "--keyword=" + query, "-n=" + str(count)]
    products_dict = run_scraper(params)
    return pd.json_normalize(products_dict)

@cache.memoize()
def run_scraper(parameters):
    default_param = ["node", "amazon-product-api/bin/cli.js", "--random-ua", "--filetype=json"]
    output = subprocess.check_output(default_param + parameters, universal_newlines=True)
    filename = output.split("was saved to: ")[1].rstrip() + ".json"
    with open(filename) as f:
        result = json.load(f)
    os.remove(filename)
    return result