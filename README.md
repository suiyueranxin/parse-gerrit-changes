# parse-gerrit-changes
A small python tool, can be used to map gerrit item to jira issue based on Gerrit APIs and Jira APIs.

# how to run parse.py
1. install dependencies
   pip install -r requirements.txt
2. copy gerrit query from gerrit review url
   take https://git.wdf.sap.corp/q/project:*** for example, query is the part of 'project:orca_***'
3. run parse.py in command line
   parse.py query git-user git-pwd
4. generate a gerrit_to_project.csv to show result and review it by excel
   

# how to run parse.exe
1. open command line
2. print parse.exe query git-user git-pwd
