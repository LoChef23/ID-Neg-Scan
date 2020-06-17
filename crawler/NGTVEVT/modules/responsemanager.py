import json
import uuid
class ResponseManager():

    def store_cases(self, extractedCases):
        Outputjson = []
        for extractedCase in extractedCases:
            Outputjson.append({ 'ID' : str(uuid.uuid1()) ,
                                'extractedCaseString' :  extractedCase            
            } )
        return( json.dumps(Outputjson) )


             