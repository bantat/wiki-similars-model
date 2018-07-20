import wiki_api
from time import sleep
from wiki_parser import WikiTextParser

wikitext_parser = WikiTextParser()


def parse_infobox_content(infobox):
    infobox_dict = {'genres': [], 'labels': [], 'associated': []}

    if 'data' in infobox:
        data = infobox['data']
        if 'genre' in data and 'links' in data['genre']:
            genre_links = data['genre']['links']
            artist_genres = []
            for link in genre_links:
                artist_genres.append(link['page'])
            infobox_dict['genres'] = artist_genres
        if 'label' in data and 'links' in data['label']:
            label_links = data['label']['links']
            artist_labels = []
            for link in label_links:
                artist_labels.append(link['page'])
            infobox_dict['labels'] = artist_labels
        if 'associated_acts' in data and 'links' in data['associated_acts']:
            associated_links = data['associated_acts']['links']
            artist_associated = []
            for link in associated_links:
                artist_associated.append(link['page'])
            infobox_dict['associated'] = artist_associated

    if 'lists' in infobox:
        for list in infobox['lists']:
            for item in list:
                if item['text'].startswith('genre') and 'links' in item:
                    genre_links = item['links']
                    artist_genres = []
                    for link in genre_links:
                        artist_genres.append(link['page'])
                    infobox_dict['genres'] = artist_genres
                if item['text'].startswith('label') and 'links' in item:
                    label_links = item['links']
                    artist_labels = []
                    for link in label_links:
                        artist_labels.append(link['page'])
                    infobox_dict['labels'] = artist_labels
                if item['text'].startswith('associated_acts') \
                        and 'links' in item:
                    associated_links = item['links']
                    artist_associated = []
                    for link in associated_links:
                        artist_associated.append(link['page'])
                    infobox_dict['associated'] = artist_associated

    return infobox_dict


def build_artist_data(title):
    categories = wiki_api.get_categories_from_title(title)

    infobox_wikitext = wiki_api.get_infobox_wikitext_from_title(title)

    if infobox_wikitext != '':
        infobox = wikitext_parser.get_infobox_from_wikitext(infobox_wikitext)
    else:
        infobox = {}

    artist_data = parse_infobox_content(infobox)

    artist_data['categories'] = categories

    return artist_data


def generate_wiki_data_for_titles(titles):
    wiki_data = {}
    num_titles = len(titles)

    for idx, title in enumerate(titles):
        if (idx + 1) % 500 == 0:
            print("Sleeping 1 minute")
            sleep(60)
        elif (idx + 1) % 1000 == 0:
            print("Sleeping 3 minutes")
            sleep(3 * 60)
        print("******** ARTIST #{} OF {} ********".format(idx + 1, num_titles))
        try:
            print("Building artist data for {}".format(title))
            artist_data = build_artist_data(title)
            print("Collected following data...")
            print(artist_data)
            wiki_data[title] = artist_data
        except Exception as e:
            print("EXCEPTION ON {}".format(title))
            print(e)

    return wiki_data
