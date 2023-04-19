from github import Github
from datetime import datetime
import yaml
import os,sys


GH_TOKEN_ENV="GH_TOKEN"
config={}
searchstrings=[]
lowestPRNumber=0


def extractTicketLinkFromDescription(pr):    
    if pr.body is None:
        return 
       
    for w in pr.body.split()  :        
            for x in searchstrings:
                if x in w:                    
                    return  w          
    return ""  


def getStartAndEndTime(tags, firstTag, secondTag):
    startcommit=None
    endcommit=None
    for tag in tags:
            if tag.name==firstTag:           
                startcommit=tag.commit                     
            elif tag.name==secondTag:            
                endcommit=tag.commit                        
            if (not startcommit is None) and (endcommit!=None):
                break
        
    fail=False
    if startcommit is None:
        print (f'cant find tag:{firstTag}')
        fail=True
    if endcommit is None:
        print (f'cant find tag:{secondTag}')
        fail=True
    if fail:
        return None, None


    startPr=startcommit.get_pulls()[0]    
    endPR=endcommit.get_pulls()[0]
    startTime=startPr.merged_at
    endTime=endPR.merged_at

    if startTime>endTime:
        startTime,endTime=endTime,startTime     

    return startTime,endTime


def getStartTime(tags, firstTag):
    startcommit=None
    
    for tag in tags:
            if tag.name==firstTag:           
                startcommit=tag.commit                                                                
                break
            
    if startcommit is None:
        print (f'cant find tag:{firstTag}')
        return None
    
    startPr=startcommit.get_pulls()[0]    
    startTime=startPr.merged_at
   
    return startTime

def main():
    global searchstrings
    if len(sys.argv)<2:
        print("Usage: <startTag> <endTag>")
        exit(2)

    if not GH_TOKEN_ENV in os.environ:
        print (f'ERROR: Environment variable {GH_TOKEN_ENV} not set.')
        exit(4)
        
    with open("gh.config.yaml", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)    
        searchstrings=config["searchstrings"]
        lowestPRNumber=config["lowestPRnumber"]

    gh_token=os.environ.get(GH_TOKEN_ENV)

    g = Github(gh_token)
    repo = g.get_repo(config["repo"])

    tags=repo.get_tags()
    firstTag=sys.argv[1]
    if len(sys.argv)<3:
        secondTag=""
    else:
        secondTag=sys.argv[2]
    
 
    startTime=None
    endTime=None
    if secondTag!="":
        startTime, endTime=getStartAndEndTime(tags, firstTag, secondTag)
        if startTime==None:
            exit(8)
    else:
        endTime=datetime.now()
        startTime =getStartTime(tags, firstTag)
        if startTime==None:
            exit(8)

    
    
    pulls = repo.get_pulls(state="all",direction="desc" ,base='master')
    for pr in pulls:
        if pr.number < lowestPRNumber:
            break    
        if pr.number ==2760:
            pass   
        if pr.merged_at is None:           
            continue
        mergedat=pr.merged_at
        if startTime < mergedat <=endTime:
            print(f'{pr.number},{pr.merged_at},{pr.title},{extractTicketLinkFromDescription(pr)},{pr.user.name}')

   
        

if __name__ == "__main__":
    main()