
import sys
import os
import cPickle
import re
from datetime import datetime
import operator
from math import log10
import nltk
import random

#pickleLoc = '/scratch/gbenjam1/TweetProbabilities'
pickleLoc = 'TweetProbabilities'
NGRAMS = 1
TRAINNUM = 50000
LINECUT = 60000
ALPHA = 1.0
SCORE_THRESH = -10000.0
PROJECT_HOME = ''

UNKGRAM = '__UNKNOWN_GRAM__'
SENSE_HAPPY = 0
SENSE_SAD = 1
SENSE_NEUTRAL = 2
SENSE_NOGUESS = 5



happyCFile = ""
happyTagFile = ""
sadCFile = ""
sadTagFile = ""
neutralCFile = ""
neutralTagFile = ""

happyP = {}
happyTagP = {}
sadP = {}
sadTagP = {}
neutralP = {}
neutralTagP = {}

testHappyTweets = []
testHappyTags = []
testSadTweets = []
testSadTags = []
testNeutralTweets = []
testNeutralTags = []

def tagFileToList(tagLines):
  tagList = []
  for line in tagLines:
    lineList = line.split('\t')
    tagList.append(lineList[1])

  return tagList
    
"""
**********************************************************
*******************Tweet Cleaning Methods*****************
**********************************************************
"""

"""
Determines if word is an emoticon
"""
def wordIsEmoticon(word):
  result = re.search(r':\)|:-\)|=\)|:D|:|:\(|:-\(|=\(|;\(|;|=',word)
  if result:
    return True
  return False

"""
Determines if word is a url
"""
def wordIsURL(word):
  result = re.search(r'http://|www\.',word)
  if result:
    return True
  return False

"""
Determines if word is @xxx or 'RT'
"""
def wordIsAt(word):
  result = re.search(r'\b@.*\b|RT',word)
  if result:
    return True
  else:
    return False


def isStopWord(word):
  return False #DON"T USE
  if word == 'the' or word == 'a' or word == 'an':
    return True
  return False




"""
**********************************************************
***********************N-Gram Methods*********************
**********************************************************
"""


"""
Take in tweets and output list of unigrams
"""
def toUnigrams(lines):
  #print "LINES: ", len(lines)
  startTime = datetime.now()
  num = 0.0
  total = len(lines)
  uniwords = []
  for line in lines:
    words = line.split()
    for i in range(0,len(words)-1):
      now = datetime.now()
      if (now-startTime).total_seconds() > 2:#(now.second*1000000+now.microsecond)-(startTime.second*1000000+startTime.microsecond) >= 2000000:
            print str((num/total)*100)+"%"
            startTime = datetime.now()
      if isStopWord(words[i]):
        break
      """Check to make sure word/nextW are not ',' or '.'"""
      word = re.sub(r',|\.','',words[i]).lower()
      nextW = re.sub(r',|\.','',words[i+1]).lower()
      
      """Check to make sure not emoticon, url or @xxx/RT"""
      if not wordIsURL(word) and not wordIsAt(word) and not wordIsEmoticon(word):
        if word == "not" or word == "no":
                uniwords.append(word+"+"+nextW)
                i += 1
                #print str(word+"+"+nextW)
        elif nextW == "not" or nextW == "no":
                uniwords.append(word+"+"+nextW)
                #print str(word+"+"+nextW)
                
        else:
                uniwords.append(word)
    #print words
    num += 1.0
  return uniwords

"""
Take in tweets and output list of bigrams
"""
def toBigrams(lines):
  words = toUnigrams(lines)
  biwords = []
  for i in range(0,len(words)-1):
    bigram = words[i]+" "+words[i+1]
    biwords.append(bigram)
    
  #print biwords
  return biwords


"""
Take in tweets and output list of Trigrams
"""
def toTrigrams(lines):
  words = toUnigrams(lines)
  triwords = []
  for i in range(0,len(words)-2):
    trigram = words[i]+" "+words[i+1]+" "+words[i+2]
    triwords.append(trigram)
    
  #print biwords
  return triwords






