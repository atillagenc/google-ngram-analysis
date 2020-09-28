#
import sys
import time

import matplotlib.pyplot as plt

VALID_LANGUAGES = ['eng']
MIN_YEAR = 1500
MAX_YEAR = 2020
goggle_ngram_viewer_dataset_folder = '/home/agenc/data/term/downloads/google_ngrams/1/'


def get_ngram_dataset_file(keyword):
    return goggle_ngram_viewer_dataset_folder + 'googlebooks-eng-all-1gram-20120701-' + keyword.lower()[0]


def get_ngram_dataset_totals_file():
    return goggle_ngram_viewer_dataset_folder + 'googlebooks-eng-all-totalcounts-20120701.txt'


def load_totals_data():
    data = []
    for i in list(range(MIN_YEAR, MAX_YEAR)):
        data.append(0)
    max_year = MIN_YEAR
    with open(get_ngram_dataset_totals_file()) as infile:
        for line in infile:
            split_line = line.split("\t")
            for valueString in split_line:
                triplet_values = valueString.split(',')
                if len(triplet_values) > 1:
                    year = int(triplet_values[0])
                    match_count = int(triplet_values[1])
                    data[year - MIN_YEAR] = data[year - MIN_YEAR] + match_count
                    if year > max_year:
                        max_year = year
    print("Max year in totals:" + str(max_year))
    return data


def filter_data(keyword, start, end, split_line):
    year = int(split_line[1])
    return keyword == split_line[0].lower() and start <= year <= end


def load_data(keyword, start, end):
    max_year = MIN_YEAR
    data = [0] * (end - start)
    keyword = keyword.lower()
    with open(get_ngram_dataset_file(keyword)) as infile:
        for line in infile:
            split_line = line.split("\t")
            if filter_data(keyword, start, end, split_line):
                year = int(split_line[1])
                # print(split_line[0], split_line[1], split_line[2], len(data), year-start)
                data[year - start] = data[year - start] + int(split_line[2])
                if year > max_year:
                    max_year = year
    print("Max year in data for keyword="+keyword+":" + str(max_year))
    return data


def compute_frequencies(totals, data, start):
    frequencies = []
    for i in range(len(data)):
        year = i + start
        total_count = totals[year - MIN_YEAR]
        if total_count > 0:
            frequency = float(data[i]) / float(total_count)
            if frequency > 1:
                print("Frequency=" + str(frequency) + " count=" + str(data[i]) + " total count=" + str(total_count))
            frequencies.append(frequency)
        else:
            frequencies.append(0)
            if data[i] != 0:
                print("Total count for year: " + str(year) + " is total count="
                      + str(total_count) + " count=" + str(data[i]))
    return frequencies


def plot_graph(keyword, start, end, frequencies):
    plt.axis([start, end, min(frequencies), max(frequencies)])
    plt.xlabel('Year')
    plt.ylabel('Frequency(%)')
    plt.title('Keyword: ' + keyword.capitalize())
    plt.plot(list(range(start, end)), frequencies)  # Plot X=Year , Y=Frequency(%)
    plt.savefig(keyword + '.' + str(start) + '-' + str(end) + '.png')
    plt.show()


def ngram_viewer(keyword, start, end, totals):
    data = load_data(keyword, start, end)
    # print(data)
    frequencies = compute_frequencies(totals, data, start)
    # print(frequencies)
    plot_graph(keyword, start, end, frequencies)


def parse_config(args):
    from argparse import ArgumentParser
    parser = ArgumentParser(
        description='Extract word frequency from Google Ngram dataset')
    parser.add_argument(
        '--keyword', dest='keyword', required=True,
        help='search keyword')
    parser.add_argument(
        '--startyear', dest='startyear', type=int, default=MIN_YEAR,
        help='only include words after specified year (default %d)' % MIN_YEAR)
    parser.add_argument(
        '--endyear', dest='endyear', type=int, default=MAX_YEAR,
        help='only include words up to specified year (default %d)' % MAX_YEAR)
    parser.add_argument(
        '--lang', dest='lang', required=False, default='eng', choices=VALID_LANGUAGES,
        help='language code')
    parser.add_argument('--debug', action="store_true")
    config = parser.parse_args(args)

    if config.startyear < 0:
        raise Exception('invalid startyear, must be > 0')
    if config.endyear > MAX_YEAR:
        raise Exception('invalid endyear, must be < %d' % MAX_YEAR)
    if config.endyear < config.startyear:
        raise Exception('endyear < startyear')
    return config


if __name__ == '__main__':
    start_time = time.time()
    config = parse_config(sys.argv[1:])
    totals = load_totals_data()
    ngram_viewer(config.keyword, config.startyear, config.endyear, totals)
    print("--- %s seconds ---" % (time.time() - start_time))
