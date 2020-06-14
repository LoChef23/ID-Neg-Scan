import requests

class NavigationManager():
    
    def __init__(self):
        self.session = requests.Session()
        self.proxies = {
                           "http": "http://127.0.0.1:3128",
                           "https": "http://127.0.0.1:3128",
                       }
    
    def calculate_next_url(self, startingUrl, pageNumber, fixedPageSuffix, fixedPagePrefix):
        pageNumber += 1
        url = startingUrl + fixedPagePrefix + str(pageNumber) + fixedPageSuffix
        return url, pageNumber

    # proxies = self.proxies
    def request_url(self, url):
        response = self.session.get(url)
        return response.text