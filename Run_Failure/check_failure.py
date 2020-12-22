import sys
import requests
import time
import xlsxwriter
import os
import mysql.connector
from mysql.connector import errorcode
from configparser import ConfigParser
from datetime import datetime, timedelta
import smtplib,ssl
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


def readConfig():
    """Function reads the configuration to
    run the script. Its enough to change configuration
    alone."""

    if os.path.exists('config.ini'):
        print ("Reading Config File")
        configur = ConfigParser()
        configur.read('config.ini')
        return configur
    else:
        print ("config.ini does not exists")
        sys.exit()

def addWorkbook(workbook, jenkins, jobData):
    """Function creates workbook to
    store data."""

    row = 1
    col = 0

    titleStyle = workbook.add_format({'bold': 1, 'font_size': 14, 'font_name': 'Times New Roman', 'bg_color': '#6F9BE4', 'border': 1})
    columnStyle = workbook.add_format({'font_size': 12, 'font_name': 'Times New Roman', 'border': 1})
    dateFormat = workbook.add_format({'num_format': 'dd/mm/yy', 'font_size': 12, 'font_name': 'Times New Roman', 'border': 1})
    url_format = workbook.add_format({'font_size': 12, 'font_name': 'Times New Roman', 'border': 1,'underline': 1, 'font_color': 'blue'})

    worksheet = workbook.add_worksheet(jenkins.split(':')[0].upper())

    worksheet.set_column('A:A', 45)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 10)
    worksheet.set_column('G:G', 10)
    worksheet.set_column('H:H', 10)
    worksheet.set_column('I:I', 10)
    worksheet.set_column('J:J', 10)
    worksheet.set_column('K:K', 10)

    worksheet.write('A1', 'Job Name', titleStyle )
    worksheet.write('B1', 'Job Type', titleStyle )
    worksheet.write('C1', 'Last Build Time', titleStyle)
    worksheet.write('D1', 'Duration', titleStyle)
    worksheet.write('E1', 'Node Name', titleStyle)
    worksheet.write('F1', 'Job Status', titleStyle)
    worksheet.write('G1', 'Total ', titleStyle)
    worksheet.write('H1', 'Success', titleStyle)
    worksheet.write('I1', 'Failure', titleStyle)
    worksheet.write('J1', 'Unstable', titleStyle)
    worksheet.write('K1', 'Aborted', titleStyle)
    worksheet.write('L1', 'RTC FailedCount', titleStyle)

    for name, types, time, duration, node, url, jobstatus, buildCount, successCount, failureCount, unstableCount, abortedCount, rtcFailedCount in (jobData):
        worksheet.write_url(row, col, url, url_format, string=name, tip='Jenkins Job URL')
        worksheet.write(row, col + 1, types, columnStyle)
        if time == 'No Time':
            date_time = ""
        else:
            date_time = datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
        worksheet.write(row, col + 2, date_time, dateFormat)
        worksheet.write(row, col + 3, duration, columnStyle)
        worksheet.write(row, col + 4, node, columnStyle)
        worksheet.write(row, col + 5, jobstatus, columnStyle)
        worksheet.write(row, col + 6, buildCount, columnStyle)
        worksheet.write(row, col + 7, successCount, columnStyle)
        worksheet.write(row, col + 8, failureCount, columnStyle)
        worksheet.write(row, col + 9, unstableCount, columnStyle)
        worksheet.write(row, col + 10, abortedCount, columnStyle)
        worksheet.write(row, col + 10, rtcFailedCount, columnStyle)
        row += 1

    del worksheet


