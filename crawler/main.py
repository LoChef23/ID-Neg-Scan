import json as js
import importlib
import codecs
import warnings
warnings.filterwarnings('ignore')

# inputdata = 'palmax_index.json'
# inputdata = 'GIS-2019-2GO_GROUP_INCORPORATED_index.json'
# inputdata = js.load(codecs.open(inputdata, 'r', 'utf-8-sig'))
# inputdata = js.dumps(inputdata)

def mainFunction(inputdata):
      
    inputdata = js.loads(inputdata)       
    
    Project = inputdata['Header']['ProjectId']
        
    Service = 'run_incremental'              
    
    module =  Project + '.' + Service  

    try:
        Crowler = importlib.import_module(module)
        returnvalue = Crowler.mainFunction(inputdata)      
    except Exception as e:
        returnvalue = str(e)  

    return(returnvalue)