import math
global_max_price = None
global_min_review_count = None
global_min_rating = None
global_title_keywords = None
def apply_full_filter(products_df):
    products_f_df = products_df[(products_df["price.current_price"] <= global_max_price) & 
                                (products_df["reviews.rating"] >= global_min_rating) & 
                                (products_df["reviews.total_reviews"] >= global_min_review_count) &
                                (products_df["title"].str
                                    .contains('|'.join(global_title_keywords), case=False))]
    return products_f_df

def update_filter(max_price=None, min_review_count=None, min_rating=None, title_keywords=None):
    global global_max_price
    global global_min_review_count
    global global_min_rating
    global global_title_keywords
    if max_price: global_max_price = max_price
    if min_review_count: global_min_review_count = min_review_count
    if min_rating: global_min_rating = min_rating
    if title_keywords: global_title_keywords = [x.lower() for x in title_keywords]

def init_filter(products_df):
    global global_max_price
    global global_min_review_count
    global global_min_rating
    global global_title_keywords
    global_max_price = math.ceil(products_df["price.current_price"].max())
    global_min_review_count = products_df["reviews.total_reviews"].max()
    global_min_rating = products_df["reviews.rating"].min()
    global_title_keywords = []