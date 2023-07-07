from github import Github
from datetime import datetime
import yaml
import os,sys
from jira import JIRA

GH_TOKEN_ENV="GH_TOKEN"
JIRA_TOKEN_ENV="JIRA_TOKEN"
config={}
searchstrings=[]
lowestPRNumber=0


def extractTicketLinkFromDescription(pr):    
    if pr.body is None:
        return 

    charsToRemove="[]()"
    replaceWith=" " * len(charsToRemove)
    transtable = str.maketrans(charsToRemove, replaceWith)  
    convertedText=pr.body.translate(transtable)
    for w in convertedText.split() :        
            for x in searchstrings:
                if x in w:                    
                    return  w          
    return ""  

def isARO(ticketlink):
    if "/ARO-" in ticketlink:
        return True
    return False

def extractAROTicketNumber(ticketlink):
    link=ticketlink.translate({ord(i): None for i in '()'})    
    aro=""
    index=link.find("/ARO-")
    if index != -1:
        aro=link[index+1:]
    return aro

def getJiraTicket(connection,ticket):
    try:
        issue = connection.issue(ticket)
    except Exception as e:
        print (e)
        return None
    return issue

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


def getJiraTicker(ticket):

    jira_token=os.environ.get(JIRA_TOKEN_ENV)

    # By default, the client will connect to a Jira instance started from the Atlassian Plugin SDK
    # (see https://developer.atlassian.com/display/DOCS/Installing+the+Atlassian+Plugin+SDK for details).
    jira = JIRA(server="https://issues.redhat.com",
            token_auth=jira_token)

    issue = jira.issue(ticket)
    return issue

def main():
    global searchstrings
    if len(sys.argv)<2:
        print("Usage: <startTag> <endTag>")
        exit(2)

    if not GH_TOKEN_ENV in os.environ:
        print (f'ERROR: Environment variable {GH_TOKEN_ENV} not set.')
        exit(4)

    if not JIRA_TOKEN_ENV in os.environ:
        print (f'ERROR: Environment variable {JIRA_TOKEN_ENV} not set.')
        exit(4)
        
    with open("gh.config.yaml", "r") as ymlfile:
        config = yaml.safe_load(ymlfile)    
        searchstrings=config["searchstrings"]
        lowestPRNumber=config["lowestPRnumber"]

    gh_token=os.environ.get(GH_TOKEN_ENV)
    jira_token=os.environ.get(JIRA_TOKEN_ENV)

    g = Github(gh_token)
    jira = JIRA(server="https://issues.redhat.com",
            token_auth=jira_token)




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
        if pr.number ==2693:
            pass   
        if pr.merged_at is None:           
            continue
        mergedat=pr.merged_at
        jira_state=""
        jira_gh_link=""
        jira_assignee=""        
        if startTime < mergedat <=endTime:
            ticketlink=extractTicketLinkFromDescription(pr)
            if isARO(ticketlink):
                aroticket=extractAROTicketNumber(ticketlink)
                ticket=getJiraTicket(jira, aroticket)
                if ticket is not None:
                    jira_state=ticket.fields.status
                    jira_assignee=ticket.fields.assignee.displayName                
                    if ticket.fields.customfield_12310220 is not None:
                        for link in ticket.fields.customfield_12310220:
                            jira_gh_link=jira_gh_link+" "+link
                else:
                    jira_state=""
                    jira_assignee=""
                    jira_gh_link=""
                # <customfield id="customfield_12310220" key="org.jboss.labs.jira.plugin.jboss-custom-field-types-plugin:multiurl">
                #<customfieldname>Git Pull Request</customfieldname>
                #<customfieldvalues> https://invalid.uli </customfieldvalues>
                #</customfield>
                pass
            title=pr.title.replace(","," ")
            
            print(f'{pr.number},{pr.merged_at},{title},{ticketlink},{pr.user.name},{jira_state},{jira_assignee},{jira_gh_link}')

   
        

if __name__ == "__main__":
    main()