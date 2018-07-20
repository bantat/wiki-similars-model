import ujson
import time
import urllib.request
import urllib.parse

wiki_endpoint = "https://en.wikipedia.org/w/api.php"
user_agent_string = "py-wiki-artist-model/0.1 (Tore.Banta@gmail.com)"


def execute_api_call(params):
    data_parsed = urllib.parse.urlencode(params)
    req = urllib.request.Request(wiki_endpoint, data_parsed.encode("utf-8"),
                                 headers={'User-Agent': user_agent_string})
    response_json = None

    with urllib.request.urlopen(req) as response:
        response_bytes = response.read()
        response_json = ujson.loads(response_bytes.decode("utf8"))
        response.close()

    time.sleep(0.1)

    return response_json


def get_categories_from_title(title):
    params = {'action': 'query', 'format': 'json', 'prop': 'categories',
              'titles': title, 'clshow': '!hidden', 'cllimit': 'max'}
    response = execute_api_call(params)

    categories = []

    if 'query' in response:
        pages = response['query']['pages']
        for page in pages:
            category_array = pages[page]['categories']
            for category in category_array:
                categories.append(category['title'])

    return categories


def get_infobox_wikitext_from_title(title):
        params = {'action': 'query', 'format': 'json', 'prop': 'revisions',
                  'rvprop': 'content', 'rvsection': '0', 'titles': title}
        response = execute_api_call(params)

        infobox_text = ''

        if 'query' in response:
            pages = response['query']['pages']
            for page in pages:
                revisions_array = pages[page]['revisions']
                infobox_text = revisions_array[0]['*']

        return infobox_text
