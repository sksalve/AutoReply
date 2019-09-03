import requests
import json
from bs4 import BeautifulSoup
import os
import csv
# API url
# url = "https://footballapi.pulselive.com/football/players"
url = "https://targetstudy.com/school/schools-in-mumbai.html?recNo={}"

fields = []
# Headers required for making a GET request
# It is a good practice to provide headers with each request.
headers = {
    "content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "DNT": "1",
    "Origin": "https://targetstudy.com",
    "Referer": "https://targetstudy.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36"
}

# Query parameters required to make get request
queryParams = {
    "pageSize": 32,
    "compSeasons": 274,
    "altIds": True,
    "page": 0,
    "type": "player",
    "id": -1,
    "compSeasonId": 274
}

# Sending the request with url, headers, and query params

all_titles = []
address_1 = []
address_2 = []
address_3 =[]
page_no =25
while page_no < 50:
    response = requests.get(url = url.format(page_no), headers = headers, params=queryParams)
    # if response status code is 200 OK, then
    if response.status_code == 200:
        # load the json data
        page = response.content
        soup = BeautifulSoup(page, 'html5lib')

        titles = []
        for title in soup.find_all('h2', class_ = "heading1"):
            f = title.text
            titles.append(f) 

        # print(titles)
        all_titles.extend(titles)

        address1= []
        address2= []
        address3= []
        # addrs = []
        for addr in soup.find_all('td'):
            address = addr.text.split('Maharashtra')[0]
            str1 = address.split(',')
            l = len(str1)
            if l ==3:
                s1 = str1[0]
                s2 = str1[1]
                s3 = str1[2]
                address1.append(s1)
                address2.append(s2)
                address3.append(s3)
            elif l==2:
                s1 = str1[0]
                s2 = str1[1]
                address1.append(s1)
                # address2.append(s2)
                # address3.append(s3)
            elif l ==1:
                s1 = str1[0]
            else:
                s1 = str1[0]
                s2 = str1[1]
                s3 = str1[2]
                address1.append(s1)
                address2.append(s2)
                address3.append(s3)

        address_1.extend(address1)
        address_2.extend(address2)
        address_3.extend(address3)

           
        # all_addr.extend(addrs)

    page_no +=25
    print(page_no)


header = ['Name of School', 'address1', 'address2', 'address3']
fields.append((all_titles, address_1, address_2, address_3))

print(fields)


csvfile = 'list_of_school.csv'

with open(csvfile, 'a', newline='') as f:
    csvwriter = csv.writer(f)
    if os.stat(csvfile).st_size == 0:
        csvwriter.writerow(header)
    csvwriter.writerow(fields)
