from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd


#create a beautiful soup object for a given url
def createSoup(url):
    #get full html of the webpage
    response = requests.get(url)
    html = response.text

    #create beautiful soup object and return it
    soup = BeautifulSoup(html, 'html.parser')
    return soup


#create the url of the webpage that will be interrogated
#using the page number that has been passed
def createUrl(pageNum):
    #https://www.yatco.com/types-of-yachts/new-used-motor-yachts-for-sale/?page_index=1
    link = """https://www.yatco.com/types-of-yachts/new-used-motor-yachts-for-sale/?page_index={0}""".format(pageNum)
    #print(link)
    return link


#function to find all the yachts on a specified web page
def findYachtList(pageNum):
    #create the url of the web page giving the page number
    url = createUrl(pageNum)

    #create selenium web driver to load the web page
    driver = webdriver.Chrome()
    driver.get(url)

    #let page fully load
    time.sleep(10)

    #find all yt-row elements on the web page
    yachts = driver.find_elements(By.CLASS_NAME, "yt-row")
    yachtList = []

    #find list of yachts we are interested in:
    #has to contain at least a single yacht listing
    for y in yachts:
        #get the html of the yt-row and create a beautiful soup object to interrogate it
        html = y.get_attribute('innerHTML')
        soup = BeautifulSoup(html, 'html.parser')

        #find all boat listings
        boats = soup.find_all("div", {"class": "yt-col-12 yt-col-md-6 yt-col-lg-4 col-yacht"})

        #if boat listings have been found, update the yachtList
        if len(boats) > 0:
            yachtList = boats

    #test whether the boats have been found
    return yachtList


#get the url of each listing from it's html
def getUrlOfListing(y):
    #convert html of yacht posting into a string and split it on each new line of html code
    html = str(y)
    htmlSplit = html.split('>')

    #instantiate flag variable and output variable
    urlFound = False
    url = ""

    #for each line in the html code
    for line in htmlSplit:
        #strip the line to get the pure text
        line = line.strip()
        #if the line will contain a link
        if line[0:2] == "<a":
            #the first link found will be the correct link to the listing
            if not urlFound:
                #set the flag and output variable
                urlFound = True
                url = line

    #clean url and return
    url = url.replace("<a href=", "")
    url = url[1:len(url)-1]
    return url


#acquire the information required from each specific listing
def getListingInfo(url):
    soup = createSoup(url)
    #specs = soup.find("div", {"id": "yc-details-specs"})
    specs = soup.find_all("span", {"class": "ycd-specs-loa"})
    count = 1
    specList = []
    for s in specs:
        specList.append(s.text.strip())
        rem = count % 2
        if rem == 0:
            pass
            #specList.append(s.text.rstrip())
            #print(s.text)
        count += 1
    return specList


#get the description of the yacht
def getDescription(url):
    #create beautiful soup object and find the description of the yacht on the web page
    soup = createSoup(url)
    desc = soup.find("div", {"id": "ycd-description"})
    return desc.text.strip()


if __name__ == '__main__':
    #find the first set of yachts
    yachtList = findYachtList(1)

    #choose how many pages to scrape
    #maximum of 288
    #18 yachts per web page
    for i in range(2, 15):
        nextYachtList = findYachtList(i)
        for y in nextYachtList:
            yachtList.append(y)

    #instantiate lists of yacht details
    length = []
    builder = []
    price = []
    built = []
    beam = []
    draft = []
    maxSpeed = []
    cruiseSpeed = []
    cabins = []
    grossTonnage = []
    displacement = []
    location = []
    links = []
    descriptions = []

    #for each individual yacht found
    for yacht in yachtList:
        #get the url, specifications and description of the yacht
        listingUrl = getUrlOfListing(yacht)
        listingInfo = getListingInfo(listingUrl)
        listingDescription = getDescription(listingUrl)

        #add the yacht's details to it's respective list
        length.append(listingInfo[0])
        builder.append(listingInfo[1])
        price.append(listingInfo[2])
        built.append(listingInfo[3])
        beam.append(listingInfo[4])
        draft.append(listingInfo[5])
        maxSpeed.append(listingInfo[6])
        cruiseSpeed.append(listingInfo[7])
        cabins.append(listingInfo[8])
        grossTonnage.append(listingInfo[9])
        displacement.append(listingInfo[10])
        location.append(listingInfo[11])
        links.append(listingUrl)
        descriptions.append(listingDescription)

    #create dictionary of information
    yachtDict = {"length": length, "builder": builder, "price": price, "built": built, "beam": beam, "draft": draft,
                 "max speed": maxSpeed, "cruise speed": cruiseSpeed, "cabins": cabins, "gross tonnage": grossTonnage,
                 "displacement": displacement, "location": location, "link": links, "description": descriptions}

    #create pandas dataframe to store the yacht data
    df = pd.DataFrame(yachtDict)

    #output to excel spreadsheet
    print(df.to_string())
    df.to_excel("yatco yachts.xlsx")
