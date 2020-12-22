import requests
import os
import sys
import random

url = os.environ['JENKINS_URL'] + "/computer/api/json"
nodeLabel=sys.argv[1]
print (nodeLabel)

def getResponse():
    """ The function does a get request to get
    response from URL and parse it to
    json data"""

    print (url)
    try:
        response = requests.get(url, timeout=600)
    except requests.exceptions.ReadTimeout:
        print ("READ TIMED OUT -", url)
    except requests.exceptions.ConnectionError:
        print ("CONNECT ERROR -", url)
    except requests.exceptions.RequestException:
        print ("OTHER REQUESTS EXCEPTION -", url)

    return response.json()

def getNode():
    nodeList=[]
    nodeListResponse=getResponse()['computer']
    for nodes in nodeListResponse:
        for labels in (nodes['assignedLabels']):
            if labels['name'].lower() == nodeLabel and nodes['offline']:
                nodeList.append(nodes['displayName'])
    print (random.choice(nodeList))

def main():
    """Main function which calls other
    functions for further proceedings"""

    print ("Starting Script to Get Labels")
    getNode()

    print ("Script ran successfully.")


if __name__== "__main__":
   main()