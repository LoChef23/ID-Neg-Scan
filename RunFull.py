from os import path, mkdir
import sys
import json
from datetime import datetime
from modules.LogManager import LogManager
from modules.NavigationManager import NavigationManager
from modules.DataManager import DataManager
from multiprocessing import Process
from modules.NavigationManager import NavigationManager

if __name__ == '__main__':
    
    # loads config from file
    with open('config.json', 'r+') as configFile:
        configData = json.load(configFile)

    elaborationsDirectory = configData['elaborationsDirectory']
    fixedPagePrefix = configData['fixedPagePrefix']
    recoveryTentatives = configData['recoveryTentatives']

    # loads url list
    with open('input/fullInput.json', 'r+') as configFile:
        urls = json.load(configFile)
    
    # creates elaborations root directory that will contain single elaboration results, if not exists
    if not path.exists(elaborationsDirectory):
        mkdir(elaborationsDirectory)
    
    # starts jobs parallelism on different urls using multiprocessing
    navigationManager = NavigationManager()
    jobs = []
    for startingUrl in urls:      
       p = Process(target=navigationManager.retrieve_online_negative_data_full, args=(elaborationsDirectory, startingUrl['url'], int(startingUrl['totPages']), startingUrl['fixedPageSuffix'], fixedPagePrefix, recoveryTentatives))
       p.start()
       jobs.append(p)
       
    
    #close the multiprocessing action once all the jobs are done
    for job in jobs:
        job.join()