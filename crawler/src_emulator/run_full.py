from os import path, mkdir
import json
from datetime import datetime
from modules.logmanager import LogManager
from modules.navigationmanager import NavigationManager
from modules.datamanager import DataManager
from multiprocessing import Process
from selenium.webdriver.chrome.options import Options

def url_parallel_parsing(localDriverPath, startingUrl):
    province = startingUrl[12:len(startingUrl)-6]
    elaborationDate = datetime.now().strftime('%m.%d.%YT%H.%M.%S')
    elaborationDirectory = '..//elaborations//' + province + '//'
    if not path.exists(elaborationDirectory):
        mkdir(elaborationDirectory)
    
    logManager = LogManager()
    chrome_options = Options()  
    #chrome_options.add_argument("--headless")
    navigationManager = NavigationManager(localDriverPath, chrome_options)
    dataManager = DataManager()
    
    logFile = logManager.create_log_file(elaborationDirectory, elaborationDate)
    dataFile = dataManager.create_data_file(elaborationDirectory, elaborationDate)
    
    try:
        navigationManager.get_start_page(startingUrl)
        logManager.add_checkpoint_log(logFile, navigationManager.currentUrl)
        extractedCases = dataManager.extract_cases(navigationManager.find_cases_table(), startingUrl, elaborationDate)
        dataManager.store_cases(dataFile, extractedCases)
    except Exception as exception:
        logManager.add_checkpoint_log(logFile, "Error: " + str(exception))
    
    while navigationManager.check_for_next_page_existence():
        try:
            navigationManager.get_next_page(startingUrl)
            logManager.add_checkpoint_log(logFile, navigationManager.currentUrl)
            extractedCases = dataManager.extract_cases(navigationManager.find_cases_table(), startingUrl, elaborationDate)
            dataManager.store_cases(dataFile, extractedCases)
        except Exception as exception:
            logManager.add_checkpoint_log(logFile, "Error: " + str(exception))


if __name__ == '__main__':
    with open('config.json', 'r+') as configFile:
        configData = json.load(configFile)

    localDriverPath = configData['driverPath']
    urls = configData['urlList']
    
    jobs = []
    for startingUrl in urls:
        p = Process(target=url_parallel_parsing, args=(localDriverPath, startingUrl['url']))
        p.start()
        jobs.append(p)
    
    for job in jobs:
        job.join()