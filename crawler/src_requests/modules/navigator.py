import requests

class Navigation():
    
    def __init__(self):
        self.session = requests.Session()
    
    def calculate_next_url(self, startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix):
        pageNumber += 1
        url = startingUrl + fixedPagePrefix + str(pageNumber) + fixedPageSuffix
        return url, pageNumber

    def request_url(self, url):
        response = self.session.get(url)
        return response.text