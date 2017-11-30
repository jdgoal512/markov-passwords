#!/usr/bin/python
import argparse
import numpy
import random

unique_words = set()

#Read in the text
def getWords(filename):
    global unique_words
    unique_words.add("$TOP")
    try:
        with open(filename) as f:
            content = f.readlines();
            #Get list of words
            for text in content:
                words = text.split()
                for word in words:
                    if (word != ""):
                        unique_words.add(word)
    except FileNotFoundError as exception:
        print("Error: " + filename + " doesn't exist, aborting")
        exit()
    return unique_words

def addProbability(filename):
    with open(filename) as f:
        content = f.readlines();

        #Add probabilities
        global stats
        global all_words
        for text in content:
            if text != "":
                text = text[:-1] + " $TOP"
                words = text.split()
                last_word = words[0]
                for word in words[1:]:
                    if (word != ""):
                        stats[all_words.index(last_word )][all_words.index(word)] += 1
                        last_word = word
    return stats

#Normalize the probabilities
def normalizeStats():
    global stats
    global all_words
    for i in range(len(all_words)):
        total = 0
        for j in range(len(all_words)):
            total += stats[i][j]
        if total > 0:
            for j in range(len(all_words)):
                stats[i][j] = stats[i][j] / total
    return stats

#Generate a phrase
def babble(max_length = 3):
    global all_words
    current_word = all_words[random.randint(0, len(all_words) - 1)]
    text = current_word
    current_count = 1
    while current_word != "$TOP" and current_count < max_length:
        pval = stats[all_words.index(current_word)]
        next_index = numpy.nonzero(numpy.random.multinomial(n=1, pvals=pval, size=1))[1][0]
        next_word = all_words[next_index]
        text = text + next_word
        current_word = next_word;
        current_count += 1
    #Remove $TOP
    if text[-4:] == "$TOP":
        text = text[:-4]

    #Don't return blank lines
    if text == "":
        return babble(max_length)

    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input-file', dest='input_file', type=str, default="", help='Name of file to read')
    parser.add_argument('-o', '--output-file', dest='output_file', type=str, default="", help='File to write output to (defaults to stdout)')
    parser.add_argument('-n', '--number-of-times', dest='number_of_times', type=int, default=1, help='Number of phrases to generate')
    parser.add_argument('-l', '--max-length', dest='max_length', type=int, default=3, help='Max number of words to be in a phrase')
    args = parser.parse_args()

    #Get command line parameters
    input_file = args.input_file
    output_file = args.output_file
    number_of_phrases = args.number_of_times
    max_length = args.max_length

    if input_file == "":
        parser.print_help()
        exit()

    if output_file == "":
        write_output = False
    else:
        write_output = True

    #Get all the words from the input file
    getWords((input_file))
    all_words = list(unique_words)

    #Create probability matrix
    stats = [[0 for x in range(len(all_words))] for y in range(len(all_words))]
    addProbability(input_file)
    normalizeStats()

    #Generate phrases
    if (write_output):
        output = open(output_file, 'w')
        for i in range(number_of_phrases):
            output.write(babble(max_length) + "\n")
        output.close()
    else:
        for i in range(number_of_phrases):
            print(babble(max_length))
