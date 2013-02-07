import tweepy
import sys
import ast

eFlag = False

def checkTweetsSinceLast(lastIDDict):
  global eFlag
  ### Output setup info
  outputTweets = ""
  ### First check for new tweets since last time for done users:
  for user in lastIDDict.keys():
    try:
        tweets = tweepy.api.user_timeline(user, since_id=lastIDDict[user],count=200)
        if len(tweets) > 0:
          lastIDDict[user] = tweets[0].id
        for tweet in tweets:
          print tweet.text.encode('utf-8')
          outputTweets += tweet.text + "\n"
    except Exception, e:
          print "EXCEPTION THROWN: ",e
          if e.message == "Rate limit exceeded. Clients may not make more than 150 requests per hour.":
            if not eFlag:
              eFlag = True
              print "EXITED IN LASTIDDICT CHECK"
              print "Last User = ",user
              return outputTweets
    return outputTweets
          
def getNewTweets(userList,listNum,userNum,lastIDDict,outFile):
  global eFlag
  if eFlag:
    return ""
  counter =0
  replyIDList = []
  stringTweets = ""
  tweets = []
  loopStop = len(userList)
  loop = 0
  outTweets = ""
  #dir(tweepy.api)
  #exit()
  #print range(userNum,len(userList))
  for num in range(userNum,len(userList)):
    userID = userList[num]
    #print userID
    #print userNum
    #print num
    for i in range (0,4):
      try:
        tweets = tweepy.api.user_timeline(userID, count=200, page=i)
        if i == 0:
          lastIDDict[userID] = tweets[0].id
        for tweet in tweets:
          print tweet.text.encode('utf-8')
          outTweets += tweet.text + "\n"
          counter += 1
      except Exception, e:
          print "EXCEPTION THROWN: ",e,"\nUserID = ",userID
          if e.message == "Rate limit exceeded. Clients may not make more than 150 requests per hour.":
            eFlag = True
            return outTweets.encode('utf-8')
  return outTweets.encode('utf-8')