"""
Takes in tweets (text, one per line) and creates probabilities for ngrams
"""
def createProbabilitiesFromTweets(lines,n):
  
  """First break tweets into n grams"""

  if n == -1:
    gramList = toTagUnigrams(lines)
  else:
    gramList = toUnigrams(lines)


  """Count up all the grams"""
  numgrams = len(gramList)
  countD = {}
  for gram in gramList:
    if gram in countD:
      countD[gram] += 1.0
    else:
      countD[gram] = 1.0


  """Now create probabilities based on counts"""
  """Also do add one smoothing"""
  probD = {}
  for key in countD.keys():
    probD[key] = ((countD[key]+ALPHA)/(numgrams+ALPHA*numgrams))

  probD[UNKGRAM] = ALPHA/(numgrams+ALPHA*numgrams)

  
  if NGRAMS > 1:
    bigramP = {}
    bcountD = {}
    if n == -1:
      bigrams = toTagBigrams(lines)
    else:
      bigrams = toBigrams(lines)
    numbigrams = len(bigrams)
    for bigram in bigrams:
      if bigram in bcountD:
        bcountD[bigram] += 1.0
      else:
        bcountD[bigram] = 1.0
    for key in bcountD.keys():
      split = key.split()
      try:
        bigramP[key] = (bcountD[key])/(countD[split[0]])
      except Exception, e:
        print "227"
        print e, split, key
    bigramP[UNKGRAM] = probD
    if NGRAMS == 2:
      return bigramP

  if NGRAMS == 3:
    trigramP = {}
    tcountD = {}
    if n == -1:
      trigrams = toTagTrigrams(lines)
    else:
      trigrams = toTrigrams(lines)
    numtrigrams = len(trigrams)
    for trigram in trigrams:
      if trigram in tcountD:
        tcountD[trigram] += 1.0
      else:
        tcountD[bigram] = 1.0
    for key in tcountD.keys():
      split = key.split()
      try:
        bigram = split[0]+" "+split[1]
        trigramP[key] = (tcountD[key])/(bcountD[bigram])
      except Exception, e:
        print "227"
        print e, split, key
    trigramP[UNKGRAM] = bigramP
    return trigramP
    
      
    
  return probD


def getSenseForTweet(tweet,tags,probs,tagPs):
  gramList = []
  tweetbackoff1 = None
  tweetbackoff2 = None
  tagbackoff1 = None
  tagbackoff2 = None
  if NGRAMS == 3:
    gramList = toTrigrams([tweet])
  elif NGRAMS == 2:
    gramList = toBigrams([tweet])
    
  else:
    gramList = toUnigrams([tweet])
  
  tagsList = tags.split()

  maxScore = -1000000000
  score = 0
  choice = -1
  for i,probD in enumerate(probs):
    score = 0
    tagP = tagPs[i]
    if NGRAMS == 2:
      try:
        tweetbackoff1 = probD[UNKGRAM]
        tagbackoff1 = tagP[UNKGRAM]
      except Exception,e:
        print "264"
        print e,"\n",tagP,i
    elif NGRAMS == 3:
      try:
        tweetbackoff2 = probD[UNKGRAM]
        tagbackoff2 = tagP[UNKGRAM]
        tweetbackoff1 = tweetbackoff2[UNKGRAM]
        tagbackoff1 = tagbackoff2[UNKGRAM]
      except Exception,e:
        print "264"
        print e,"\n",tagP,i
    for gram in gramList:
      if gram in probD:
        #print "trigram"
        temp = log10((probD[gram]))
        #print temp
        score += temp
      else:
        if isinstance(probD[UNKGRAM],dict):
          #print "BACKOFF TO BIGRAM"
          split = gram.split()
          if tweetbackoff2 != None and len(split) == 3:
            bigram = split[1]+" "+split[2]
            if bigram in tweetbackoff2:
              #print "backoff bigram"
              score += log10(tweetbackoff2[bigram])
            else:
              split = bigram.split()
          if tweetbackoff1 != None and len(split) == 2:
            #print gram
            #print "BACKOFF TO UNIGRAM"
            if split[1] in tweetbackoff1:
              score += log10(tweetbackoff1[split[1]])
            else:
              score += log10(tweetbackoff1[UNKGRAM])
        else:
          try:
            score += log10(probD[UNKGRAM])
          except Exception,e:
            print gram,e
    #print score
    
    for tag in tagsList:
      if tag in tagP:
        temp = log10(tagP[tag])
        #print temp
        score += temp
      else:
        if isinstance(probD[UNKGRAM],dict):
          split = tag.split()
          #print "BACKOFF TAG"
          if tagbackoff2 != None and len(split) == 3:
            bigram = split[1]+" "+split[2]
            if bigram in tweetbackoff2:
              #print "backoff bigram"
              score += log10(tweetbackoff2[bigram])
            else:
              split = bigram.split()
          if tagbackoff1 != None and len(split) == 2:
            #print gram
            #print "BACKOFF TO UNIGRAM"
            if split[1] in probD[UNKGRAM]:
              score += log10(tagbackoff1[split[1]])
            else:
              score += log10(tagbackoff1[UNKGRAM])
        else:
          score += log10(tagP[UNKGRAM])
        #print "NO TAG"

    #print score
    if score > maxScore:
      choice = i
      maxScore = score
  #print maxScore
  if maxScore < SCORE_THRESH:
    choice = SENSE_NOGUESS
  return (choice,maxScore)


