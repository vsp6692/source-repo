import sys
import requests
import time
import os

modules=[]
jobUrl=os.environ['JENKINS_URL'] + os.environ['JOB'] + '/' + os.environ['BUILD_NUMBER'] + '/api/json'

def getResponse(url):
    """ The function does a get request to get
    response from URL and parse it to
    json data"""

    try:
        response = requests.get(url, timeout=600)
    except requests.exceptions.ReadTimeout:
        print ("READ TIMED OUT -", url)
        exit (1)
    except requests.exceptions.ConnectionError:
        print ("CONNECT ERROR -", url)
        exit (1)
    except requests.exceptions.RequestException:
        print ("OTHER REQUESTS EXCEPTION -", url)
        exit (1)

    return response.json()

response=getResponse(jobUrl)
if response['changeSets']:
    for path in response['changeSets'][0]['items'][0]['affectedPaths']:
        moduleName=path.split('/')[0]
        if moduleName not in modules:
            modules.append(moduleName)

print(modules)   