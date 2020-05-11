from os import path, mkdir
import json
from datetime import datetime
from modules.logmanager import LogManager
from modules.navigationmanager import NavigationManager
from modules.datamanager import DataManager
from multiprocessing import Process


#everything that happens in this function is referred to a single url elaboration
def url_parallel_parsing(elaborationsDirectory, startingUrl, totPages, fixedPageSuffix, fixedPagePrefix, recoveryTentatives, updateDays):

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
    
    # initializes the client session and the parser and the page number
    navigationManger = NavigationManager()
    pageNumber = 0

    # create recovery list
    urlsToRecover = []
    limitReached = False

    # tries to crawl the first page
    print(f'Requesting - {startingUrl}')
    logManager.add_checkpoint_log(logFile, startingUrl)
    try:
        response = navigationManger.request_url(startingUrl)
        extractedCases = dataManager.extract_cases(response, startingUrl, elaborationDate)
        incrementalCases = dataManager.check_incremetal_cases(extractedCases, updateDays)
        casesToBeStored = incrementalCases[0]
        limitReached = incrementalCases[1]
        dataManager.store_cases(dataFile, casesToBeStored)
    except Exception as ex:
        logManager.add_error_log(logFile, str(ex))
        urlsToRecover.append(startingUrl)
    
    #re-sets the page number after the first page has been done
    pageNumber = 1
    
    # starts the crawling loop
    while limitReached == False:
        url = navigationManger.calculate_next_url(startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix)
        print(f'Requesting - {url[0]}')
        logManager.add_checkpoint_log(logFile, url[0])
        pageNumber = url[1]
        try:
            response = navigationManger.request_url(url[0])
            extractedCases = dataManager.extract_cases(response, startingUrl, elaborationDate)
            incrementalCases = dataManager.check_incremetal_cases(extractedCases, updateDays)
            casesToBeStored = incrementalCases[0]
            limitReached = incrementalCases[1]
            dataManager.store_cases(dataFile, casesToBeStored)
        except Exception as ex:
            logManager.add_error_log(logFile, str(ex))
            urlsToRecover.append(url[0])
    
    #recovers the urls that failed
    if len(urlsToRecover) > 0:
        failedRecoveryFile = logManager.create_urls_failed_recovery_file(siteElaborationDirectory, elaborationDate)

        recoveryRound = 0
        while recoveryRound <= recoveryTentatives:
            for urlToRecover in urlsToRecover:
                print(f'Requesting - {urlToRecover}')
                logManager.add_checkpoint_log(logFile, urlToRecover)
                try:
                    response = navigationManger.request_url(urlToRecover)
                    extractedCases = dataManager.extract_cases(response, startingUrl, elaborationDate)
                    incrementalCases = dataManager.check_incremetal_cases(extractedCases, updateDays)
                    casesToBeStored = incrementalCases[0]
                    limitReached = incrementalCases[1]
                    dataManager.store_cases(dataFile, casesToBeStored)
                    urlsToRecover.remove(urlToRecover)
                except Exception as ex:
                    logManager.add_error_log(logFile, str(ex))
            recoveryRound += 1

        failedRecoveryFile.write(str(urlsToRecover))
        failedRecoveryFile.close()

    logFile.close()
    dataFile.close()
    
                        
if __name__ == '__main__':
    
    # loads config from file
    with open('config.json', 'r+') as configFile:
        configData = json.load(configFile)

    elaborationsDirectory = configData['elaborationsDirectory']
    fixedPagePrefix = configData['fixedPagePrefix']
    recoveryTentatives = configData['recoveryTentatives']
    urls = configData['urlList']
    
    # creates elaborations root directory that will contain single elaboration results, if not exists
    if not path.exists(elaborationsDirectory):
        mkdir(elaborationsDirectory)
    
    # starts jobs parallelism on different urls using multiprocessing
    jobs = []
    for startingUrl in urls:
       p = Process(target=url_parallel_parsing, args=(elaborationsDirectory, startingUrl['url'], int(startingUrl['totPages']), startingUrl['fixedPageSuffix'], fixedPagePrefix, recoveryTentatives, startingUrl['updateDays']))
       p.start()
       jobs.append(p)
    
    #close the multiprocessing action once all the jobs are done
    for job in jobs:
        job.join()