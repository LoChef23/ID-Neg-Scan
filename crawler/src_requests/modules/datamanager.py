from bs4 import BeautifulSoup
import uuid
from datetime import datetime, timedelta

class DataManager():

    def create_data_file(self, elaborationDirectory, elaborationDate):
        dataFile = open(elaborationDirectory + 'full_' + elaborationDate + '_data' + '.json', 'a+')
        return dataFile
    
    def create_incremental_data_file(self, elaborationDirectory, elaborationDate):
        dataFile = open(elaborationDirectory + 'incr_' + elaborationDate + '_data' + '.json', 'a+')
        return dataFile


    def extract_cases(self, html, startUrl, elaborationDate):
        extractedCases = []
        soup = BeautifulSoup(html, 'lxml')
        casesGrid = soup.find(id = 'tablePerkaraAll')
        rows = casesGrid.find_all('tr')
        rowPosition = 0
        for row in rows:
            if rowPosition != 0:
                columns = row.find_all('td')
                columnPosition = 0
                for column in columns:
                    if columnPosition == 0:
                        #caseSiteNumber = column.get_text()
                        columnPosition +=1
                        continue
                    if columnPosition == 1:
                        caseIdentifier = column.get_text()
                        columnPosition +=1
                        continue
                    if columnPosition == 2:
                        rawRegistrationDate = column.get_text()
                        registrationDate = self.convert_registration_date(rawRegistrationDate)
                        columnPosition +=1
                        continue
                    if columnPosition == 3:
                        classification = column.get_text()
                        columnPosition +=1
                        continue 
                    if columnPosition == 4:
                        allParties = column.get_text()
                        columnPosition +=1
                        continue
                    if columnPosition == 5:
                        status = column.get_text()
                        columnPosition +=1
                        continue
                    if columnPosition == 6:
                        #duration = column.get_text()
                        columnPosition +=1
                        continue
                    if columnPosition == 7:
                        linkAttribute = column.find('a', href=True)
                        detailsLink = linkAttribute['href']
                        columnPosition +=1
                        continue

                caseProperties = {
                    "Site": startUrl,
                    "CreationDate": elaborationDate,
                    "CaseID": caseIdentifier,
                    "RegistrationDate": registrationDate,
                    "Classification": classification,
                    "AllParties": allParties,
                    "Status": status,
                    "DetailsLink": detailsLink
                }
                
                extractedCases.append(caseProperties)

                rowPosition += 1   
            else:
                rowPosition += 1
                continue
        
        return extractedCases

    # limit date should be provided as string in the format dd-mm-yyyy'
    def check_incremetal_cases(self, extractedCases, limitDate):
        
        limitDate = list(map(int, limitDate.split('-')))
        limitDate = datetime(limitDate[2],limitDate[1],limitDate[0])

        incrementalCases = list(extractedCases)

        for extractedCase in extractedCases:
            limitReached = False
            registrationDate = extractedCase['RegistrationDate'] #dd-mm-yyyy'
            registrationDate = list(map(int, registrationDate.split('-')))
            registrationDate = datetime(registrationDate[2],registrationDate[1],registrationDate[0])

            if registrationDate < limitDate:
                incrementalCases.remove(extractedCase)
                limitReached = True


        return incrementalCases, limitReached

    def convert_registration_date(self, rawRegistrationDate):
        if len(rawRegistrationDate) > 0:
            splittedDate = rawRegistrationDate.split()
            extractedMonth = splittedDate[1]
            monthsDict = {'Jan' : '01', 'Feb' : '02',
                          'Mar' : '03', 'Apr' : '04',
                          'May' : '05', 'Jun' : '06',
                          'Jul' : '07', 'Aug' : '08',
                          'Sep' : '09', 'Oct' : '10',
                          'Nov' : '11', 'Dec' : '12'}
            for monthDict in monthsDict.keys():
                if extractedMonth == monthDict:
                    month = monthsDict[monthDict]
                    formattedDate = splittedDate[0] + '-' + month + '-' + splittedDate[2]
                    break
                else:
                    formattedDate = ''
                    continue
                
            if formattedDate != '':
                return formattedDate
            else:
                return rawRegistrationDate
        else:
            return rawRegistrationDate
    
    def store_cases(self, dataFile, extractedCases):
        for extractedCase in extractedCases:
            uniqueCaseID = uuid.uuid1()
            uniqueCaseIDStr = '{"index":{"_id":"' + str(uniqueCaseID.int) + '"}}'

            extractedCaseString = str(extractedCase)
            extractedCaseString = extractedCaseString.replace("'", '"')

            dataFile.seek(0)
            data = dataFile.read(10)
            if len(data) > 0:
                dataFile.write('\n')
            dataFile.write(uniqueCaseIDStr)
            dataFile.write('\n')
            dataFile.write(extractedCaseString)