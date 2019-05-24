

rank = {  }

ls = sorted(rank.items(), key=lambda x: x[1]['weight'], reverse=True)


print(ls[0: 3])
