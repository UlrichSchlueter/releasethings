from github import Github
from datetime import datetime
import yaml
import os,sys


GH_TOKEN_ENV="GH_TOKEN"
config={}
searchlist=[]


def extractTicketLinkFromDescription(pr):    
    if pr.body is None:
        return 
       
    for w in pr.body.split()  :        
            for x in searchlist:
                if x in w:                    
                    return  w          
    return ""  
        

def main():

    if len(sys.argv)<3:
        print("Usage: <startTag> <endTag>")
        exit(2)

    if not GH_TOKEN_ENV in os.environ:
        print (f'ERROR: Environment variable {GH_TOKEN_ENV} not set.')
        exit(4)
        
    with open("gh.config.yaml", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)    
        searchlist=config["searchstrings"]

    gh_token=os.environ.get(GH_TOKEN_ENV)

    g = Github(gh_token)
    repo = g.get_repo(config["repo"])

    tags=repo.get_tags()
    firstTag=sys.argv[1]
    secondTag=sys.argv[2]
    
    found=0
    startcommit=None
    endcommit=None
    for tag in tags:
        if tag.name==firstTag:           
            startcommit=tag.commit            
            found+=1
        elif tag.name==secondTag:            
            endcommit=tag.commit            
            found+=1        
        if found==2:
            break
    
    fail=False
    if startcommit is None:
        print (f'cant find tag:{firstTag}')
        fail=True
    if endcommit is None:
        print (f'cant find tag:{secondTag}')
        fail=True
    if fail:
        exit(8)

   
    startPr=startcommit.get_pulls()[0]    
    endPR=endcommit.get_pulls()[0]
    startTime=startPr.merged_at
    endTime=endPR.merged_at
   
    if startTime>endTime:
        startTime,endTime=endTime,startTime        
    
    pulls = repo.get_pulls(state="all",direction="desc" ,base='master')
    for pr in pulls:
        if pr.number < 2200:
            break  
        if pr.number ==2750:
            pass       
        if pr.merged_at is None:           
            continue
        mergedat=pr.merged_at
        if startTime < mergedat <=endTime:
            print(f'{pr.number},{pr.merged_at},{pr.title},{extractTicketLinkFromDescription(pr)},{pr.user.name}')

   
        

if __name__ == "__main__":
    main()