def getBuildCount(url):
    """This the function used to get
    build count ran during the last one month"""

    builds = []
    buildCount = 0
    successCount = 0
    failureCount = 0
    abortedCount = 0
    rtcFailedCount = 0
    unstableCount = 0
    stop_date = datetime.strptime(datetime.now().strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")
    start_date = datetime.strptime((datetime.now()-timedelta(days=30)).strftime("%d.%m.%Y %H:%M:%S"), "%d.%m.%Y %H:%M:%S")

    request_url = "{0:s}/api/json{1:s}".format(
            url,
            "?tree=builds[fullDisplayName,id,number,timestamp,url]"
        )
    response = requests.get(request_url, timeout=600).json()

    if response["builds"]:
        for build in response['builds']:

            build_date = datetime.utcfromtimestamp(build['timestamp']/1000)

            if build_date >= start_date and build_date <= stop_date:
                buildURL = build["url"] + "api/json"
                buildResponse = requests.get(buildURL, timeout=600).json()

                if buildResponse['result'] == 'SUCCESS':
                    successCount += 1
                elif buildResponse['result'] == 'FAILURE':
                    wfapiURL = build["url"] + "wfapi/describe"
                    wfResponse = requests.get(wfapiURL, timeout=600).json()
                    for stages in wfResponse["stages"]:
                        if "RTC" in stages["name"]:
                            if stages["status"] == 'FAILURE':
                                rtcFailedCount +=1
                    failureCount += 1
                elif buildResponse['result'] == 'ABORTED':
                    abortedCount += 1
                elif buildResponse['result'] == 'UNSTABLE':
                    unstableCount += 1
                builds.append(build)
                buildCount += 1
    return (buildCount, successCount, failureCount, unstableCount, abortedCount, rtcFailedCount)


def send_mail(configur):
    """ The function sends mail to SCM
    members with Jenkins Data Excel Sheet"""

    print ("Sending report to SCM People.")
    msg = MIMEMultipart()
    msg['From'] = configur.get('mailconfig','from')
    msg['To'] = configur.get('mailconfig','to')
    msg['Cc'] = configur.get('mailconfig','cc')
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = configur.get('mailconfig','subject')
    msg.attach(MIMEText(configur.get('mailconfig','text')))

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open("Jenkins_Data.xlsx", "rb").read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Jenkins_Data.xlsx"')
    msg.attach(part)
    smtp = smtplib.SMTP('mail.kla-tencor.com', 25)
    smtp.sendmail(configur.get('mailconfig','from'), configur.get('mailconfig','to'), msg.as_string())
    print ("Mail Sent Successfully.")
    smtp.quit()


def getResponse(url, type):
    """ The function does a get request to get
    response from URL and parse it to
    json data"""

    try:
        response = requests.get(url, timeout=600)
    except requests.exceptions.ReadTimeout:
        print ("READ TIMED OUT -", url)
    except requests.exceptions.ConnectionError:
        print ("CONNECT ERROR -", url)
    except requests.exceptions.RequestException:
        print ("OTHER REQUESTS EXCEPTION -", url)

    if type == 'json':
        return response.json()
    elif type == 'text':
        return response.text


def buildData(jenkins):
    """ The function helps in getting build data
    and calls function to store in excel"""

    print ("Getting Job Data for Jenkins " + jenkins + ".")
    jobData = []

    apiUrl = "http://" + jenkins + "/api/json?tree=jobs[name,url]"
    apiJson = getResponse(apiUrl, "json")

    for jobs in apiJson["jobs"]:
        nodeName=""

        jobUrl =  jobs["url"] + "/api/json"
        jobJson = getResponse(jobUrl, "json")

        if jobJson["_class"] == "org.jenkinsci.plugins.workflow.job.WorkflowJob":
            print ("Working on Job - " + jobs["name"])

            if jobJson["color"] == "disabled":
                jobStatus = "Disabled"
            else:
                jobStatus = "Active"

            if jobJson["lastBuild"] == None:
                jobData.append([jobs["name"], "Pipeline Job", "No Time", "NA", "NA", jobs["url"], "NA", 0, 0, 0, 0, 0])
            else:
                buildCount, successCount, failureCount,unstableCount, abortedCount = getBuildCount(jobs["url"])
                lastBuildUrl = jobs["url"] + "lastBuild/api/json"
                buildJson = getResponse(lastBuildUrl, "json")

                nodeUrl = jobs["url"] + "/lastBuild/consoleText"
                nodeText = getResponse(nodeUrl, "text")

                for item in nodeText.splitlines():
                    if "Running on" in item:
                        itemline = item.split(' ')
                        if itemline[0] == 'Running':
                            nodeName = itemline[2]
                            break
                        else:
                            nodeName = itemline[3]
                            break

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(buildJson["timestamp"]/1000)))
                duration = time.strftime("%H:%M:%S", time.gmtime(float(buildJson["duration"])))

                jobData.append([ jobs["name"], "Pipeline Job", timestamp, duration, nodeName.upper(), jobJson["url"], jobStatus, buildCount, successCount, failureCount, unstableCount, abortedCount])


        elif jobJson["_class"] == "hudson.model.FreeStyleProject":
            print ("Working on Job - " + jobs["name"])

            if jobJson["color"] == "disabled":
                jobStatus = "Disabled"
            else:
                jobStatus = "Active"

            if jobJson["lastBuild"] == None:
                jobData.append([jobs["name"], "Freestyle Job", "No Time", "NA", "NA", jobs["url"], "NA", 0, 0, 0, 0, 0])
            else:
                buildCount, successCount, failureCount, unstableCount, abortedCount = getBuildCount(jobs["url"])
                lastBuildUrl = jobs["url"] + "/lastBuild/api/json"
                buildJson = getResponse(lastBuildUrl, "json")

                if buildJson["builtOn"] == "":
                    nodeName = "Jenkins"
                elif buildJson["builtOn"] == None:
                    nodeName = "Jenkins"
                else:
                    nodeName = buildJson["builtOn"]

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(buildJson["timestamp"]/1000)))
                duration = time.strftime("%H:%M:%S", time.gmtime(float(buildJson["duration"])))

                jobData.append([jobs["name"], "Freestyle Job", timestamp, duration, nodeName.upper(), jobs["url"], jobStatus, buildCount, successCount, failureCount, unstableCount, abortedCount])


        elif jobJson["_class"] == "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject":

            print ("Working on Job - " + jobs["name"])
            if len(jobJson["jobs"]) != 0:
                for multijobs in jobJson["jobs"]:

                    if multijobs["color"] == "disabled":
                        jobStatus = "Disabled"
                    else:
                        jobStatus = "Active"

                    buildCount, successCount, failureCount, unstableCount, abortedCount = getBuildCount(multijobs["url"])

                    multiJobUrl = multijobs["url"] + "lastBuild/api/json"
                    multiJobJson = getResponse(multiJobUrl, "json")

                    nodeUrl = multijobs["url"] + "lastBuild/consoleText"
                    nodeText = getResponse(nodeUrl, "text")

                    for item in nodeText.splitlines():
                        if "Running on" in item:
                            itemline = item.split(' ')
                            if itemline[0] == "Running":
                                nodeName = itemline[2]
                                break
                            else:
                                nodeName = itemline[3]
                                break

                    jobName = jobs["name"] + "-" + multijobs["name"]

                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(multiJobJson["timestamp"]/1000)))
                    duration = time.strftime("%H:%M:%S", time.gmtime(float(multiJobJson["duration"])))

                    jobData.append([jobName, "Piepline Job", timestamp, duration, nodeName.upper(), multijobs["url"], jobStatus, buildCount, successCount, failureCount, unstableCount, abortedCount])

        elif jobJson["_class"] == "com.tikal.jenkins.plugins.multijob.MultiJobProject":
            print ("Working on Job - " + jobs["name"])

            if jobJson["color"] == "disabled":
                jobStatus = "Disabled"
            else:
                jobStatus = "Active"

            if jobJson["lastBuild"] == None:
                jobData.append([jobs["name"], "Freestyle Job", "No Time", "NA", "NA", jobs["url"], "NA", 0, 0, 0, 0, 0])
            else:
                buildCount, successCount, failureCount, unstableCount, abortedCount = getBuildCount(jobs["url"])
                lastBuildUrl = jobs["url"] + "/lastBuild/api/json"
                buildJson = getResponse(lastBuildUrl, "json")

                if buildJson["builtOn"] == "":
                    nodeName = "Jenkins"
                elif buildJson["builtOn"] == None:
                    nodeName = "Jenkins"
                else:
                    nodeName = buildJson["builtOn"]

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(buildJson["timestamp"]/1000)))
                duration = time.strftime("%H:%M:%S", time.gmtime(float(buildJson["duration"])))

                jobData.append([jobs["name"], "Multi Build Job", timestamp, duration, nodeName.upper(), jobs["url"], jobStatus, buildCount, successCount, failureCount, unstableCount, abortedCount])

        elif jobJson["_class"] == "jenkins.branch.OrganizationFolder":
            print ("Working on Job - " + jobs["name"])
            print ("Skipping Organisation folder, since its not a job.")

        else:
            print ("Working on Job - " + jobs["name"])
            jobData.append([jobs["name"], "Other Job", "No Time", "NA", "NA", jobs["url"], "NA", 0, 0, 0, 0, 0])

    print ("Job Data for Jenkins " + jenkins + " captured succesfully.")
    jobData.sort(key=lambda x:x[2])
    return jobData


def main():
    """Main function which calls other
    functions for further proceedings"""

    print ("Starting Script to Push Build Details")
    print ("=====================================")
    jenkinsURL = [ "ca1vmllsqe227"]
    configur = readConfig()

    print ("Creating Jenkins_Data.xlsx Workbook.")
    workbook = xlsxwriter.Workbook('Jenkins_Data.xlsx')

    for jenkins in jenkinsURL:
        print ("-----------------------------------------------")
        jobData = buildData(jenkins)
        addWorkbook(workbook, jenkins, jobData)
        print ("-----------------------------------------------")
    workbook.close()
    send_mail(configur)
    print ("Script ran successfully.")


if __name__== "__main__":
   main()