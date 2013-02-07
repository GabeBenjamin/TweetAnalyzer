import sys
from tweepy.utils import import_simplejson, urlencode_noplus
json = import_simplejson()

file = open(sys.argv[1],'r')
content = file.readlines()
file.close()
out = open(sys.argv[1][:-4]+'_LINES.txt','wb')
for i,line in enumerate(content):
  if i > 100000:
    break
  else:
    try:
      tweetDict = json.loads(line)
      print >> out, tweetDict['text'].encode('utf-8')
    except Exception,e:
      print "EXCEPTION THROWN: ",e

out.close()
  
