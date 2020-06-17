from datetime import datetime
from os import path, mkdir
from modules.logmanager import LogManager
from modules.navigationmanager import NavigationManager
from modules.datamanager import DataManager
import json

def retrieve_incremental_cases_info_from_url(urlToBeRequested, startingUrlOfTheProvince, navigationManger, dataManager,  dataFile, logManager, logFile, elaborationDate, limitDate):
    logManager.add_checkpoint_log(logFile, urlToBeRequested)

    try:
        response = navigationManger.request_url(urlToBeRequested)
        extractedCases = dataManager.extract_cases(response, startingUrlOfTheProvince, elaborationDate)
        incrementalCases = dataManager.check_incremetal_cases(extractedCases, limitDate)
        casesToBeStored = incrementalCases[0]
        limitReached = incrementalCases[1]
        # dataManager.store_cases(dataFile, casesToBeStored)        
        return True, limitReached, casesToBeStored
    except Exception as ex:
        logManager.add_error_log(logFile, str(ex))
        return False, False, { }

        
#everything that happens in this function is referred to a single url elaboration
def retrieve_online_negative_data(elaborationsDirectory, startingUrl, totPages, fixedPageSuffix, fixedPagePrefix, recoveryTentatives, limitDate, retval):
    # defines working directory for each url elaboration and elaboration date
    province = startingUrl[12:len(startingUrl)-6]
    elaborationDate = datetime.now().strftime('%m.%d.%YT%H.%M.%S')
    siteElaborationDirectory = elaborationsDirectory + province + '//'
    
    # creates the url elaboration directory that will contain log and data file, if not exists
    if not path.exists(siteElaborationDirectory):
        mkdir(siteElaborationDirectory)
    
    # instantiates the log class and creates the log file and data file
    logManager = LogManager()
    logFile = logManager.create_incremental_log_file(siteElaborationDirectory, elaborationDate)
    dataManager = DataManager()
    dataFile = dataManager.create_incremental_data_file(siteElaborationDirectory, elaborationDate)
    
    # initializes the client session and create recovery list
    navigationManger = NavigationManager()
    urlsToRecover = []

    # create recovery list
    urlsToRecover = []
    limitReached = False

    # tries to crawl the first page
    print(f'Requesting - {startingUrl}')
    casesDataRetrieved = retrieve_incremental_cases_info_from_url(startingUrl, startingUrl, navigationManger, dataManager,  dataFile, logManager, logFile, elaborationDate, limitDate)
    casesDataRetrievedWithoutErrors = casesDataRetrieved[0]
    limitReached = casesDataRetrieved[1]
    retval.append(casesDataRetrieved[2])
    
    if casesDataRetrievedWithoutErrors == False:
        urlsToRecover.append(startingUrl)
    
    #re-sets the page number after the first page has been done
    pageNumber = 1
    
    # starts the crawling loop
    while limitReached == False:
        url = navigationManger.calculate_next_url(startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix)
        print(f'Requesting - {url[0]}')
        pageNumber = url[1]
        casesDataRetrieved = retrieve_incremental_cases_info_from_url(url[0], startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate, limitDate)
        casesDataRetrievedWithoutErrors = casesDataRetrieved[0]
        limitReached = casesDataRetrieved[1]
        retval.append(casesDataRetrieved[2])

        if casesDataRetrievedWithoutErrors == False:
            urlsToRecover.append(startingUrl)
    
    #recovers the urls that failed
    if len(urlsToRecover) > 0:
        failedRecoveryFile = logManager.create_urls_failed_recovery_file(siteElaborationDirectory, elaborationDate)
        recoveryRound = 0
        while recoveryRound <= recoveryTentatives:
            for urlToRecover in urlsToRecover:
                print(f'Requesting - {urlToRecover}')
                casesDataRetrieved = retrieve_incremental_cases_info_from_url(urlToRecover, startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate, limitDate)
                casesDataRetrievedWithoutErrors = casesDataRetrieved[0]
                retval.append(casesDataRetrieved[2])
                if casesDataRetrievedWithoutErrors == True:
                    urlsToRecover.remove(startingUrl)
            recoveryRound += 1

        failedRecoveryFile.write(str(urlsToRecover))
        failedRecoveryFile.close()

    logFile.close()
    dataFile.close()
    
    return(retval)