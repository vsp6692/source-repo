import groovy.json.JsonSlurper 

def env = System.getenv()
String url= env['JENKINS_URL'] + "/computer/api/json"
def r = new Random()

String nodeLabel = "Cougar"

String getResult = new URL(url).text
ArrayList nodeList= new ArrayList()

def card = new JsonSlurper().parseText(getResult)

nodeList.add('ca1vmlwbbp271')
nodeList.add('ca1vmlwbbp272')
nodeList.add('ca1vmlwbbp273')
nodeList.add('ca1vmlwbbp274')

for(int i=0;i<card.computer.size;i++) {
    for (int j=0;j<card.computer[i].assignedLabels.size();j++) {               
        if (card.computer[i].assignedLabels[j].name.toLowerCase() == nodeLabel.toLowerCase() && card.computer[i].offline == true) {
            nodeList.add(card.computer[i].displayName)
        }
    }
}

def nodeListSize=nodeList.size()
Host = nodeList.get(r.nextInt(nodeListSize))

println Host