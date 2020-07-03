from flask import Flask
from flask import request
import json
import traceback
#from waitress import serve
from Crawler import Crawler

app = Flask(__name__)

def buildResponseFromJson(jsonData, statusCode, mimeType):     
    response = app.response_class(
        response=jsonData,
        status=statusCode,
        mimetype=mimeType
    )    
    return response

@app.errorhandler(500)
def handle_bad_request(error):
    return buildResponseFromJson(traceback.format_exc(), 500, 'application/text')

@app.route('/')
def serviceUp():
    # Render the page
    app.register_error_handler(500, handle_bad_request)
    return "Hello Python!"

@app.route('/RunIncrementalNegativEventCrawler', methods=['POST'])
def runIncremental():   
    requestData = request.json
    print(requestData)
    crawler = Crawler()
    result = crawler.run(requestData)
    return buildResponseFromJson(result, 200, 'application/json')

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449)  #FLASK       
    #serve(app, host='0.0.0.0', port = 4449) #WAITRESS