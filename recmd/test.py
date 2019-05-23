d = {}

d[1] = dict()

d[1][2] = 1
# print(d)
v = {1: 1, 2:2, 3: 1.5}
ls = sorted(v.items(), key=lambda x: x[1])

for i in ls:
    print(i)

