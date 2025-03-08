# pulls all Issue data from Jira
# tokens come from here: https://id.atlassian.com/manage-profile/security/api-tokens

import requests
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
# decided to use JIRA lib for issue history ...
from jira import JIRA

G_Fields = [
    {"Field":"ProjectName",  "Path":["fields","project","name"]},
    {"Field":"Team",        "Path":["fields","customfield_10001","name"]},
    {"Field":"ID",          "Path":["id"]},
    {"Field":"Key",         "Path":["key"]},
    {"Field":"Created",    "Path":["fields","created"]},
    {"Field":"Creator",    "Path":["fields","creator","displayName"]},
    {"Field":"Reporter",    "Path":["fields","reporter","displayName"]},
    {"Field":"Assignee",    "Path":["fields","assignee","displayName"]},
    {"Field":"Status",      "Path":["fields","status","name"]},
    {"Field":"Priority",    "Path":["fields","priority","name"]},
    {"Field":"Category",    "Path":["fields","customfield_10078","value"]},
    {"Field":"Summary",    "Path":["fields","summary"]},
    {"Field":"Description", "Path":["fields","description"]},
    {"Field":"Group",       "Path":["fields","customfield_10046","value"]},
    {"Field":"Site",        "Path":["fields","customfield_10045[0]","value"]},
    {"Field":"DueDate",      "Path":["fields","duedate"]},
    {"Field":"WatcherURL",   "Path":["fields","watches","self"]}
]
class BAJiraHelper():
    def __init__(self,pConfig,pLogger):
        self.aConfig = pConfig
        self.aLogger = pLogger
        self.aLogger.debug("BAJiraHelper.init")
        self.aUser = self.aConfig.getParm("Jira.User")
        self.aToken = self.aConfig.getParm("Jira.Token")
        self.aServer = self.aConfig.getParm("Jira.Server")
        self.aFilter = "project=" + self.aConfig.getParm("Jira.Project") + " and created>=<CreatedDate>"

        self.aTeam = self.aConfig.getParm("Jira.Team")

    def getIssuesCreatedAfterDF(self,pStartDate):
        self.aLogger.info("getIssues.Start")
        sFilter = self.aFilter.replace("<CreatedDate>",pStartDate)

        auth = HTTPBasicAuth(self.aUser, self.aToken)
        dHeaders = {"Accept": "application/json"}
        iStart = 0
        iChunk = self.aConfig.getParmDefault("Jira.Chunk", 100)
        iTotal = 10
        lFinal = []
        sURL = self.aConfig.getParm("Jira.URL")
        self.aLogger.debug(sURL + ":" + self.aFilter)
        while iStart <= iTotal:
            self.aLogger.debug("starting with record: " + str(iStart))
            dQuery = {'jql': sFilter, "startAt": iStart, "maxResults": iChunk}
            response = requests.request("GET", sURL, headers=dHeaders, auth=auth, params=dQuery)
            # self.aLogger.info("response:"+response)
            print(f"response:{response}")
            iTotal = json.loads(response.text)["total"]
            lIssues = json.loads(response.text)["issues"]
            lFinal = lFinal + lIssues
            self.aLogger.debug("Total is: " + str(iTotal) + ", running total is: " + str(len(lFinal)))
            iStart = iStart + iChunk

        return self.buildIssuesDFFromList(lFinal)

     # builds a filtered and narrowed DF from a list of issues
    def buildIssuesDFFromList(self,pIssues):
        lIssues = []
        for dIssue in pIssues:
            dNewIssue = {}
            for dField in G_Fields:
                sField = dField["Field"]
                lPath = dField["Path"]
                try:
                    oValue = dIssue[lPath[0]]
                    for sPart in lPath[1:]:
                        if '[0]' in sPart:
                            oValue = oValue[sPart.replace("[0]", "")][0]
                        else:
                            oValue = oValue[sPart]
                except:
                    oValue = 'unknown'
                dNewIssue[sField] = oValue
            if dNewIssue["Team"] == self.aTeam:
                lIssues.append(dNewIssue)
        return pd.DataFrame(lIssues)

    # get watchers for a list of issues found in DF
    def getWatchersDF(self,pDFIssues):
        self.aLogger.info("createWatchersDF.Start")
        lAllWatchers = []
        auth = HTTPBasicAuth(self.aConfig.getParm("Jira.User"), self.aConfig.getParm("Jira.Token"))
        dHeaders = {"Accept": "application/json"}
        for index, dIssue in pDFIssues.iterrows():
            self.aLogger.debug("Requesting: " + str(dIssue["WatcherURL"]))
            response = requests.request("GET", dIssue["WatcherURL"], headers=dHeaders, auth=auth)
            lWatchers = json.loads(response.text)["watchers"]
            for dWatcher in lWatchers:
                dNewWatcher = {}
                dNewWatcher["Issue key"] = dIssue["Key"]
                dNewWatcher["Watchers"] = dWatcher["displayName"]
                lAllWatchers.append(dNewWatcher)

        self.aLogger.info("createWatchersDF.End.OK")
        return pd.DataFrame(lAllWatchers)

    # this needs to loop ... to get more than 100 issues
    def getAllIssueHistoryDF(self,pStartDate):
        self.aLogger.info("getAllIssueHistoryDF.Start.OK")
        sFilter = self.aFilter.replace("<CreatedDate>", pStartDate)
        lAllChanges = []
        lChanges = []

        jira = JIRA(basic_auth=(self.aUser,self.aToken),options={'server': self.aServer})
        iStart = 0
        iChunk = 100
        iSize = 200

        while iSize >= iChunk:
            self.aLogger.info("getNextChunkOfHistory")
            issues = jira.search_issues(sFilter,maxResults=iChunk,startAt=iStart,expand='changelog')
            for oIssue in issues:
                # only need history for issues where Team = Toasted Snow
                if oIssue.fields.customfield_10001 != None:
                    if oIssue.fields.customfield_10001.name == self.aTeam:
                        lChanges = self.getIssueHistory(oIssue)
                        for o in lChanges:
                            lAllChanges.append(o)
            iSize = len(issues)
            iStart  = iStart + iChunk

        # convert final list to DF and return
        dfIssueHistory = pd.DataFrame(lAllChanges)
        self.aLogger.info("getAllIssueHistoryDF.End.OK")
        return dfIssueHistory


    def getIssueHistory(self,pIssue):
        lChanges = []
        for history in pIssue.changelog.histories:
            for item in history.items:
                if item.field == "status":
                    dChange = {}
                    dChange["Key"] = pIssue.key
                    dChange["Author"] = history.author
                    dChange["DateTime"] = history.created
                    dChange["FromStatus"] = item.fromString
                    dChange["ToStatus"] = item.toString
                    lChanges.append(dChange)
        return lChanges