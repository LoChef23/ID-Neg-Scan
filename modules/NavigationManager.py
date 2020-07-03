import requests
from datetime import datetime
from os import path, mkdir
import json
from modules.LogManager import LogManager
from modules.DataManager import DataManager
import sys
class NavigationManager():
    
    def __init__(self):
        self.session = requests.Session()
        self.proxies = {
                           "http": "http://127.0.0.1:3128",
                           "https": "http://127.0.0.1:3128",
                       }
    
    def calculate_next_url(self, startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix):
        pageNumber += 1
        url = startingUrl + fixedPagePrefix + str(pageNumber) + fixedPageSuffix
        return url, pageNumber

    # proxies = self.proxies
    def request_url(self, url):
        response = self.session.get(url)
        return response.text

    def retrieve_incremental_cases_info_from_url(self, urlToBeRequested, startingUrlOfTheProvince, navigationManger, dataManager,  dataFile, logManager, logFile, elaborationDate, limitDate):
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
    def retrieve_online_negative_data(self, elaborationsDirectory, startingUrl, totPages, fixedPageSuffix, fixedPagePrefix, recoveryTentatives, limitDate):
        retval = []
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
        casesDataRetrieved = self.retrieve_incremental_cases_info_from_url(startingUrl, startingUrl, navigationManger, dataManager,  dataFile, logManager, logFile, elaborationDate, limitDate)
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
            casesDataRetrieved = self.retrieve_incremental_cases_info_from_url(url[0], startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate, limitDate)
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
                    casesDataRetrieved = self.retrieve_incremental_cases_info_from_url(urlToRecover, startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate, limitDate)
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

    def retrieve_cases_info_from_url_full(self, urlToBeRequested, startingUrlOfTheProvince, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate):
        logManager.add_checkpoint_log(logFile, urlToBeRequested)
        try:
            response = navigationManger.request_url(urlToBeRequested)
            extractedCases = dataManager.extract_cases(response, startingUrlOfTheProvince, elaborationDate)            
            dataManager.store_cases(dataFile, extractedCases)           
            return True
        except Exception as ex:
            logManager.add_error_log(logFile, str(ex))
            return False

    #everything that happens in this function is referred to a single url elaboration
    def retrieve_online_negative_data_full(self, elaborationsDirectory, startingUrl, totPages, fixedPageSuffix, fixedPagePrefix, recoveryTentatives):

        # defines working directory for each url elaboration and elaboration date
        province = startingUrl[12:len(startingUrl)-6]
        elaborationDate = datetime.now().strftime('%m.%d.%YT%H.%M.%S')
        siteElaborationDirectory = elaborationsDirectory + province + '//'
        
        # creates the url elaboration directory that will contain log and data file, if not exists
        if not path.exists(siteElaborationDirectory):
            mkdir(siteElaborationDirectory)
        
        # instantiates the log class and creates the log file and data file
        logManager = LogManager()
        logFile = logManager.create_log_file(siteElaborationDirectory, elaborationDate)
        dataManager = DataManager()
        dataFile = dataManager.create_data_file(siteElaborationDirectory, elaborationDate)
        
        # initializes the client session and create recovery list
        navigationManger = NavigationManager()
        urlsToRecover = []
        
        # crawls the first page
        print(f'Requesting - {startingUrl}')        
        casesDataRetrievedWithoutErrors = self.retrieve_cases_info_from_url_full(startingUrl, startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate)
        if casesDataRetrievedWithoutErrors == False:
            urlsToRecover.append(startingUrl)

        #set the page number in ordeer to start the crawling loop
        pageNumber = 1
        
        # starts the crawling loop
        while pageNumber < totPages:
            url = navigationManger.calculate_next_url(startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix)
            # print(f'Requesting - {url[0]}')
            pageNumber = url[1]

            casesDataRetrievedWithoutErrors = self.retrieve_cases_info_from_url_full(url[0], startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate)
            if casesDataRetrievedWithoutErrors == False:
                urlsToRecover.append(url[0])
        
        #recovers the urls that failed
        if len(urlsToRecover) > 0:
            failedRecoveryFile = logManager.create_urls_failed_recovery_file(siteElaborationDirectory, elaborationDate)
            
            recoveryRound = 0
            while recoveryRound <= recoveryTentatives:
                for urlToRecover in urlsToRecover:
                    # print(f'Requesting - {urlToRecover}')
                    casesDataRetrievedWithoutErrors = self.retrieve_cases_info_from_url_full(urlToRecover, startingUrl, navigationManger, dataManager, dataFile, logManager, logFile, elaborationDate)
                    if casesDataRetrievedWithoutErrors == True:
                        urlsToRecover.remove(urlToRecover)
                recoveryRound += 1

            failedRecoveryFile.write(str(urlsToRecover))
            failedRecoveryFile.close()

        logFile.close()
        dataFile.close()