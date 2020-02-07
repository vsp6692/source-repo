import sys
import logging
import socket
from datetime import datetime,date,timedelta
from os import path,system,popen

#Varaibled for Jenkins
homeDir="/var/lib/jenkins"
bkpDir="/opt/jenkins_backup/" + socket.gethostname()
bkpDir="/mnt/jenkins_backup/" + socket.gethostname()
logFile="/opt/backup.log"
user="root"
server="ca1vmslsqe206"

#Logging Format
logging.basicConfig(filename=logFile, filemode='a', format='%(asctime)s: [%(levelname)s] - %(message)s', level=logging.INFO,datefmt='%d-%b-%y %H:%M:%S')

#Getting Time and Date
now = datetime.now()
today = date.today()


def cleanBackupLinux():
    """
    This function cleans backup
    which is older than 14 days
    """
    logging.info("Cleaning Old Backup.")
    listcmd='"ssh ' + user + "@" + server + ' ls ' + bkpDir + '"'
    ssh_out=popen(listcmd).read()
    dirNames=list(ssh_out.read().split("\n"))
    dirList=[i for i in dirNames if i]

    for dirs in dirList:
        dirDateStr = '-'.join(dirs.split('_')[2:])
        dirDate = datetime.strptime(dirDateStr, '%Y-%m-%d').date()
        if (today - dirDate).days > 14:
           logging.info("Remving Old Backup Folder " + bkpDir + "/" + dirs)
           rmcmd = '"yes | rm -rf "' + bkpDir + "/" + dirs + '"'
           popen(rmcmd)


def cleanBackupWindows():
    """
    This function cleans backup
    which is older than 14 days
    """
    logging.info("Cleaning Old Backup.")
    listcmd=' ls ' + bkpDir
    dirNames=popen(listcmd).read().split('\n')
    dirList=[i for i in dirNames if i]

    for dirs in dirList:
        dirDateStr = '-'.join(dirs.split('_')[2:])
        dirDate = datetime.strptime(dirDateStr, '%Y-%m-%d').date()
        if (today - dirDate).days > 14:
           logging.info("Remving Old Backup Folder " + bkpDir + "/" + dirs)
           rmcmd = '"yes | rm -rf "' + bkpDir + "/" + dirs + '"'
           popen(rmcmd)           


def backup():
    """
    This Function creates a tar gz file
    for the jenkins home directory
    """
    logging.info("Compressing Jenkins Directory.")
    zipcmd="cd /var/lib ; tar --create --listed-incremental=jenkins.snar --gzip --absolute-names --preserve-permissions --file=jenkins.tar.gz " + homeDir
    system(zipcmd)


def copyBackupLinux(dirName, fileName):
    """
    Copies the Zipped File to
    the backup server
    """
    logging.info("Copying Files to Shared Server.")
    scpcmd="cd /var/lib ; scp jenkins.tar.gz " + user + "@" + server + ":" + bkpDir + "/" + dirName + "/" + fileName
    system(scpcmd)


def copyBackupWindows(dirName, fileName):
    """
    Copies the Zipped File to
    the backup server
    """
    logging.info("Copying Files to Shared Server.")
    cpcmd="cd /var/lib ; cp jenkins.tar.gz " + bkpDir + "/" + dirName + "/" + fileName
    system(cpcmd)    


def makePathLinux():
    dirName="jenkins_backup_" + now.strftime("%Y_%m_%d")
    mkdircmd="ssh " + user + "@" + server + " 'mkdir -p " + bkpDir + "/" + dirName + "'"
    system(mkdircmd)


def makePathWindows():
    dirName="jenkins_backup_" + now.strftime("%Y_%m_%d")
    mkdircmd="'mkdir -p " + bkpDir + "/" + dirName + "'"
    system(mkdircmd)


def main():
    """
    Main function which is called to
    start backup and copy it
    """
    if (len(sys.argv) == 0) or (len(sys.argv) >=2 ):
        logging.error("No of arguement passed is wrong. Please use L for Linux and W for Windows Share")
        sys.exit(1) 
        
    logging.info ("Starting Backup Script.")
    if path.exists(homeDir):
        if now.strftime("%w") == "0":
            logging.info("Runnning Full Backup.")

            logging.info("Deleting snar file for new backup.")
            rmcmd="rm -rf /var/lib/jenkins.snar"
            system(rmcmd)
            fileName="jenkins-master-backup-" + now.strftime("%Y-%d-%m-%H-%M-%S") + ".tar.gz"

            if sys.argv[1] == "L":
                logging.info("Backup Files to Linux Server.")
                dirName=makePathLinux()
                backup()
                copyBackupLinux(dirName, fileName)
                cleanBackupLinux()                
            elif sys.argv[1] == "W":
                logging.info("Backup Files to Windows Share")
                dirName=makePathWindows()
                backup()
                copyBackupWindows(dirName, fileName)
                cleanBackupWindows()                
            else:
                logging.error("Wrong arguement passed. Please use L for Linux and W for Windows Share")
                sys.exit(1)                
        else:
            logging.info("Running Incremental Backup.")

            days=timedelta(days=int(now.strftime("%w")))
            masterDate=now-days
            dirName="jenkins_backup_" + masterDate.strftime("%Y_%m_%d")
            fileName="jenkins-incremental-backup-" + now.strftime("%Y-%d-%m-%H-%M-%S") + ".tar.gz"
            if sys.argv[1] == "L":
                logging.info("Backup Files to Linux Server.")
                dirName=makePathLinux()
                backup()
                copyBackupLinux(dirName, fileName)               
            elif sys.argv[1] == "W":
                logging.info("Backup Files to Windows Share")
                dirName=makePathWindows()
                backup()
                copyBackupWindows(dirName, fileName)              
            else:
                logging.error("Wrong arguement passed. Please use L for Linux and W for Windows Share")
                sys.exit(1)    
    else:
        logging.error("Error: " + homeDir + " not found. Can not continue.")
        sys.exit(1)
    logging.info("Backup Completed.")


#Calling Main Function
if __name__== "__main__":
       main()