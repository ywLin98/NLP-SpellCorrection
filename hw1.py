import csv
import nltk
from pyxdameraulevenshtein import damerau_levenshtein_distance
import string
import operator
import json
import math
from language_model import KneserNeyBigram
import itertools
import dictdiffer
import time

vocab_path = 'vocab.txt'
test_data_path = 'testdata.txt'
count_1edit_path = 'count_1edit.txt'
spell_error_path = 'spell-errors.txt'
count_bin_letter_path = 'count_bin_letter.json'
count_sin_letter_path = 'count_sin_letter.json'
totalBigram_path = 'TotalBigram.json'
precede_path = 'KN_precede.json'
follow_path = 'KN_follow.json'
dic_corpus_path = 'dic_corpus.json'


class SpellCorrection():
    def __init__(self, test_data, vocab, count_1edit, spell_error, sin_letter, bin_letter, dic_corpus):
        self.dic_num_error = self.load_testdata(test_data)[1]
        self.dic_sentences = self.load_testdata(test_data)[0]
        # self.dic_num_error = {0: 1}
        # self.dic_sentences = self.load_testdata(test_data)
        # self.dic_sentences = {0:
        #                       "If the whoe purpose is to prevent imports, one day it will be extended to other sources."}
        self.vocab = self.load_vocab(vocab)
        self.corpus = self.load_json(dic_corpus)
        self.total_n_corpus = len(self.corpus)
        self.count_1edit = self.load_count_1edit(count_1edit)
        self.dic_token = {}
        self.misspell = []
        self.count_sin_letter = self.load_json(sin_letter)
        self.count_bin_letter = self.load_json(bin_letter)
        self.kn = KneserNeyBigram(totalBigram_path, precede_path, follow_path, dic_corpus_path)

    def load_vocab(self, path):
        with open(path, 'r') as f:
            words = f.readlines()
        words = [x.strip() for x in words]
        return words

    def load_testdata(self, path):
        sentence = {}
        num_error = {}
        with open(path, 'r') as f:
            for row in csv.reader(f, delimiter='\t'):
                sentence[int(row[0])] = row[2]
                num_error[int(row[0])] = int(row[1])
        return sentence, num_error

    def load_json(self, path):
        with open(path) as f:
            dic = json.load(f)
        return dic

    def load_count_1edit(self, path):
        count_1edit = {}
        with open(path, 'r', encoding = "ISO-8859-1") as f:
            for row in csv.reader(f, delimiter='\t'):
                count_1edit[row[0]] = row[1]
        return count_1edit

    def tokenize_sentence(self, sen):
        '''
        input: sentence containing misspelled word
        return: dic {idx: word}
        '''
        ret = {}
        ret[0] = '>'
        tokens = nltk.word_tokenize(sen)
        tokens = [word for word in tokens]
        for idx, token in enumerate(tokens, 1):
            ret[idx] = token
        return ret

    def edit_distance(self, w1, w2):
        return damerau_levenshtein_distance(w1, w2)

    def swap(self, c, i, j):
        c = list(c)
        c[i], c[j] = c[j], c[i]
        return ''.join(c)

    def generate_candidate(self, misspelled_word):
        ret = {}
        for i in self.corpus.keys():
            ed = self.edit_distance(i, misspelled_word)
            if ed == 1 and i in self.vocab:
            # if self.edit_distance(i, misspelled_word) == 2:
                ret[i] = 0
        if len(ret) == 0:
            len_m = len(misspelled_word)
            for m in range(0, len_m):
                for n in range(m+1, len_m):
                    ret[self.swap(misspelled_word, m, n)] = 0
            ret = {k: v for k, v in ret.items() if self.edit_distance(k, misspelled_word) == 2 and k in self.vocab}
        return ret

    def create_dic_of_word(self, w):
        dic = {}
        for i in range(0, len(w)):
            dic[i] = w[i]
        return dic

    def correct_operation(self, w1, w2):
        '''
        w1: candidate word
        w2: misspelled word
        return: x|w
        '''
        global wi_1, wi, op
        len_w1 = len(w1)
        len_w2 = len(w2)
        dic_w1 = self.create_dic_of_word(w1)
        dic_w2 = self.create_dic_of_word(w2)

        if len_w1 < len_w2: # ins error
            op = 'ins'
            i = 0
            while i < len_w1:
                if dic_w1[i] == dic_w2[i]:
                    i += 1
                    continue
                else:
                    if i > 0:
                        wi_1 = dic_w2[i-1]
                    elif i == 0:
                        wi_1 = '>'  # the start of a word
                    wi = wi_1+dic_w2[i]  # inserted letter
                    break
            if i == len_w1:
                wi = dic_w2[i-1]+dic_w2[i]
                wi_1 = dic_w2[i-1]

        if len_w1 > len_w2: # del error
            op = 'del'
            i = 0
            while i < len_w2:
                if dic_w1[i] == dic_w2[i]:
                    i += 1
                    continue
                else:
                    if i > 0:
                        wi = dic_w1[i-1]  # the letter prior to the deleted letter
                        wi_1 = dic_w1[i-1]+dic_w1[i]
                    elif i == 0:
                        wi = '>'
                        wi_1 = '>'+dic_w1[i]  # the start of a word
                    break
            if i == len_w2:
                wi = dic_w1[i-1]
                wi_1 = dic_w1[i-1]+dic_w1[i]

        if len_w1 == len_w2:
            dd = list(dictdiffer.diff(dic_w1, dic_w2))
            len_differ = len(dd)                            # check whether it is sub or tra
            two_letters = dd[0][2]
            if len_differ == 1:
                op = 'sub'
                wi_1 = two_letters[0]
                wi = two_letters[1]
            if len_differ == 2:
                op = 'tra'
                wi_1 = two_letters[0] + two_letters[1]
                wi = two_letters[1] + two_letters[0]

        # ret = wi + '|' + wi_1
        return wi, wi_1, op

    def prob_x_w(self, x, word):   # Channel Model
        tmp = self.correct_operation(word, x)
        op = tmp[2]
        deno = 0
        if op == 'del' or op == 'tra':
            deno = self.count_bin_letter[tmp[1].lower()]
        if op == 'sub' or op == 'ins':
            deno = self.count_sin_letter[tmp[1].lower()]
        try:
            ret = int(self.count_1edit[tmp[0].lower() + '|' + tmp[1].lower()])/ int(deno)
        except:
            ret = 0
        return ret

    def prob_w_sen(self, dic_token, idx):
        '''
        input: candidate word, dictionary of token of the sentence, idx of the misspelled word
        output: kn smoothing except for the misspelled word
        '''
        # log
        ret = 0
        for i in range(1, len(dic_token)):
            if i != idx and i-1 != idx:
                ret += math.log(self.kn.run(dic_token[i], dic_token[i-1]))
        return ret

    def prob_w_mis(self, dic_token, idx, w):
        ret = 0
        if idx == 0:
            ret += math.log(self.kn.run(w, '>'))
        else:
            ret += math.log(self.kn.run(w, dic_token[idx-1]))
        try:
            ret += math.log(self.kn.run(dic_token[idx+1], w))
        except:
            pass
        return ret

    def run(self):
        myfile = open('result.txt', 'w')
        timing = 0
        for i in self.dic_sentences.keys():
            dic_token = self.tokenize_sentence(self.dic_sentences[i])
            num_change = 0
            for j in dic_token.keys():
            ############## for non word error
                if dic_token[j] not in self.vocab and dic_token[j] not in string.punctuation:  # locate the misspelled word
                    dic_cand = self.generate_candidate(dic_token[j])
                    # tmp = self.prob_w_sen(dic_token, j)
                    if len(dic_cand) == 1:
                        dic_token[j] = list(dic_cand.keys())[0]
                        num_change += 1
                    else:
                        for k in dic_cand.keys():
                            # lan_mdl = tmp + self.prob_w_mis(dic_token, j, k)
                            lan_mdl = self.prob_w_mis(dic_token, j, k)
                            chan_mdl = self.prob_x_w(dic_token[j], k)
                            if chan_mdl == 0:
                                dic_cand[k] = lan_mdl - 10
                            else:
                                dic_cand[k] = lan_mdl + math.log(chan_mdl)
                        try:
                            best_cand = max(dic_cand.items(), key=operator.itemgetter(1))[0]
                            dic_token[j] = best_cand  # substitute the misspelled word with the best candidate
                            num_change += 1
                        except:
                            pass

            ############## for real word error
            if num_change < self.dic_num_error[i]:
                lst_dic = []
                lst_dic_prob = []
                for l in dic_token.keys():
                    if l > 0 and l < len(dic_token) and dic_token[l] not in string.punctuation:
                        kn_other_words = self.prob_w_sen(dic_token, l)
                        dic_can_real = self.generate_candidate(dic_token[l]) # generate candidates
                        dic_can_real[dic_token[l]] = 0  # adding itself
                        best_prob = -1e20
                        best_word = ''
                        for m in dic_can_real.keys():
                            kn_cand_word = self.prob_w_mis(dic_token, l, m)
                            if kn_cand_word > best_prob:
                                best_prob = kn_cand_word
                                best_word = m
                        tmp_dic = dic_token.copy()
                        tmp_dic[l] = best_word
                        lst_dic.append(tmp_dic)
                        lst_dic_prob.append(kn_other_words+best_prob)
                dic_token = lst_dic[lst_dic_prob.index(max(lst_dic_prob))]

            corrected_sen = ' '.join(x for i, x in enumerate(dic_token.values()) if i != 0)
            myfile.write(str(i) + '\t' + corrected_sen + '\n')
        myfile.close()


sc = SpellCorrection(test_data_path, vocab_path, count_1edit_path,
                     spell_error_path, count_sin_letter_path, count_bin_letter_path, dic_corpus_path)
start_time = time.time()
sc.run()
print("--- %s seconds ---" % (time.time() - start_time))