from flask import Flask
from flask import request
from waitress import serve
from crowler import main as Crowler

app = Flask(__name__)

def BuildResponseFromJson(jsonData):     
    response = app.response_class(
        response=jsonData,
        status=200,
        mimetype='application/json'
    )    
    return response

@app.errorhandler(500)
def handle_bad_request(error):
    response = app.response_class(
        response=error,
        status=500,
        mimetype='application/text'
    )    
    return response #STRING

@app.route('/')
def serviceUp():
    # Render the page
    app.register_error_handler(500, handle_bad_request)
    return "Hello Python!"


@app.route('/crawler', methods=['POST'])
def crawler():   
    return BuildResponseFromJson(Crowler.mainFunction(request.get_data()))
  

if __name__ == '__main__':
    # Run the app server on localhost:4449
    #app.run('localhost', 4449)  #FLASK       
    serve(app, host='0.0.0.0', port = 4449) #WAITRESS