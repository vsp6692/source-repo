import os
import sys

modules=['sds','JunkerGui','softs','sots','sta','sts','slv','uaaa']
module_list=[]

#files=os.environ['CHANGE_FILES']
#file_list=os.environ['CHANGE_FILES'].split('\n')
file_list=['\r', 'F:\\Jenkins303\\workspace\\EBeam_CI_SDK2_pull_request_build_validation>git log -1 --stat --pretty=format:ashwin/fix_1753 \r', 'ashwin/fix_1753', ' softs/pom.xml                                      |  47 +++++++-', ' .../java/com/klatencor/softs/db/HttpService.java   |   8 ++', ' .../softs/dataaccessor/SDSDataAccessorTest.java    | 119 ++++++++++++++++++', ' .../softs/datadiscovery/DataDiscoveryTest.java     |  60 +++++++++', ' .../com/klatencor/softs/tests/utils/Constants.java |  13 ++', ' .../java/com/klatencor/softs/tests/utils/Util.java |   5 +', ' .../com/klatencor/softs/testsuite/TestSuite.java   |  32 +++++', ' .../klatencor/softs/wiremock/WiremockClass.java    | 134 +++++++++++++++++++++', ' softs/src/test/resources/app.properties            |  23 +++-', ' .../testgetallsources/getallsourcesRes.json        |   1 +', ' .../testgetsource/getsourceRes.json                |   1 +', ' .../testgetworkspacebyid/getWorkspaceByIdRes.json  |   1 +', ' .../testinsertworkspace/postworkspace.json         |  42 +++++++', ' .../testDiscoverDataAccessor/lotlist.json          |   1 +', ' ..._lots-870200e2-1577-4169-9c2b-1dd34d772f4f.json |   1 +', ' ...ces_1-b541bb9f-d97f-4a66-9dd0-ca102f42b788.json |   1 +', ' ..._lots-870200e2-1577-4169-9c2b-1dd34d772f4f.json |  20 +++', ' ...ces_3-bfe35bce-c913-47ef-a253-aec91a2b4b06.json |  19 +++', ' ...paces-12a045ae-d9dc-46aa-9e67-dc85e7e16828.json |  19 +++', ' ...ces_1-b541bb9f-d97f-4a66-9dd0-ca102f42b788.json |  19 +++', ' ...urces-d1ac11d2-5cc1-4be0-b788-d6c72f877351.json |  19 +++', ' 21 files changed, 578 insertions(+), 7 deletions(-)', '']
for file_name in file_list:
  if '|' in file_name and '/' in file_name and '...' not in file_name:
      file = file_name[1:-1].split(' ')[0]
      module_name=file.split('/')[0]
      if module_name == 'sds':
          module_name == file.split('/')[1]
      if module_name in modules:
        module_list.append(module_name)
      
final_list=list(set(module_list))
print (final_list)