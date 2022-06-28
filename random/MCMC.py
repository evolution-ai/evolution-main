import numpy as np
from matplotlib import pyplot as plt
from collections import Counter

p0 = [1/3, 1/6, 1/3, 1/6]
p1 = [0, 1/2, 0, 1/2]
p2 = [0, 0, 2/3, 1/3]
p3 = [0, 0, 0, 1]

all_counts = []

for i in range(100000):

    state = 0
    counts = 0

    while True:
        if state == 0:
            state = np.random.choice([0,1,2,3], p=p0)
        elif state == 1:
            state = np.random.choice([0,1,2,3], p=p1)
        elif state == 2:
            state = np.random.choice([0,1,2,3], p=p2)

        counts += 1
        if state == 3: break

    all_counts.append(counts)
    
print(np.mean(all_counts))

all_counts.sort()
histo = Counter(all_counts)

for key in histo:
    histo[key]/= 100000

print(histo[0]+histo[1]+histo[2])