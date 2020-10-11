import enchant
d = enchant.Dict("en_US")

f = open("./species.txt", "r")
lines = f.readlines()

# for line in lines:
# 	cur = line.split(" ")
# 	common_name = []
# 	latin_name = []
# 	status = []
# 	for word in range(len(cur) - 1):
# 		if (d.check(word)):
# 			common_name.append(word)
# 		else:
# 			latin_name.append(word)
# 	status.append(cur[len(cur) - 1])
# 	print(common_name)
# 	print(latin_name)
# 	print(status)




