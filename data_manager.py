import csv
import ujson


def generate_similars_csv(filename, similars, max):
    with open(filename, 'w') as csvfile:
        fieldnames = ['source']

        for i in range(1, max + 1):
            fieldnames.append("A{}".format(i))
            fieldnames.append("S{}".format(i))

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for source_artist in similars:
            row = {'source': source_artist}

            for idx, similar_tuple in enumerate(similars[source_artist]):
                row['A{}'.format(idx + 1)] = similar_tuple[0]
                row['S{}'.format(idx + 1)] = similar_tuple[1]

            writer.writerow(row)

        csvfile.close()


def load_artist_data():
    with open('artists-complete-03-18.json', 'r') as f:
        artist_data = ujson.load(f)

    return artist_data


def store_wiki_data(filename, wiki_data):
    with open(filename, 'w') as f:
        ujson.dump(wiki_data, f, ensure_ascii=False)