"""
**********************************************************
***********************Tagging Methods**********************
**********************************************************
"""
def toTagUnigrams(lines):
  print "LINES: ", len(lines)
  startTime = datetime.now()
  num = 0.0
  total = len(lines)
  uniwords = []
  for line in lines:
    words = line.split()
    for word in words:
      now = datetime.now()
      if (now-startTime).total_seconds() > 1:
            print str((num/total)*100)+"%"
            startTime = datetime.now()
      uniwords.append(word)
    num += 1.0

  words = uniwords
  
  return uniwords


def toTagBigrams(lines):
  words = toTagUnigrams(lines)
  biwords = []
  for i in range(0,len(words)-1):
    bigram = words[i]+" "+words[i+1]
    biwords.append(bigram)

  return biwords

def toTagTrigrams(lines):
  words = toUnigrams(lines)
  triwords = []
  for i in range(0,len(words)-2):
    trigram = words[i]+" "+words[i+1]+" "+words[i+2]
    triwords.append(trigram)
    
  #print biwords
  return triwords

    
"""
**********************************************************
***********************Other Methods**********************
**********************************************************
"""

def randomizeTweets(tweets,seed):#(numItems,largeSplit):
  random.seed(seed)
  random.shuffle(tweets)
  
  
"""
**********************************************************
*******************File Handling Methods******************
**********************************************************
"""

def pickleExists(i):
  if os.path.exists(pickleLoc+str(NGRAMS)+"_"+str(i)+'.pkl'):
    return True
  return False

def openPickle(i):
  global happyP
  global happyTagP
  global sadP
  global sadTagP
  global neutralP
  global neutralTagP

  global testHappyTweets
  global testHappyTags
  global testSadTweets
  global testSadTags
  global testNeutralTweets
  global testNeutralTags
  
  """
  Load probabilities from pickle
  """

  pickleInput = open(pickleLoc+str(NGRAMS)+"_"+str(i)+'.pkl','r')

  happyP = cPickle.load(pickleInput)
  happyTagP = cPickle.load(pickleInput)
  sadP = cPickle.load(pickleInput)
  sadTagP = cPickle.load(pickleInput)
  neutralP = cPickle.load(pickleInput)
  neutralTagP = cPickle.load(pickleInput)

  pickleInput.close()

  """
  Open the files of tweets
  """
  happyCFile = open(happyCFileName,'r')
  happyTagFile = open(happyTagFileName,'r')
  sadCFile = open(sadCFileName,'r')
  sadTagFile = open(sadTagFileName,'r')
  neutralCFile = open(neutralCFileName,'r')
  neutralTagFile = open(neutralTagFileName,'r')

  happyCLines = happyCFile.readlines()
  happyTagLines = happyTagFile.readlines()
  sadCLines = sadCFile.readlines()
  sadTagLines = sadTagFile.readlines()
  neutralCLines = neutralCFile.readlines()
  neutralTagLines = neutralTagFile.readlines()

  happyCFile.close()
  happyTagFile.close()
  sadCFile.close()
  sadTagFile.close()
  neutralCFile.close()
  neutralTagFile.close()

  
  """Randomize lines for seed"""
  seed = i*12

  randomizeTweets(happyCLines,seed)
  randomizeTweets(happyTagLines,seed)
  randomizeTweets(sadCLines,seed)
  randomizeTweets(sadTagLines,seed)
  randomizeTweets(neutralCLines,seed)
  randomizeTweets(neutralTagLines,seed)

  """TEMP: CUT CORPI TO LINECUT"""
  happyCLines = happyCLines[:LINECUT]
  happyTagLines = happyTagLines[:LINECUT]
  sadCLines = sadCLines[:LINECUT]
  sadTagLines = sadTagLines[:LINECUT]
  neutralCLines = neutralCLines[:LINECUT]
  neutralTagLines = neutralTagLines[:LINECUT]


  """Break into training and test"""

  testHappyTweets = happyCLines[TRAINNUM:]
  testHappyTags = happyTagLines[TRAINNUM:]
  testSadTweets = sadCLines[TRAINNUM:]
  testSadTags = sadTagLines[TRAINNUM:]
  testNeutralTweets = neutralCLines[TRAINNUM:]
  testNeutralTags = neutralTagLines[TRAINNUM:]

