# releasethings



Expects 
- env variable GH_TOKEN to contain a valid Github token (https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) 
- env variable JIRA_TOKEN to contain a valid Jira token (https://issues.redhat.com/secure/ViewProfile.jspa)
- a file called `gh.config.yaml` to contain repo and url search strings (see the example file)

Run with

`python gh.py <tag1> <tag2> `

or 

`python gh.py <a single tag>`

and the fun starts