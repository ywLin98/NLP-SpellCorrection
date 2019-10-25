from nltk.corpus import gutenberg
from nltk.corpus import reuters
import string
import json

def load_corpus():
    ret = {}
    for w in gutenberg.words() + reuters.words():
        if w not in ret:
            ret[w] = 1
        else:
            ret[w] += 1
    return ret
dic_corpus = load_corpus()

dg = json.dumps(dic_corpus)
f = open("dic_corpus.json","w")
f.write(dg)
f.close()


class TotalBigram():
    def __init__(self):
        self.corpus = gutenberg.sents() + reuters.sents()

    def CountTotalBigram(self):
        dic_bigram = {}
        for sen in self.corpus:
            sen = ['>'] + [word for word in sen if word not in string.punctuation]
            for i in range(2, len(sen)+1):
                bigram = str(sen[i-2:i])
                if bigram in dic_bigram:
                    dic_bigram[bigram] += 1
                else:
                    dic_bigram[bigram] = 1
        return dic_bigram

tb = TotalBigram()
dic = tb.CountTotalBigram()

d = json.dumps(dic)
f = open("TotalBigram.json","w")
f.write(d)
f.close()