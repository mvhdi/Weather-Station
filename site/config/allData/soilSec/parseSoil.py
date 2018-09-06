conlist = [line.rstrip() for line in open('soilCon.txt')]
rawlist = [line.rstrip() for line in open('soilRaw.txt')]

conMap = {}
rawMap = {}

conStartIndex = 191
rawStartIndex = 217


for i in conlist:
	conMap[i] = conStartIndex
	conStartIndex+=1

for j in rawlist:
	rawMap[j] = rawStartIndex
	rawStartIndex+=1

rawKeys = rawMap.keys()

conKeys = conMap.keys()



masterList = []

for x in rawlist:
	if x in conKeys:
		rawValue = str(rawMap[x])
		conValue = str(conMap[x])
		del conMap[x]
		rawNameLabel = "[fields. " + x + " ]"
		ConNumLabel = "convFN = " + conValue
		rawNumLabel = "rawFN = " + rawValue
		ConNameLabel = "conName = " + x

		masterList.append(rawNameLabel)
		masterList.append(ConNumLabel)
		masterList.append(rawNumLabel)
		masterList.append(ConNameLabel)
		masterList.append(" ")


	else:
		rawValue = str(rawMap[x])
		rawNameLabel = "[fields. " + x + " ]"
		ConNumLabel = "convFN = "
		rawNumLabel = "rawFN = " + rawValue
		ConNameLabel = "conName = " 

		masterList.append(rawNameLabel)
		masterList.append(ConNumLabel)
		masterList.append(rawNumLabel)
		masterList.append(ConNameLabel)
		masterList.append(" ")

conKeys = conMap.keys()
for y in conKeys:
	conValue = str(conMap[y])
	rawNameLabel = "[fields. n/a for " + y + " ]"
	ConNumLabel = "convFN = " + conValue
	rawNumLabel = "rawFN = " 
	ConNameLabel = "conName = " + y

	masterList.append(rawNameLabel)
	masterList.append(ConNumLabel)
	masterList.append(rawNumLabel)
	masterList.append(ConNameLabel)
	masterList.append(" ")


thefile = open('soilSec.ini', 'w')
for item in masterList:
  thefile.write("%s\n" % item)