def createPickle(i):
  global happyP
  global happyTagP
  global sadP
  global sadTagP
  global neutralP
  global neutralTagP

  global testHappyTweets
  global testHappyTags
  global testSadTweets
  global testSadTags
  global testNeutralTweets
  global testNeutralTags
  """
  Else, create the probabilities for each corpus
  """
  """
  Open the files of tweets
  """
  happyCFile = open(happyCFileName,'r')
  happyTagFile = open(happyTagFileName,'r')
  sadCFile = open(sadCFileName,'r')
  sadTagFile = open(sadTagFileName,'r')
  neutralCFile = open(neutralCFileName,'r')
  neutralTagFile = open(neutralTagFileName,'r')

  happyCLines = happyCFile.readlines()
  happyTagLines = happyTagFile.readlines()
  sadCLines = sadCFile.readlines()
  sadTagLines = sadTagFile.readlines()
  neutralCLines = neutralCFile.readlines()
  neutralTagLines = neutralTagFile.readlines()

  happyCFile.close()
  happyTagFile.close()
  sadCFile.close()
  sadTagFile.close()
  neutralCFile.close()
  neutralTagFile.close()


  """Randomize lines for seed"""
  seed = i*12

  randomizeTweets(happyCLines,seed)
  randomizeTweets(happyTagLines,seed)
  randomizeTweets(sadCLines,seed)
  randomizeTweets(sadTagLines,seed)
  randomizeTweets(neutralCLines,seed)
  randomizeTweets(neutralTagLines,seed)

  """TEMP: CUT CORPI TO LINECUT"""
  happyCLines = happyCLines[:LINECUT]
  happyTagLines = happyTagLines[:LINECUT]
  sadCLines = sadCLines[:LINECUT]
  sadTagLines = sadTagLines[:LINECUT]
  neutralCLines = neutralCLines[:LINECUT]
  neutralTagLines = neutralTagLines[:LINECUT]

  """Break into training and test"""
  trainLinesH = happyCLines[:TRAINNUM]
  trainTagH = happyTagLines[:TRAINNUM]
  trainLinesS = sadCLines[:TRAINNUM]
  trainTagS = sadTagLines[:TRAINNUM]
  trainLinesN = neutralCLines[:TRAINNUM]
  trainTagN = neutralTagLines[:TRAINNUM]

  testHappyTweets = happyCLines[TRAINNUM:]
  testHappyTags = happyTagLines[TRAINNUM:]
  testSadTweets = sadCLines[TRAINNUM:]
  testSadTags = sadTagLines[TRAINNUM:]
  testNeutralTweets = neutralCLines[TRAINNUM:]
  testNeutralTags = neutralTagLines[TRAINNUM:]
  
  print ("******\nCREATING HAPPY\n*****")
  happyP = createProbabilitiesFromTweets(trainLinesH,NGRAMS)
  
  print ("******\nCREATING HAPPY Tags\n*****")
  happyTagP = createProbabilitiesFromTweets(trainTagH,-1)

  print ("******\nCREATING SAD\n*****")
  sadP = createProbabilitiesFromTweets(sadCLines[:TRAINNUM],NGRAMS)
  print ("******\nCREATING Sad Tags\n*****")
  sadTagP = createProbabilitiesFromTweets(trainTagS,-1)

  print ("******\nCREATING Neutral\n*****")
  neutralP = createProbabilitiesFromTweets(neutralCLines[:TRAINNUM],NGRAMS)
  print ("******\nCREATING Neutral Tags\n*****")
  neutralTagP = createProbabilitiesFromTweets(trainTagN,-1)

  """
  Store probabilities using cPickle
  """
  pickleOutput = open(pickleLoc+str(NGRAMS)+"_"+str(i)+'.pkl','wb')

  cPickle.dump(happyP,pickleOutput,-1)
  cPickle.dump(happyTagP,pickleOutput,-1)
  cPickle.dump(sadP,pickleOutput,-1)
  cPickle.dump(sadTagP,pickleOutput,-1)
  cPickle.dump(neutralP,pickleOutput,-1)
  cPickle.dump(neutralTagP,pickleOutput,-1)

  pickleOutput.close()



