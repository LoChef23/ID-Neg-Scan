from os import path, mkdir
import json
from datetime import datetime
from modules.logger import Log
from modules.navigator import Navigation
from modules.extractor import CasesParser
from multiprocessing import Process


#everythiing that happens in this function is referred to a single url elaboration
def url_parallel_parsing(elaborationsDirectory, startingUrl, totPages, fixedPageSuffix, fixedPagePrefix):

    # defines working directory for each url elaboration and elaboration date
    province = startingUrl[12:len(startingUrl)-6]
    elaborationDate = datetime.now().strftime('%m.%d.%YT%H.%M.%S')
    siteElaborationDirectory = elaborationsDirectory + province + '//'
    
    # creates the url elaboration directory that will contain log and data file, if not exists
    if not path.exists(siteElaborationDirectory):
        mkdir(siteElaborationDirectory)
    
    # instantiates the log class and creates the log file and data file
    log = Log()
    logFile = log.create_log_file(siteElaborationDirectory, elaborationDate)
    dataFile = open(siteElaborationDirectory + 'full_data' + '_' + elaborationDate + '.json', 'a+')
    
    # initializes the client session and the parser and the page number
    navigationManger = Navigation()
    dataManager = CasesParser()
    pageNumber = 0

    # tries to crawl the first page
    try:
        print(f'Requesting {startingUrl}')
        log.add_checkpoint_log(logFile, startingUrl)
        response = navigationManger.request_url(startingUrl)
        extractedCases = dataManager.extract_cases(response, startingUrl, elaborationDate)
        dataManager.store_cases(dataFile, extractedCases)
    except Exception as ex:
        log.add_error_log(logFile, "ERROR: " + str(ex))
    
    #re-sets the page number after the first page has been don
    pageNumber = 1
    
    # starts the crawling loop
    while pageNumber <= totPages:
        try:
            url = navigationManger.calculate_next_url(startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix)
            print(f'Requesting {url[0]}')
            log.add_checkpoint_log(logFile, url[0])
            response = navigationManger.request_url(url[0])
            pageNumber = url[1]
            extractedCases = dataManager.extract_cases(response, startingUrl, elaborationDate)
            dataManager.store_cases(dataFile, extractedCases)
        except Exception as ex:
            log.add_error_log(logFile, "ERROR: " + str(ex))

if __name__ == '__main__':
    
    # loads config from file
    with open('config.json', 'r+') as configFile:
        configData = json.load(configFile)

    elaborationsDirectory = configData['elaborationsDirectory']
    fixedPagePrefix = configData['fixedPagePrefix']
    urls = configData['urlList']
    
    # creates elaborations root directory that will contain single elaboration results, if not exists
    if not path.exists(elaborationsDirectory):
        mkdir(elaborationsDirectory)
    
    # starts parallelism on different urls using multiprocessing
    jobs = []
    for startingUrl in urls:
       p = Process(target=url_parallel_parsing, args=(elaborationsDirectory, startingUrl['url'], int(startingUrl['totPages']), startingUrl['fixedPageSuffix'], fixedPagePrefix))
       p.start()
       jobs.append(p)
    
    #close the various processes
    for job in jobs:
        job.join()