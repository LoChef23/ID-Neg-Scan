from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class Navigation():
    
    def __init__(self, localDriverPath, chrome_options):
        
        self.driver = webdriver.Chrome(executable_path=localDriverPath, chrome_options=chrome_options)
        self.currentUrl = ''

    #exception to be managed and logged
    def get_start_page(self, startingUrl):
        self.currentUrl = startingUrl
        self.driver.get(self.currentUrl)

    def check_for_next_page_existence(self):
        try:
            self.driver.find_element_by_xpath("//div[@id='selector']/ul/li/a[@class = 'page-link next' and contains(@href, '#page-')]")
        except NoSuchElementException as exception:
            return False
        else:
            return True
    
    #exception to be managed and logged
    def get_next_page(self, startingUrl):
        self.driver.find_element_by_xpath("//div[@id='selector']/ul/li/a[@class = 'page-link next' and contains(@href, '#page-')]").click()
        self.currentUrl = self.driver.current_url

    def find_cases_table(self):
        htmlTable = self.driver.find_element_by_id('tablePerkaraAll').get_attribute('outerHTML')
        return htmlTable