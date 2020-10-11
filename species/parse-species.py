import enchant
import json
d = enchant.Dict("en_US")

f = open("./species.txt", "r")
lines = f.readlines()
js = {}

for line in lines:
	cur = line.split(" ")
	common_name = []
	latin_name = []
	for i, word in enumerate(cur):
		if i != len(cur) - 1:
			if (d.check(word)):
				common_name.append(word)
			else:
				latin_name.append(word)
	common_n = " ".join(common_name)
	if latin_name[0][0].islower():
		latin_name.remove(latin_name[0])
	latin_n = " ".join(latin_name)
	status = cur[len(cur) - 1].rstrip()
	if status == 'FE':
		js[latin_n]='Endangered'
	elif status == 'FT' or status == 'ST' or status == 'SSC':
		js[latin_n]='Threatened'

# with open("./species-list.json", 'w') as outfile:
#     json.dump(js, outfile, indent=4)		




