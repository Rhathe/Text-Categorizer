#Text Categorization Program for NLP
#Ramon Sandoval

import re, os, string, math, operator

trainListName = raw_input("Please enter training data list name: ")
testListName = raw_input("Please enter testing data list name: ")
resultName = raw_input("Please enter output file: ")

#Default files if nothing is entered
if not trainListName:
	trainListName = 'corpus1_train.labels'
	
if not testListName:
	testListName = 'corpus1_test.list'
	
if not resultName:
	resultName = 'result.txt'

trainList = open(trainListName, 'r')
testList = open(testListName, 'r')
result = open(resultName, 'w')

#Only valid characters in a word are lowercase letters, all words processed into lowercase beforehand
validChar = set(string.ascii_lowercase)

#List of words so common they won't offer useful information in categorization
stoplist = ["a", "about", "above", "above", "across", "after", 
"afterwards", "again", "against", "all", "almost", "alone", "along", 
"already", "also","although","always","am","among", "amongst", 
"amoungst", "amount",  "an", "and", "another", "any","anyhow","anyone",
"anything","anyway", "anywhere", "are", "around", "as",  "at", "back",
"be","became", "because","become","becomes", "becoming", "been", 
"before", "beforehand", "behind", "being", "below", "beside", "besides", 
"between", "beyond", "bill", "both", "bottom","but", "by", "call", "can", 
"cannot", "cant", "co", "con", "could", "couldnt", "cry", "de", "describe", 
"detail", "do", "done", "down", "due", "during", "each", "eg", "eight", 
"either", "eleven","else", "elsewhere", "empty", "enough", "etc", "even", 
"ever", "every", "everyone", "everything", "everywhere", "except", "few", 
"fifteen", "fify", "fill", "find", "fire", "first", "five", "for", "former", 
"formerly", "forty", "found", "four", "from", "front", "full", "further", 
"get", "give", "go", "had", "has", "hasnt", "have", "he", "hence", "her", 
"here", "hereafter", "hereby", "herein", "hereupon", "hers", "herself", 
"him", "himself", "his", "how", "however", "hundred", "ie", "if", "in", 
"inc", "indeed", "interest", "into", "is", "it", "its", "itself", "keep", 
"last", "latter", "latterly", "least", "less", "ltd", "made", "many", "may", 
"me", "meanwhile", "might", "mill", "mine", "more", "moreover", "most", 
"mostly", "move", "much", "must", "my", "myself", "name", "namely", "neither", 
"never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone", 
"nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on", "once", 
"one", "only", "onto", "or", "other", "others", "otherwise", "our", "ours", 
"ourselves", "out", "over", "own","part", "per", "perhaps", "please", "put", 
"rather", "re", "same", "see", "seem", "seemed", "seeming", "seems", 
"serious", "several", "she", "should", "show", "side", "since", "sincere", 
"six", "sixty", "so", "some", "somehow", "someone", "something", "sometime", 
"sometimes", "somewhere", "still", "such", "system", "take", "ten", "than", 
"that", "the", "their", "them", "themselves", "then", "thence", "there", 
"thereafter", "thereby", "therefore", "therein", "thereupon", "these", "they", 
"thickv", "thin", "third", "this", "those", "though", "three", "through", 
"throughout", "thru", "thus", "to", "together", "too", "top", "toward", 
"towards", "twelve", "twenty", "two", "un", "under", "until", "up", "upon", 
"us", "very", "via", "was", "we", "well", "were", "what", "whatever", "when", 
"whence", "whenever", "where", "whereafter", "whereas", "whereby", "wherein", 
"whereupon", "wherever", "whether", "which", "while", "whither", "who", 
"whoever", "whole", "whom", "whose", "why", "will", "with", "within", "without", 
"would", "yet", "you", "your", "yours", "yourself", "yourselves", "the"]

allWords = {} #Dictionary of all words in training set and their frequency
currTestDoc = {} #Dictionary of all words in current testing document and their frequency
numOfAllWords = 0 #Number of all words, including their repitions, in training set
numOfTerms = 0 #Number of all unique terms in training set

cats = {} #List of all categories
probWordCat = {} #Logarithmic probabilities of a word given a category
docCatProb = {} #Logarithmic probabilites that document is in a specific category
probCat = {} #Logarithmic probability of a category

catFiles = {} #List of all category files, each file written with words and frequencies
zeroProbs = {} #Logarithmic probabilities given to words that have zero probablities in a category
WEIGHT = 5 #Weight of tokens in comparison to zero-probability tokens. One token is given WEIGHT+1 per frequency than other tokens 
allWordsFile = open('allWords.txt', 'w')