def main():
  global eFlag
  lastFileName = sys.argv[1]
  lastFile = open(lastFileName,'r')
  lastContents = lastFile.readlines()
  lastFile.close()
  listNum = int(lastContents[0])
  userNum = int(lastContents[1])
  nullChecker = lastContents[2]
  outputTweets = ""
  outNum = int(lastFileName[10:-4])+1
  print outNum
  outFile = open("NewsTweets"+str(outNum)+".txt",'wb')
  #print nullChecker
  if nullChecker != "None" and nullChecker != "None\n" and nullChecker != '{}\n':
    lastIDDict = ast.literal_eval(lastContents[2])
    try:
      outputTweets += str(checkTweetsSinceLast(lastIDDict))
    except Exception, e:
      print e
    if eFlag:
      print >> outFile, listNum
      print >> outFile, userNum
      print >> outFile, lastIDDict
      print >> outFile, outputTweets
      outFile.close()
      exit()
  else:
    lastIDDict = {}
  #print str(lastIDDict)


  

 
  #recentIds = open("RecentIds.txt",'wb')
  userList = ['CNN','CNNNewsroom','nytimes','nytimeskrugman','nytimespolitics','nytimesworld','nytimeshealth','nytimestravel','nytimesscience']
  userList2 = ['nytimesbusiness','nickkristof','wsj','washingtonpost','latimes','usatoday','newyorkpost','chicagotribune','denverpost','dallas_news','seattletimes','suntimes','freep','nydailynew','houstonchron','azcentral','oregonian','phillyinquirer','sfgate','clevelanddotcom','MN_News','NJ_News','SDUT','tampabaycom','insidebayarea','cctimes','mercurynews','newsday']
  ul3 = ['man','msn_money','ap','ap_politics','apstylebook','ap_top25','ap_retail','ap_interactive','ap_personalfin','ap_country','ap_travel','ap_nfl','ap_lifestyles','ap_video','ap_courtside','ap_fashion','ap_courtside']
  ul4 = ['maddow','huffingtonpost','senJeffMerkley','alfranken','secnav','theeconomist','slate','miamiherald','njhotline','billgates','CM_MargaretChin','StephenLevin33','NY1headlines']
  ul5 = ['JansingCo','NRCGov','CraigatFEMA','alroker','NBCConnecticut','NOAA','senatorreid']
  ul6 = ['deanheller','orrinhatch','johnensign','senarienspecter','senjohnmccain','repmikepence','sensanders','senbobcorker','repmaryfallin','chuckgrassley','dennis_kucinich']
  ul7 = ['PeopleMag','Time','InStyle','WomensWearDaily','EW','LIFE','Newsweek','GoodHealth','Wired']
  ul8=['TVGuide','StyleWatchMag','Good','ElleMagazine','TheEconomist','Teen_Vogue']
  ul9 =['NewYorker','NatGeoSociety','HarvardBiz','SI_24seven','UsWeekly','NylonMag','MarieClaire','WMag','HarpersBazaarUS','FastCompany']
  ul10 = ["AP", "washingtonpost", "digg", "nbcwashington", "ABC7news", "WTOP", "breakingweather", "HuffPostDC", "weatherchannel", "TWCbreaking", "ABC7", "ABC", "abc15", "abc7newsBayArea", "BreakingNews", "WestWingReport", "washingtonian", "Atlantic_LIVE", "FairfaxTimes", "dcexaminerlocal"]
  ul11 = ["WTTGMORNINGNEWS", "FoxNews", "twc_hurricane", "wired", "TIME", "peoplemag", "WSJpersfinance", "WSJusnews", "nypost", "daily", "FoxNewsLive", "WSJ", "msnbc_breaking", "NBCNewsPictures", "NBCNewsUS", "nbcnightlynews", "todayshow", "NBCNewsEnt", "meetthepress", "datelinenbc"]
  ul12 = ["AP_Mobile", "dcexaminer", "nationalpost", "PoliticalTicker", "NewYorker", "fivethirtyeight", "Gallerist_NY", "politico44", "ForeignPolicy", "TIMEThePage", "NY1headlines", "NYT_Arts", "villagevoice", "NYMag", "tnygoingson", "cnnmornings", "CNBC", "CBSThisMorning", "CBSNews", "washingtonweek"]
  ul13 = ["Nightline", "GMA", "Slate", "CFR_org", "TheEconomist", "TPM", "thedailybeast", "usnews", "HuffingtonPost", "politico", "nprnews", "thecaucus", "nytimesarts", "PhillyInquirer", "CIRonline", "CNN", "ThePhillyPost", "WSJbreakingnews", "philly311", "politifact", "njspotlight"]
  ul14 = ["wcp", "citypaper", "PassyunkPost", "6abc", "TheKeyXPN", "KYWNewsradio", "MotherJones", "PhillyTrib", "cnnbrk", "cnnhealth", "myfoxdc", "FedNewsRadio", "quartznews", "adndotcom", "ARLnowDOTcom", "HuffPostPol", "latimes", "NBCFirstRead", "TechNewsDaily", "seattletimes"]
  ul15 = ["seattletimes", "PopSci", "Reuters", "GuardianUS", "thenation", "DailyCaller", "EconUS", "postlive", "Techmeme", "Newsweek", "roanoketimes", "pgpolitics", "metroweekly", "HuffPostSF", "HuffPostLA", "HuffPostDetroit", "HuffPostDenver", "NBCPhiladelphia", "LansReporter", "HaverfordPatch"]

  allUserLists=[userList,userList2,ul3,ul4,ul5,ul6,ul7,ul8,ul9,ul10,ul11,ul12,ul13,ul14,ul15]

  
  ### Continue from where last left off
  while ((not eFlag) and (listNum < len(allUserLists))):
    outputTweets += getNewTweets(allUserLists[listNum],listNum,userNum,lastIDDict,outFile)
    if not eFlag:
      listNum += 1
      userNum = 0

  if not eFlag:
    print >> outFile, listNum
    print >> outFile, userNum
  print >> outFile, lastIDDict
  print >> outFile, outputTweets

  outFile.close()




if __name__ == '__main__':
  if len(sys.argv) < 2:
    print "Usage: python newsDownloadTest.py <LAST FILE>"
    exit()
  main()
