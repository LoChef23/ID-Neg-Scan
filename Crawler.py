from os import path, mkdir
import json
from modules.NavigationManager import NavigationManager

class Crawler():

    def run(self, imputData):
        # loading config
        with open('config.json', 'r+') as configFile:
            configData = json.load(configFile)

        # creates elaborations directory if not exists
        if not path.exists(configData['elaborationsDirectory']):
            mkdir(configData['elaborationsDirectory'])
        navigationManager = NavigationManager()
        retval = navigationManager.retrieve_online_negative_data(configData['elaborationsDirectory'],
                                            imputData['url'], 
                                            imputData['totPages'],
                                            imputData['fixedPageSuffix'],
                                            configData['fixedPagePrefix'], 
                                            configData['recoveryTentatives'],
                                            imputData['limitDate'])
        #close the multiprocessing action once all the jobs are done        
        retvalue = json.dumps(retval) 
        return(retvalue)

    def testCrowl(self):
        ###############################         INPUT
        with open('config.json', 'r+') as configFile:
            inputdata = json.load(configFile)
        inputdata = json.dumps(inputdata)   
        return print( 'Result\n'+ str(self.run(inputdata)) )
