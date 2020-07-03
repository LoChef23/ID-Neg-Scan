from datetime import datetime
from os import mkdir

class LogManager():
 
    def create_log_file(self, elaborationDirectory, elaborationDate):
        logFile = open(elaborationDirectory + 'full_' + elaborationDate + '_logs' '.txt', 'a+')
        return logFile
    
    def create_incremental_log_file(self, elaborationDirectory, elaborationDate):
        logFile = open(elaborationDirectory + 'incr_' + elaborationDate + '_logs' '.txt', 'a+')
        return logFile
    
    def create_urls_failed_recovery_file(self, elaborationDirectory, elaborationDate):
        urlsFailedRecoveryFile = open(elaborationDirectory + 'full_' + elaborationDate + '_urlsFailedRecovery' '.txt', 'a+')
        return urlsFailedRecoveryFile
    
    def add_checkpoint_log(self, logFile, currentUrl):
        timestamp = str(datetime.now())
        logFile.seek(0)
        data = logFile.read(10)
        if len(data) > 0:
            logFile.write('\n')
        logFile.write(timestamp + ' - ' + 'Elaborating' + ' - ' + currentUrl)
    
    def add_error_log(self, logFile, exception):
        timestamp = str(datetime.now())
        logFile.seek(0)
        data = logFile.read(10)
        if len(data) > 0:
            logFile.write('\n')
        logFile.write(timestamp + ' - ERROR: ' + exception)

    