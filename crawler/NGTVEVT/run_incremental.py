from os import path, mkdir
import json
from modules.helpers import retrieve_online_negative_data
from modules.helpers import retrieve_incremental_cases_info_from_url
from multiprocessing import Process, Manager


def mainFunction(imputData):
    retval = []
    if __name__ == '__main__':

        # loads config from file

        # configData =  json.load(imputData) 
        
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
        startingUrl = urls[0]  
                  
        retval = retrieve_online_negative_data(elaborationsDirectory,
                                            startingUrl['url'], 
                                            int(startingUrl['totPages']),
                                            startingUrl['fixedPageSuffix'],
                                            fixedPagePrefix, 
                                            recoveryTentatives,
                                            startingUrl['limitDate'],
                                            retval)                
           
        print(retval)
        #close the multiprocessing action once all the jobs are done        
        retvalue = json.dumps(retval) 
        # retval = list(retval) 
        
        return(retvalue)


def testCrowl():
    ###############################         INPUT
    with open('config.json', 'r+') as configFile:
        inputdata = json.load(configFile)
    inputdata = json.dumps(inputdata)   
    return print( 'Result\n'+ str(mainFunction(inputdata)) )

testCrowl()
