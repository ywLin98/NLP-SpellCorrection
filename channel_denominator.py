import string
import json
import csv
import re

count_sin_letter = {}
count_bin_letter = {}
spell_err = {}
spell_error_path = 'spell-errors.txt'


def load_spelling_error(path):
    sple = {}
    with open(path, 'r') as f:
        for row in csv.reader(f, delimiter=':'):
            if len(re.findall("[^A-Za-z' ]", row[0])) == 0:
                err = [word.strip() for word in row[1].split(',') if len(re.findall("[^A-Za-z' ]", word)) == 0]
                err = [word for word in err if len(word) > 0]
                if len(err) > 0:
                    sple[row[0]] = err
    return sple


def channel_denominator():
    count_sin_letter["'"] = 0
    count_sin_letter[">"] = 0
    count_sin_letter["-"] = 0
    for l in string.ascii_lowercase + string.ascii_uppercase:
        count_sin_letter[l] = 0
        count_bin_letter["'" + l] = 0
        count_bin_letter[l + "'"] = 0
        count_bin_letter["-" + l] = 0
        count_bin_letter[l + "-"] = 0
        count_bin_letter[">" + l] = 0

    for m in string.ascii_lowercase + string.ascii_uppercase:
        for n in string.ascii_lowercase + string.ascii_uppercase:
            count_bin_letter[m + n] = 0

    for i in spell_err.keys():
        factor = len(spell_err[i])
        count_sin_letter[">"] += factor
        count_bin_letter[">"+i[0]] += factor
        len_word = len(i)
        for j in i:
            try:
                count_sin_letter[j] += 1 * factor
            except:
                pass
        for k in range(2, len_word+1):
            try:
                count_bin_letter[i[k-2:k]] += 1 * factor
            except:
                pass


spell_err = load_spelling_error(spell_error_path)
channel_denominator()

sin = json.dumps(count_sin_letter)
f = open("count_sin_letter.json","w")
f.write(sin)
f.close()

bin = json.dumps(count_bin_letter)
f = open("count_bin_letter.json","w")
f.write(bin)
f.close()