import nltk
import os
import json
import logging
from pocket import Pocket
from typing import List, Dict
from collections import Counter
from nltk.corpus import stopwords
from constants import CACHE_FILE, CONSUMER_KEY, ACCESS_TOKEN, DEFAULT_READING_SPEED


api = Pocket(consumer_key=CONSUMER_KEY, access_token=ACCESS_TOKEN)
nltk.download('stopwords')
invalid_words = stopwords.words('english')


def fetch_data(offset: int = 0, limit: int = None, overwrite_cache: bool = False) -> List[Dict]:
    ans = []
    count = limit if (limit is not None) else 100
    while True:
        response = api.retrieve(offset=offset, count=count)
        items = response.get('list', [])
        ans.extend(item for k, item in items.items())
        if (limit is not None) or (len(items) == 0):
            break
    logging.info(f'Fetched {len(ans)} records')
    if overwrite_cache:
        logging.info(f'Writing data to cache file {CACHE_FILE}')
        with open(CACHE_FILE, 'w') as fo:
            json.dump(ans, fo)
    return ans


def load_cache() -> List[Dict]:
    if not os.path.isfile(CACHE_FILE):
        return []
    with open(CACHE_FILE, 'r') as fi:
        return json.load(fi)


def is_valid_word(w):
    if len(w) == 0:
        return False
    if w in invalid_words:
        return False
    return True


def count_words_in_title(data: List[Dict]) -> Dict[str, int]:
    words = []
    for record in data:
        title = record['given_title']
        words.extend(x.strip().lower() for x in title.split(' ') if is_valid_word(x.strip().lower()))
    return Counter(words)


def get_word_counts(data: List[Dict]) -> List[int]:
    return [int(record.get('word_count', -99999)) for record in data]


def get_reading_time(data: List[Dict], reading_speed: int = DEFAULT_READING_SPEED) -> List[int]:
    # because some records in data don't have the 'time_to_read' field
    word_counts = get_word_counts(data)
    return [wc / DEFAULT_READING_SPEED for wc in word_counts if wc > 0]
