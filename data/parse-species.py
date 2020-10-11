f = open("species.txt", "r")
lines = f.readlines()



for line in lines:
	cur = line.split(" ")
	for word in range(len(cur) - 1):
		if (word)