######################definitely fo real##############################

#Find number of words in a dictionary array
def numOfWords(someDict):
	x = someDict.values()
	return sum(x)

#Remove capitalization/punctuation from tokens
def cleanWord(word):
	word = word.lower()
	li = list(word)
	li = [x for x in li if x in validChar]
	word = "".join(li)
	return word
	
#Add word to dictionaries
def addWord(word, catName,mode):
	word = cleanWord(word)
	
	if not word:
		return 0
	
	if word in stoplist:
		return 0
	
	if mode is 'train':
		if word not in allWords:
			allWords[word] = WEIGHT
		else:
			allWords[word] += WEIGHT
			
		if word not in cats[catName]:
			cats[catName][word] = WEIGHT
		else:
			cats[catName][word] += WEIGHT
	
	else:
		if word not in allWords:
			return 0
		
		if word not in currTestDoc:
			currTestDoc[word] = WEIGHT
		else:
			currTestDoc[word] += WEIGHT
		
	return 1
	
#Open a document and process it
def whatsUpDoc(docName, catName, mode):
	doc = open(docName, 'r')
	
	while 1:
		text = doc.readline()
		if not text:
			break
			
		textTokens = text.split()
		
		if textTokens:
			for word in textTokens:
				addWord(word,catName,mode)
					
#Train program
def trainingMontage():

	#Loop to open documents in training list and process them
	while 1:
		fileAndLabel = trainList.readline()
		if not fileAndLabel:
			break
			
		tokens = fileAndLabel.split()
		if tokens[1] not in cats:
			cats[tokens[1]] = {}
			catFiles[tokens[1]] = open(tokens[1] + ".txt", 'w')
			
		whatsUpDoc(tokens[0], tokens[1], 'train')

	#Find number of all words and all unique terms in training data
	numOfAllWords = numOfWords(allWords)
	numOfTerms = len(allWords)
	
	#Write to file on all words
	allWordsFile.write("Total words: " + str(numOfAllWords) + '\n')
	allWordsFile.write("Total unique terms: " + str(numOfTerms) + '\n')
	for word, num in allWords.items():
		allWordsFile.write(word + ": " + str(num) + '\n')
		
	#Process word and frequency data for each category
	for catName, catWords in cats.items():
		
		#Find number of words in a specific category
		numOfCatWords = numOfWords(catWords)
		
		#Calculate logarithmic zero probabilites, using Laplace smoothing
		zeroProbs[catName] = math.log(1) - math.log(numOfCatWords + numOfTerms)
		
		catFiles[catName].write("Total words: " + str(numOfCatWords) + '\n')
		
		#Find logarithmic probabilites of each category, taking into account Laplace smoothing
		probCat[catName] = math.log(numOfCatWords + numOfTerms)- math.log(numOfAllWords + numOfTerms)
		
		probWordCat[catName] = {}
		docCatProb[catName] = 0
		
		#Find logarithmic conditional probabilties of a word in a given category, with Laplace smoothing
		for word, num in catWords.items():
			wordprob = math.log(num + 1) - math.log(numOfCatWords + numOfTerms)
			probWordCat[catName][word] = wordprob
			catFiles[catName].write(word + ": " + str(num) + ", " + str(wordprob) + '\n')
		
#Use naive Bayes approach
def baseOfKnives():

	#Start calculating log probabilites of a category given document words with log probability of category
	for catName, catProb in probCat.items():
		docCatProb[catName] = catProb
	
	#Add log conditional probabilites of word in given category for all words in document
	for word, num in currTestDoc.items():
		for catName in docCatProb.keys():
			if word in probWordCat[catName]:
				docCatProb[catName] += probWordCat[catName][word] #+ math.log(num)
			else:
				docCatProb[catName] += zeroProbs[catName]
	
	#return category with highest probability
	return max(docCatProb, key = docCatProb.get)
		

#Test program
def testYourMight():
	while 1:
		testFile = testList.readline()
		if not testFile:
			break
			
		tokens = testFile.split()
		
		currTestDoc.clear()
		whatsUpDoc(tokens[0], 'blah', 'test')
		result.write(tokens[0] + " " + baseOfKnives() + '\n')
				
#Train then test program
def wordsWordsWords():
	trainingMontage()
	testYourMight()

##################main##########################################

wordsWordsWords()
