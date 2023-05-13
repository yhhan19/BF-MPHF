import os
from bbhash import PyMPHF
from bbhash_table import BBHashTable
from random import random, randint, choice
from bloomfilter import BloomFilter
from time import time
from math import log, exp

size = 1000000
data = []
for i in range(size * 2):
    cur = randint(0, 2**32)
    data.append(cur)
data = sorted(set(data))[:size]

def queries(ratio):
    query = []
    for i in range(0, size // 2):
        query.append(0 if random() < ratio else 1)
    return query

def testmphf(query, b):
    half = []
    fps = []
    for i in range(0, size // 2):
        half.append(data[i * 2])
        fps.append(None)
    gamma = 1.0
    mph = PyMPHF(half, len(half), 1, gamma)
    for i in range(0, size // 2):
        fps[mph.lookup(data[i * 2])] = data[i * 2] % (2**b)
    mph.save("tmp")
    s = os.path.getsize("tmp")
    start = time()
    for i in range(0, size // 2):
        res = mph.lookup(data[i * 2 + query[i]])
        res != None and res < size // 2 and fps[res] == data[i * 2 + query[i]] % (2**b)
    t = time() - start
    tp = fn = fp = tn = 0
    for i in range(0, size // 2):
        res = mph.lookup(data[i * 2 + query[i]])
        if query[i] == 0:
            if res != None and res < size // 2 and fps[res] == data[i * 2 + query[i]] % (2**b):
                tp += 1
            else:
                fn += 1
        else:
            if res != None and res < size // 2 and fps[res] == data[i * 2 + query[i]] % (2**b):
                fp += 1
            else:
                tn += 1
    return "%4.2f" % t, "%4.2f" %((s * 8 + b * (size // 2)) / (size // 2)), "%4.2f" %(3.1 + b), "%.6f" %(fn / (fn + tp)), "%.6f" %(fp / (fp + tn)), "%.6f" % 0.0

def testbloom(error, query):
    bf = BloomFilter(expected_insertions=size // 2, err_rate=error)
    for i in range(0, size // 2):
        bf.put(data[i * 2])
    start = time()
    for i in range(0, size // 2):
        data[i * 2 + query[i]] in bf
    t = time() - start
    tp = fn = fp = tn = 0
    for i in range(0, size // 2):
        if query[i] == 0:
            if (data[i * 2] in bf):
                tp += 1
            else:
                fn += 1
        elif query[i] == 1:
            if (data[i * 2 + 1] in bf):
                fp += 1
            else:
                tn += 1
    return "%4.2f" % t, "%4.2f" %(len(bf.dumps()) * 8 / ( size // 2)), "%4.2f" %(-log(error)/log(2)/log(2)), "%.6f" %(fn / (fn + tp)), "%.6f" %(fp / (fp + tn)), "%.6f" %error

for ratio in [0.2, 0.4, 0.6, 0.8]:
    query = queries(ratio)
    for b in [0, 7, 8, 10]:
        print(testmphf(query, b))
    for err in [1/(2**7), 1/(2**8), 1/(2**10)]:
        print(testbloom(err, query))


