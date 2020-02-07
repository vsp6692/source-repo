import requests
import json
import time
import datetime
import os
import sys
import mysql.connector
from mysql.connector import errorcode
from configparser import ConfigParser


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


def dbConnect(configur):
    """This function creates DB connection
    and returns db connection object"""

    try:
        print ("Connecting to Database " + configur.get('dbconfig','databaseName'))
        mydb = mysql.connector.connect(
            host = configur.get('dbconfig','dbhost') ,
            user = os.environ['DB_USERNAME'],
            passwd = os.environ['DB_PASSWORD'],
            database = configur.get('dbconfig','databaseName')
        )
        print ("Connected to Database " + configur.get('dbconfig','databaseName'))
        return mydb
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
            sys.exit(1)
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
            sys.exit(1)            
        elif err.errno == 2003:
            print("Invalid DB host address")
            sys.exit(1)            
        else:
            print(err.errno)      
            sys.exit(1)

def createTable(mydb):
    """Function creates tables with default colums
    for the pipeline, if not there,
    else will skip the step"""

    print ("Getting tables list from Database.")
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")  
    tables = mycursor.fetchall()
    table_list = [item for t in tables for item in t] 

    if os.environ['BUILD_NAME'] not in table_list:
        print ( "Creating table " + os.environ['BUILD_NAME'] + ".") 
        createCmd = "CREATE TABLE " + os.environ['BUILD_NAME'] + " ( Name VARCHAR(255), Number VARCHAR(255), Division VARCHAR(255), Result VARCHAR(255), CHECK (Result in ('SUCCESS','FAILURE','UNSTABLE')), Duration TIME, `Build Time` DATETIME, `Build URL` VARCHAR(255), `Stream Name` VARCHAR(255));"
        try:
            mycursor.execute(createCmd)
            print ( "Created table " + os.environ['BUILD_NAME'] + ".") 
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Already exists.")
                sys.exit(1)                
            else:
                print(err.msg)  
                sys.exit(1)                
    else:
        print ( "Table " + os.environ['BUILD_NAME'] + " already exists, so skipping creation.")          


def getResponses(configur):
    """This function helps in getting response 
    from Jenkins API's"""

    responseDict = {}

    print ( "Getting response from API URL " +os.environ['BUILD_URL'] + "/api/json." ) 
    apiresponse = requests.get(os.environ['BUILD_URL'] + "/api/json")

    print ( "Getting response from WFAPI URL " +os.environ['BUILD_URL'] + "/wfapi/describe." ) 
    wfresponse = requests.get(os.environ['BUILD_URL'] + "/wfapi/describe")

    if apiresponse.status_code != 200 and wfresponse.status_code != 200:
        print ("No response from API.")
        sys.exit(1)
    else:
        print ("Modifying API and WFAPI response to JSON.")
        apiJson = apiresponse.json()
        wfJson = wfresponse.json()

    for i in apiJson["actions"]:
        if i != {}:
            if (i["_class"] == "hudson.model.ParametersAction"):
                if (i["parameters"][0]["name"] == "StreamName"):
                    responseDict["Stream Name"] = i["parameters"][0]["value"]

    for i in list(configur.get('buildconfig', 'divisions').split(',')):
        if i in apiJson["fullDisplayName"]:
            responseDict["Division"] = i

    responseDict["Name"] = os.environ['BUILD_NAME']
    responseDict["Number"] = os.environ['BUILD_NUMBER']
    responseDict["Result"] = wfJson["status"]
    responseDict["Duration"] = time.strftime("%H:%M:%S", time.gmtime(wfJson["durationMillis"]/1000))
    responseDict["Build Time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(wfJson["startTimeMillis"]/1000)))
    responseDict["Build URL"] = os.environ['BUILD_URL']

    return responseDict, wfJson


def alterTable(mydb, jobValue, wfJson):
    """Function creates column for each stages,
    with their suitable datatype"""
    mycursor = mydb.cursor()
    print ("Getting Columns name from table " + os.environ['BUILD_NAME'] + ".")
    selectCmd = 'SELECT column_name from information_schema.columns where table_schema = "build" and table_name = "' + os.environ['BUILD_NAME'] + '";'
    try:
        mycursor.execute(selectCmd)  
        columns = mycursor.fetchall()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Already Exists.")
            sys.exit(1)            
        else:
            print(err.msg)    
            sys.exit(1)            
    colums_list = [item for t in columns for item in t] 

    for i in wfJson["stages"]:
        if i["name"] != "Declarative: Post Actions":
            jobValue[i["name"]] = time.strftime("%H:%M:%S", time.gmtime(float(i["durationMillis"]/1000)))
            if ( i["name"] not in colums_list):
                altCmd = "ALTER TABLE " + os.environ['BUILD_NAME'] + " ADD `" + i["name"] + "` TIME;"
                try:                    
                    print("Creating New Column " + i["name"] + ".")
                    mycursor.execute(altCmd)
                except mysql.connector.Error as err:
                    print(err.msg) 
                    sys.exit(1)                    
    return jobValue                     


def insertValues(mydb,jobValue):
    """This function inserts all values
    from response to the database table"""

    columnNames = '`, `'.join(jobValue.keys())
    columnValues = '", "'.join(jobValue.values())

    mycursor = mydb.cursor()
    insertCmd = 'INSERT INTO %s ( `%s` ) VALUES ( "%s" );' % (os.environ['BUILD_NAME'], columnNames, columnValues)

    try:
        print ("Inserting Values to the table " + os.environ['BUILD_NAME'] + ".")
        mycursor.execute(insertCmd)
    except mysql.connector.Error as err:
            print(err.msg)             
            sys.exit(1)            
    mydb.commit()
    print ("Inserted job data in the table.")


def main():
    """Main function which calls other 
    functions for further proceedings"""
    jobValue = {}

    print ("Starting Script to Push Job Details")
    configur = readConfig()
    mydb = dbConnect(configur)
    createTable(mydb)
    jobValue, wfJson = getResponses(configur)
    jobValue = alterTable(mydb, jobValue, wfJson)
    insertValues(mydb, jobValue)
    print ("Script ran successfully.")

if __name__== "__main__":
   main()