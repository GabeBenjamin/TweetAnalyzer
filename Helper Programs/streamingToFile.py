from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from datetime import datetime
import codecs
import sys
from tweepy.utils import import_simplejson, urlencode_noplus
json = import_simplejson()
# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after
consumer_key="zfT8EphApqvOiGSrEE04w"
consumer_secret="6yNkBHl10XnFyCBkAh8tr8Qy6JIQx5UAiPCFeAV7M"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="16196742-19x5pD4zsfXZASczzeih4Aod0UUBvbYVv1jG7KUD5"
access_token_secret="fZLBcmDJNQWksKkApvVwHkn969GmFjJUil5aIVHo"
search = ""
fileName = ""
class StdOutListener(StreamListener):
        
       
	""" A listener handles tweets are the received from the stream. 
	This is a basic listener that just prints received tweets to stdout.

	"""
	def on_data(self, data):
                myFile = open(fileName,'a')
                #status = Status.parse(self.api, json.loads(data))
                #print >> myFile, "TEST"
                myStr = ""
		#print  data, "\n"
                myDict = json.loads(data)
                
                if 'entities' not in myDict:
                        print "ERROR -- NO ENTITIES"
                elif len(myDict['entities']['hashtags']) > 0:
                        print >> myFile, data.encode("utf-8")
                        print myDict['text'].encode("utf-8")
                        """
                        myStr = "Tweet:\n" + myDict['text']
                        myStr += "\nHashTags:"
                        for hashtag in myDict['entities']['hashtags']:
                                myStr += hashtag['text']
                        #print "HashTags:\n",myDict['entities']['hashtags']['text']
                        myStr += "\n"
                        print myStr
                        #content = unicode(myStr.strip(codecs.BOM_UTF8), 'utf-8')
                        print >> myFile, myStr.encode("utf-8")
                        #if 'hashtags' in myDict:
        #                        print "HashTags:\n",myDict['hashtags']
                        #print >> myFile, "TEST\n", dict(data)
                        """
                        myFile.close()
                        
                
		return True
        def on_status(status):
                print "STATUS"

	def on_error(self, status):
		print status
        #myFile.close()

if __name__ == '__main__':
	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
        stream = Stream(auth, l)
        if len(sys.argv) < 2:
          fileName = "AllTweets.txt"
          stream.sample()
        elif sys.argv[1] == '1':
          fileName = "HappyEmoAll.txt"
          stream.filter(track=[':-)',':)','=)',':D'])
        elif sys.argv[1] == '2':
          fileName = "SadEmoAll.txt"
          stream.filter(track=[':-(',':(','=(',';('])
        
        else:
          search = sys.argv[1]
          #serach = "#" + search 
          fileName = search + ".txt"
          stream.filter(track=[search],locations=[-124.848974, 24.396308,-66.885444, 49.384358])
