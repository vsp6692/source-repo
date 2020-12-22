# Script to check Jenkins build status, got from
# https://serverfault.com/questions/309848/how-do-i-check-the-build-status-of-a-jenkins-build-from-the-command-line
# and converted to be used by Python3
# Sachin Gupta
# Feb 10, 2020

import json 
import sys
import requests

jenkinsUrl = "http://ci-jenkins-01/bbp/job/"

def getResponse(url, type):
    """ The function does a get request to get
    response from URL and parse it to
    json data"""

    try:
        response = requests.get(url, timeout=600)
    except requests.exceptions.ReadTimeout:
        print ("READ TIMED OUT -", url)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print ("CONNECT ERROR -", url)
        sys.exit(1)
    except requests.exceptions.RequestException:
        print ("OTHER REQUESTS EXCEPTION -", url)
        sys.exit(1)

    if type == 'json':
        return response.json()
    elif type == 'text':
        return response.text

def main():
    if len( sys.argv ) > 1 :
        jobName = sys.argv[1]
    else :
        print ("Provide Job Name as Arguement")
        sys.exit(1)

    apiUrl = jenkinsUrl + jobName + "/lastBuild/api/json"
    buildStatusJson = getResponse(apiUrl, "json")

    if "result" in buildStatusJson.keys():
        print ("CI Pipeline for Job " + jobName + " is " + buildStatusJson["result"] )
        sys.exit(0)
    else:
        print("Result not Found in API")
        sys.exit(1)

if __name__== "__main__":
   main()