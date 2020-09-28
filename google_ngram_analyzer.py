#
import time
import matplotlib.pyplot as plt
import sys

VALID_LANGUAGES = ['eng']
MIN_YEAR = 1500
MAX_YEAR = 2012
goggle_ngram_viewer_dataset_folder = '/home/agenc/data/term/downloads/google_ngrams/1/'


def get_ngram_dataset_file(keyword):
    return goggle_ngram_viewer_dataset_folder + 'googlebooks-eng-all-1gram-20120701-' + keyword.lower()[0]


def get_ngram_dataset_totals_file():
    return goggle_ngram_viewer_dataset_folder + 'googlebooks-eng-all-totalcounts-20120701.txt'


def load_totals_data():
    data = []
    for i in list(range(1500, 2012)):
        data.append(0)
    with open(get_ngram_dataset_totals_file()) as infile:
        for line in infile:
            split_line = line.split("\t")
            for valueString in split_line:
                triplet_values = valueString.split(',')
                if len(triplet_values) > 1:
                    year = int(triplet_values[0])
                    match_count = int(triplet_values[1])
                    data[year - 1500] = data[year - 1500] + match_count
    return data


def filter_data(keyword, start, end, split_line):
    year = int(split_line[1])
    return keyword == split_line[0].lower() and start <= year <= end


def load_data(keyword, start, end):
    data = [0] * (end - start)
    keyword = keyword.lower()
    with open(get_ngram_dataset_file(keyword)) as infile:
        for line in infile:
            split_line = line.split("\t")
            if filter_data(keyword, start, end, split_line):
                year = int(split_line[1])
                # print(split_line[0], split_line[1], split_line[2], len(data), year-start)
                data[year - start] = data[year - start] + int(split_line[2])
    return data


def compute_frequencies(totals, data, start):
    frequencies = []
    for i in range(len(data)):
        year = i + start
        total_count = totals[year - 1500]
        if total_count > 0:
            frequency = data[i] / total_count
            frequencies.append(frequency)
        else:
            frequencies.append(0)
            print("Total count for year: " + str(year) + " is " + str(total_count))
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
    print(data)
    frequencies = compute_frequencies(totals, data, start)
    print(frequencies)
    plot_graph(keyword, start, end, frequencies)


def parse_config(args):
    from argparse import ArgumentParser
    parser = ArgumentParser(
        description='Extract top frequency words from Google Ngram data')
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
    ngram_viewer("analysis", 1500, 2012, totals)
    print("--- %s seconds ---" % (time.time() - start_time))