"""
**********************************************************
***********************Main Methods**********************
**********************************************************
"""
def main():
  """
  global ALPHA
  if len(sys.argv) == 2:
    ALPHA = float(sys.argv[1])/10
  """
  #print "NGRAMS = ", NGRAMS
  percentTotal = 0.0
  for i in range(5):
    if pickleExists(i):
      openPickle(i)
    else:
      createPickle(i)

    correct = 0
    total = 0
    noguess = 0

    probs = [happyP,sadP,neutralP]
    tagPs = [happyTagP,sadTagP,neutralTagP]
    avgGoodScore = 0
    
    #print "TEST HAPPY: ",len(testHappyTweets)
    for i,tweet in enumerate(testHappyTweets):
      (sense,score) = getSenseForTweet(tweet,testHappyTags[i],probs,tagPs)
      if sense == SENSE_HAPPY:
        correct += 1
        avgGoodScore += score
      elif sense == SENSE_NOGUESS:
        noguess += 1
      #else:
        #print tweet,sense
      total += 1

    
    
    
    #print "TEST SAD: ",len(testSadTweets)
    for i,tweet in enumerate(testSadTweets):
      (sense,score) = getSenseForTweet(tweet,testSadTags[i],probs,tagPs)
      if sense == SENSE_SAD:
        correct += 1
        avgGoodScore += score
      total +=1
    
  
       
    #print "TEST NEUTRAL: ",len(testNeutralTweets)
    for i,tweet in enumerate(testNeutralTweets):
      (sense,score) = getSenseForTweet(tweet,testNeutralTags[i],probs,tagPs)
      if sense == SENSE_NEUTRAL:
        correct += 1
        avgGoodScore += score
      total +=1
    
    percent = (float(correct)/total*100)
    percentTotal += percent
    print "%Correct = ", percent
    #print "%Precision = ", ((float(correct)/(total-noguess))*100)
    #print "NOGUESS = ", noguess
    #print "AVG SCORE = ", avgGoodScore/float(correct)
  
  print "Average = %", (percentTotal/5)


  return 0




















if __name__ == '__main__':
  if len(sys.argv) == 1 or len(sys.argv) == 2:
    happyCFileName = 'HappyTweets/HappyTweets.txt'
    happyTagFileName = PROJECT_HOME+'HappyTweets/HappyTags.txt'
    sadCFileName = PROJECT_HOME+'SadTweets/SadTweets.txt'
    sadTagFileName = PROJECT_HOME+'SadTweets/SadTags.txt'
    neutralCFileName = PROJECT_HOME+'NeutralTweets/NeutralTweets.txt'
    neutralTagFileName = PROJECT_HOME+'NeutralTweets/NeutralTags.txt'
  
  elif len(sys.argv) < 7:
    print "Usage: python tweetAnalyzer.py <HAPPY CORPUS> <SAD CORPUS> <NEUTRAL CORPUS>"
    exit()
  else:
    happyCFileName = sys.argv[1]
    happyTagFileName = sys.argv[2]
    sadCFileName = sys.argv[3]
    sadTagFileName = sys.argv[4]
    #neutralCFileName = sys.argv[5]
    #neutralTagFileName = sys.argv[6]
    
  main()
