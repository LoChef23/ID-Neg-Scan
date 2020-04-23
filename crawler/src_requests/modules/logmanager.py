from datetime import datetime
from os import mkdir

class LogManager():
 
    def create_log_file(self, elaborationDirectory, elaborationDate):
        logFile = open(elaborationDirectory + 'full_logs' + '_' + elaborationDate + '.txt', 'a+')
        return logFile

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
        logFile.write(timestamp + ' - ' + exception)