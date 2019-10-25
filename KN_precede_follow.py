import json
totalBigram_path = 'TotalBigram.json'

class calKN_precede_follow():
    def __init__(self, totalBigram):
        self.totalBigram = self.load_json(totalBigram)
        self.precede = {}
        self.follow = {}

    def load_json(self, path):
        with open(path) as f:
            dic = json.load(f)
        return dic

    def run(self):
        for i in self.totalBigram.keys():
            p = eval(i)[0]
            f = eval(i)[1]
            if f not in self.follow.keys():
                self.follow[f] = 1
            elif f in self.follow.keys():
                self.follow[f] += 1
            if p not in self.precede.keys():
                self.precede[p] = 1
            elif f in self.follow.keys():
                self.precede[p] += 1
        return self.precede, self.follow


cal = calKN_precede_follow(totalBigram_path)
dic_pre = cal.run()[0]
dic_fol = cal.run()[1]

dp = json.dumps(dic_pre)
df = json.dumps(dic_fol)
f = open("KN_precede.json","w")
f.write(dp)
f.close()
f = open("KN_follow.json","w")
f.write(df)
f.close()