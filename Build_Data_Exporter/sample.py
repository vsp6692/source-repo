
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


apiUrl = "http://ca1vmllsqe223/api/json?tree=jobs[name,url]"
apiJson = getResponse(apiUrl, "json")

for jobs in apiJson["jobs"]:
    print ("http://ca1vmllsqe223/job/" + jobs["name"] + "/disable")