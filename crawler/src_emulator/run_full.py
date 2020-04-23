from os import path, mkdir
import json
from datetime import datetime
from modules.logger import Log
from modules.navigator import Navigation
from modules.extractor import CasesParser
from multiprocessing import Process
from selenium.webdriver.chrome.options import Options

def url_parallel_parsing(localDriverPath, startingUrl):
    province = startingUrl[12:len(startingUrl)-6]
    elaborationDate = datetime.now().strftime('%m.%d.%YT%H.%M.%S')
    elaborationDirectory = '..//elaborations//' + province + '//'
    if not path.exists(elaborationDirectory):
        mkdir(elaborationDirectory)
    
    log = Log()
    chrome_options = Options()  
    #chrome_options.add_argument("--headless")
    sippNavigation = Navigation(localDriverPath, chrome_options)
    casesParser = CasesParser()
    
    logFile = log.create_log_file(elaborationDirectory, elaborationDate)
    dataFile = casesParser.create_data_file(elaborationDirectory, elaborationDate)
    
    try:
        sippNavigation.get_start_page(startingUrl)
        log.add_checkpoint_log(logFile, sippNavigation.currentUrl)
        extractedCases = casesParser.extract_cases(sippNavigation.find_cases_table(), startingUrl, elaborationDate)
        casesParser.store_cases(dataFile, extractedCases)
    except Exception as exception:
        log.add_checkpoint_log(logFile, "Error: " + str(exception))
    
    while sippNavigation.check_for_next_page_existence():
        try:
            sippNavigation.get_next_page(startingUrl)
            log.add_checkpoint_log(logFile, sippNavigation.currentUrl)
            extractedCases = casesParser.extract_cases(sippNavigation.find_cases_table(), startingUrl, elaborationDate)
            casesParser.store_cases(dataFile, extractedCases)
        except Exception as exception:
            log.add_checkpoint_log(logFile, "Error: " + str(exception))


if __name__ == '__main__':
    with open('config.json', 'r+') as configFile:
        configData = json.load(configFile)

    localDriverPath = configData['driverPath']
    urls = configData['urlList']
    

    for startingUrl in urls:
        Process(target=url_parallel_parsing, args=(localDriverPath, startingUrl['url'])).start()