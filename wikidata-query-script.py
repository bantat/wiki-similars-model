import os
import time
import ujson
import traceback
import urllib.request
import urllib.parse

from random import shuffle
from pynfs.aurora_client import AuroraClient
from vevoml.dbtools.client_connection import query_aurora_with_conn_check

AURORA_HOST = os.environ.get('AURORA_HOST')
AURORA_USER = os.environ.get('AURORA_USER')
AURORA_PASSWORD = os.environ.get('AURORA_PASSWORD')

aurora_client = AuroraClient(AURORA_HOST,
                             AURORA_USER,
                             AURORA_PASSWORD)

artists_sql_query = "SELECT artist_id, name, week_views FROM artists " + \
                    "WHERE enabled = true"

with open('label_query.sparql', 'r') as f:
    LABEL_QUERY = f.readline().strip()
with open('alias_query.sparql', 'r') as f:
    ALIAS_QUERY = f.readline().strip()
with open('title_query.sparql', 'r') as f:
    TITLE_QUERY = f.readline().strip()

language_codes = ["@en", "@es", "@zh"]

wdqs_endpoint = "http://localhost:9999/bigdata/namespace/wdq/sparql"

artist_data = {}


def build_artist_dataset():
    results = query_aurora_with_conn_check(aurora_client, artists_sql_query)
    for artist in results:
        vevo_id = artist['artist_id']
        name = artist['name']
        week_views = artist['week_views']
        artist_data[vevo_id] = {'name': name, 'week_views': week_views,
                                'wiki': '', 'title': ''}


def generate_sparql_queries(query_term):
    queries = []

    for code in language_codes:
        query = LABEL_QUERY % (query_term, code)
        queries.append(query)

        query = ALIAS_QUERY % (query_term, code)
        queries.append(query)

    return queries


def generate_title_sparql_query(qid):
    return TITLE_QUERY % (qid)


def execute_sparql_query(sparql):
    data = {'format': 'json', 'query': sparql}
    data_parsed = urllib.parse.urlencode(data)
    req = urllib.request.Request(wdqs_endpoint, data_parsed.encode("utf-8"))
    response_json = None

    with urllib.request.urlopen(req) as response:
        response_bytes = response.read()
        response_json = ujson.loads(response_bytes.decode("utf8"))
        response.close()

    return response_json


def parse_qid_from_response(response_json):
    if 'results' in response_json:
        if 'bindings' in response_json['results']:
            bindings = response_json['results']['bindings']
            if len(bindings) > 1 or len(bindings) == 0:
                return None
            else:
                uri = bindings[0]['artist']['value']
                uri_split = uri.split('/')
                return uri_split[len(uri_split) - 1]


def parse_title_from_response(response_json):
    # TODO: Use url parser/wiki logic to account for titles with / inclueded
    # ex: AC/DC
    if 'results' in response_json:
        if 'bindings' in response_json['results']:
            bindings = response_json['results']['bindings']
            if len(bindings) > 1 or len(bindings) == 0:
                return None
            else:
                article = bindings[0]['articleSample']
                uri = article['value']
                uri_split = uri.split('/')
                title_encoded = uri_split[len(uri_split) - 1]
                title = title_encoded.replace('_', ' ')
                return urllib.parse.unquote_plus(title)


def update_artist_data_from_wdqs(vevo_id):
    artist_dict = artist_data[vevo_id]

    search_queries = generate_sparql_queries(artist_dict['name'])

    print("Querying data for {}".format(artist_dict['name']))

    for idx, query in enumerate(search_queries):
        try:
            print('.', end='', flush=True)
            qid = parse_qid_from_response(execute_sparql_query(query))
            time.sleep(0.1)
            if qid:
                print()
                print("Found qid {}".format(qid))
                artist_dict['wiki'] = qid
                break
            if idx == (len(search_queries) - 1):
                print()
        except Exception as e:
            print(e)
            traceback.print_exc()
            continue

    if artist_dict['wiki'] != "":
        try:
            print("Getting title for {}".format(artist_dict['name']))
            query = generate_title_sparql_query(artist_dict['wiki'])
            title = parse_title_from_response(execute_sparql_query(query))
            time.sleep(0.1)
            if title:
                print("Found title {}".format(title))
                artist_dict['title'] = title
        except Exception:
            pass

    artist_data[vevo_id] = artist_dict


if __name__ == '__main__':
    build_artist_dataset()
    updated_artists = []
    artist_ids = list(artist_data.keys())
    shuffle(artist_ids)
    artist_count = 0
    artist_total = len(artist_ids)
    qids_found = 0
    titles_found = 0
    for vevo_id in artist_ids:
        updated_artists.append(vevo_id)
        update_artist_data_from_wdqs(vevo_id)
        time.sleep(0.25)
        artist_count += 1
        if artist_data[vevo_id]['wiki'] != '':
            qids_found += 1
        if artist_data[vevo_id]['title'] != '':
            titles_found += 1
        if artist_count % 10 == 0:
            msg = '*********** %i ARTISTS PROCESSED *********' % (artist_count)
            print(msg)
            msg = '*************** %s PERCENT COMPLETE ***************' \
                % (str(artist_count*100//artist_total))
            print(msg)
            msg = '**** WIKI QIDs FOUND FOR %s PERCENT OF ARTISTS ****' \
                % (str(qids_found*100//artist_count))
            print(msg)
            msg = '****** TITLES FOUND FOR %s PERCENT OF ARTISTS *****' \
                % (str(titles_found*100//artist_count))
            print(msg)
    with open('wdqs-artists-set.json', 'w') as f:
        ujson.dump(artist_data, f, ensure_ascii=False)
