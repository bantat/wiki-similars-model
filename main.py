import wiki_data_gen
import data_manager

from wiki_network_model import WikiNetworkModel
from random import shuffle

# temp code test functionality
# with open('wiki-data-test-py.json', 'r') as f:
#     wiki_data = ujson.load(f)
# with open('artists-complete-03-18.json', 'r') as f:
#     artist_data = ujson.load(f)
# print(wiki_model.get_artist_similars("Local Natives", 25, test=True))

if __name__ == '__main__':
    artist_data = data_manager.load_artist_data()

    titles = []
    for artist in artist_data:
        if artist['title'] != '':
            titles.append(artist['title'])
    shuffle(titles)

    wiki_data = wiki_data_gen.generate_wiki_data_for_titles(titles)
    data_manager.store_wiki_data('wiki-data-temp.json', wiki_data)

    wiki_model = WikiNetworkModel(wiki_data, artist_data)

    wiki_model.generate_similars(50)
    data_manager.generate_similars_csv('test-similars.csv',
                                       wiki_model.similars, 50)
