import networkx as nx
import operator
import math


class WikiNetworkModel():

    def __init__(self, wiki_data, artist_data):
        self.artist_data = {}
        for artist_dict in artist_data:
            if artist_dict['title'] != '':
                artist_title = artist_dict['title']
                artist_info = {'vevo': artist_dict['vevo'],
                               'birth': artist_dict['birth'],
                               'inception': artist_dict['inception'],
                               'week_views': artist_dict['week_views']}
                self.artist_data[artist_title] = artist_info
        # TODO: Not necessary in complete pipeline run
        for artist in wiki_data:
            if artist not in self.artist_data:
                self.artist_data[artist] = {'vevo': '', 'birth': '',
                                            'inception': '', 'week_views': 0}
        self.graph = self.build_graph(wiki_data)
        self.similars = {}

    def build_graph(self, wiki_data):
        G = nx.DiGraph()

        print("Building Wiki Artist Graph...")

        for artist in wiki_data:
            artist_info = self.artist_data[artist]
            G.add_node(artist, type='artist', vevo=artist_info['vevo'],
                       birth=artist_info['birth'],
                       inception=artist_info['inception'],
                       week_views=artist_info['week_views'])
            artist_data = wiki_data[artist]

            for genre in artist_data['genres']:
                if genre not in G:
                    G.add_node(genre, type='genre')
                G.add_edge(artist, genre, source='artist')
                G.add_edge(genre, artist, source='genre')

            for label in artist_data['labels']:
                if label not in G:
                    G.add_node(label, type='label')
                G.add_edge(artist, label, source='artist')
                G.add_edge(label, artist, source='label')

            for associated in artist_data['associated']:
                if associated not in G:
                    if associated in self.artist_data:
                        artist_info = self.artist_data[associated]
                    else:
                        artist_info = {'vevo': '', 'birth': '',
                                       'inception': '', 'week_views': 0}
                    G.add_node(associated, type='artist',
                               vevo=artist_info['vevo'],
                               birth=artist_info['birth'],
                               inception=artist_info['inception'],
                               week_views=artist_info['week_views'])
                G.add_edge(artist, associated, source='source-artist')

            for category in artist_data['categories']:
                if category not in G:
                    G.add_node(category, type='category')
                G.add_edge(artist, category, source='artist')
                G.add_edge(category, artist, source='category')

        return G

    def update_node_first_degree(self, map):
        if 'source-artist' not in map:
            map['source-artist'] = 1
        else:
            map['source-artist'] = map['source-artist'] + 1

        return map

    def update_node_second_degree(self, source, map):
        if source == 'genre':
            if 'genre' not in map:
                map['genre'] = 1
            else:
                map['genre'] = map['genre'] + 1
        elif source == 'label':
            if 'label' not in map:
                map['label'] = 1
            else:
                map['label'] = map['label'] + 1
        elif source == 'category':
            if 'category' not in map:
                map['category'] = 1
            else:
                map['category'] = map['category'] + 1
        elif source == 'artist':
            if 'artist' not in map:
                map['artist'] = 1
            else:
                map['artist'] = map['artist'] + 1
        elif source == 'source-artist':
            if 'source-return' not in map:
                map['source-return'] = 1
            else:
                map['source-return'] = map['source-return'] + 1

        return map

    def update_node_third_degree(self, source, map):
        if source == 'genre':
            if 'genre-ext' not in map:
                map['genre-ext'] = 1
            else:
                map['genre-ext'] = map['genre-ext'] + 1
        elif source == 'label':
            if 'label-ext' not in map:
                map['label-ext'] = 1
            else:
                map['label-ext'] = map['label-ext'] + 1
        elif source == 'category':
            if 'category-ext' not in map:
                map['category-ext'] = 1
            else:
                map['category-ext'] = map['category-ext'] + 1
        elif source == 'artist':
            if 'artist-ext' not in map:
                map['artist-ext'] = 1
            else:
                map['artist-ext'] = map['artist-ext'] + 1
        # TODO: maybe add source artist count here?

        return map

    def generate_artist_mappings(self, artist):
        artist_mappings = {}

        neighbors = self.graph.neighbors(artist)

        for neighbor in neighbors:
            if self.graph.nodes[neighbor]['type'] == 'artist':
                if neighbor not in artist_mappings:
                    artist_map = {}
                    artist_map = self.update_node_first_degree(artist_map)
                    artist_mappings[neighbor] = artist_map
                else:
                    artist_map = self.update_node_first_degree(
                                                    artist_mappings[neighbor])
                    artist_mappings[neighbor] = artist_map

            second_neighbors = self.graph.neighbors(neighbor)

            for second_neighbor in second_neighbors:
                if self.graph.nodes[second_neighbor]['type'] == 'artist' and \
                        second_neighbor != artist:
                    if second_neighbor not in artist_mappings:
                        artist_map = {}
                        edge_data = self.graph[neighbor][second_neighbor]
                        source = edge_data['source']
                        artist_map = self.update_node_second_degree(source,
                                                                    artist_map)
                        artist_mappings[second_neighbor] = artist_map
                    else:
                        edge_data = self.graph[neighbor][second_neighbor]
                        source = edge_data['source']
                        artist_map = self.update_node_second_degree(
                                    source, artist_mappings[second_neighbor])
                        artist_mappings[second_neighbor] = artist_map

                third_neighbors = self.graph.neighbors(second_neighbor)

                for third_neighbor in third_neighbors:
                    if self.graph.nodes[third_neighbor]['type'] == 'artist' \
                            and second_neighbor != artist:
                        if third_neighbor not in artist_mappings:
                            artist_map = {}
                            edge_data = \
                                self.graph[second_neighbor][third_neighbor]
                            source = edge_data['source']
                            artist_map = self.update_node_third_degree(
                                                            source, artist_map)
                            artist_mappings[third_neighbor] = artist_map
                        else:
                            edge_data = \
                                self.graph[second_neighbor][third_neighbor]
                            source = edge_data['source']
                            artist_map = self.update_node_third_degree(
                                    source, artist_mappings[third_neighbor])
                            artist_mappings[third_neighbor] = artist_map

        return artist_mappings

    def get_popularity_factor(self, source_artist, artist):
        source_views = self.graph.nodes[source_artist]['week_views']
        similar_views = self.graph.nodes[artist]['week_views']

        if source_views < 10000:
            return 1

        if source_views == 0:
            return 1
        if similar_views == 0:
            return 0.1

        if similar_views > source_views:
            return 1

        source_magnitude = int(math.log10(source_views) + 1)
        similar_magnitude = int(math.log10(similar_views) + 1)

        return similar_magnitude / source_magnitude

    def get_age_difference_factor(self, source_artist, artist):
        inception_diff_range = 20
        birth_diff_range = 20
        birth_to_inception_boost = 25
        unknown_factor = 0.3

        source_info = self.graph.nodes[source_artist]
        similar_info = self.graph.nodes[artist]

        if source_info['birth'] != '' and similar_info['birth'] != '':
            difference = math.fabs(source_info['birth']
                                   - similar_info['birth'])
            if difference >= birth_diff_range:
                return 0.2
            else:
                return 1 - (0.75 * (difference / birth_diff_range))

        elif source_info['inception'] != '' and \
                similar_info['inception'] != '':
            difference = math.fabs(source_info['inception'] -
                                   similar_info['inception'])
            if difference >= inception_diff_range:
                return 0.1
            else:
                return 1 - (difference / inception_diff_range)

        else:
            if source_info['birth'] == '' and similar_info['birth'] == '' and \
                    source_info['inception'] == '' and \
                    similar_info['inception'] == '':
                return 1
            if source_info['birth'] != '':
                birth = source_info['birth']
                inception = similar_info['inception']
            else:
                birth = similar_info['birth']
                inception = source_info['inception']
            if birth == '' or inception == '':
                return unknown_factor
            difference = math.fabs((birth + birth_to_inception_boost)
                                   - inception)
            if difference >= inception_diff_range:
                return 0.1
            else:
                return 1 - (difference / inception_diff_range)

    def generate_artist_scorings(self, source_artist, artist_mappings):
        artist_scorings = {}

        for artist in artist_mappings:
            if self.graph.nodes[artist]['vevo'] == '':
                continue
            artist_map = artist_mappings[artist]
            total = 0

            for type in artist_map:
                if type == 'artist':
                    total += 20 * artist_map[type]
                elif type == 'genre':
                    total += 8 * artist_map[type]
                elif type == 'category':
                    total += 5 * artist_map[type]
                elif type == 'source-artist':
                    total += 40 * artist_map[type]
                elif type == 'label':
                    total += 0.5 * artist_map[type]
                elif type == 'artist-ext':
                    total += 1.0 * artist_map[type]
                elif type == 'genre-ext':
                    total += 0.1 * artist_map[type]
                elif type == 'category-ext':
                    total += 0.05 * artist_map[type]

            if 'genre' not in artist_map and 'genre-ext' not in artist_map:
                total = total * 0.5

            popularity_factor = self.get_popularity_factor(source_artist,
                                                           artist)
            age_factor = self.get_age_difference_factor(source_artist, artist)

            total = total * popularity_factor * age_factor
            artist_scorings[artist] = total

        return artist_scorings

    def get_artist_similars(self, artist, max, test=False):
        if test:
            print("Generating similars for artist {}".format(artist))

        artist_mappings = self.generate_artist_mappings(artist)

        artist_scorings = self.generate_artist_scorings(artist,
                                                        artist_mappings)

        results = list(reversed(sorted(artist_scorings.items(),
                                       key=operator.itemgetter(1))))[:max]

        if test:
            for artist_tuple in results[:25]:
                print(artist_tuple, end=': ')
                print(artist_mappings[artist_tuple[0]])

        scored_similars = []
        if len(results) > 0:
            max = results[0][1]
            for artist_tuple in results:
                ratio_score = artist_tuple[1]/max
                scored_similars.append((artist_tuple[0], ratio_score))

        return scored_similars

    def generate_similars(self, max):
        print("Generating artist similars data for complete dataset")
        artist_count = len(self.artist_data)
        for idx, artist in enumerate(self.artist_data):
            if idx % 100 == 0:
                print("{} of {}".format(idx, artist_count))
            if artist not in self.graph:
                continue
            artist_info = self.artist_data[artist]
            similars = self.get_artist_similars(artist, max)
            vevo_similars = []
            for similar_tuple in similars:
                vevo_tuple = (self.artist_data[similar_tuple[0]]['vevo'],
                              similar_tuple[1])
                vevo_similars.append(vevo_tuple)
            if len(vevo_similars) > 0:
                self.similars[artist_info['vevo']] = vevo_similars


# if __name__ == '__main__':
#     with open('wiki-data-test-py.json', 'r') as f:
#         wiki_data = ujson.load(f)
#     with open('artists-complete-03-18.json', 'r') as f:
#         artist_data = ujson.load(f)
#     wiki_model = WikiNetworkModel(wiki_data, artist_data)
#     wiki_model.generate_similars(50)
#     # wiki_model.get_artist_similars("Joel Taylor (musician)", 25)
