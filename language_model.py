from nltk.corpus import gutenberg
from nltk.corpus import reuters
import json
totalBigram_path = 'TotalBigram.json'
precede_path = 'KN_precede.json'
follow_path = 'KN_follow.json'
dic_corpus_path = 'dic_corpus.json'


class KneserNeyBigram():
    def __init__(self, totalBigram, precede, follow, corpus):
        self.d = 0.75
        self.corpus_count = self.load_json(corpus)
        self.totalBigram = self.load_json(totalBigram)
        self.len_totalBigram = len(self.totalBigram)
        self.precede = self.load_json(precede)
        self.follow = self.load_json(follow)

    def load_json(self, path):
        with open(path) as f:
            dic = json.load(f)
        return dic

    def run(self, wi, wi_1):
        try:
            Pconti = self.precede[wi] / self.len_totalBigram
        except:
            Pconti = 0
        try:
            count_lambda = self.follow[wi_1]
        except:
            count_lambda = 0
        try:
            cWi_1Wi = self.totalBigram[str([wi_1, wi])]
        except:
            cWi_1Wi = 0
        try:
            cWi_1 = self.corpus_count[wi_1]
        except:
            cWi_1 = 1e10   # penalize if there is no wi_1 at all
        lambdaWi_1 = (self.d/cWi_1) * count_lambda
        p = max(cWi_1Wi-self.d, 0) / cWi_1 + lambdaWi_1 * Pconti
        if p == 0:
            return 0.0000000001
        else:
            return p


# kn = KneserNeyBigram(totalBigram_path, precede_path, follow_path)
# print(kn.run('>', 'This'))


# def Pcon_Lambda(self, w, wi_1):
#     ptmp = 0
#     lamb = 0
#     for i in self.totalBigram.keys():
#         if eval(i)[1] == w:
#             ptmp += 1
#         if eval(i)[0] == wi_1:
#             lamb += 1
#     Pconti = ptmp / self.len_totalBigram
#     return Pconti, lamb
#
# def run(self, wi, wi_1):
#     tmp = self.Pcon_Lambda(wi, wi_1)
#     try:
#         cWi_1Wi = self.totalBigram[str([wi_1, wi])]
#     except:
#         cWi_1Wi = 1
#     try:
#         cWi_1 = self.corpus_count[wi_1]
#     except:
#         cWi_1 = 1
#     lambdaWi_1 = (self.d/cWi_1) * tmp[1]
#     p = max(cWi_1Wi-self.d, 0) / cWi_1 + lambdaWi_1 * tmp[0]
#     if p == 0:
#         return 0.00000001
#     else:
#         return p


# def Pcontinuation(self, w):
#     c_Wi_1_W = 0
#     for i in self.totalBigram.keys():
#         if eval(i)[1] == w:
#             c_Wi_1_W += 1
#     Pconti = c_Wi_1_W / self.len_totalBigram
#     return Pconti
#
# def count_lambdaWi_1(self, wi_1):   # The number of word types that can follow wi-1
#     c_Wi_1_W = 0
#     for i in self.totalBigram.keys():
#         if eval(i)[0] == wi_1:
#             c_Wi_1_W += 1
#     return c_Wi_1_W
#
# def run(self, wi, wi_1):
#     try:
#         cWi_1Wi = self.totalBigram[str([wi_1, wi])]
#     except:
#         cWi_1Wi = 1
#     try:
#         cWi_1 = self.corpus_count[wi_1]
#     except:
#         cWi_1 = 1
#     lambdaWi_1 = (self.d/cWi_1) * self.count_lambdaWi_1(wi_1)
#     p = max(cWi_1Wi-self.d, 0) / cWi_1 + lambdaWi_1 * self.Pcontinuation(wi)
#     if p == 0:
#         return 0.00000001
#     else:
#         return p