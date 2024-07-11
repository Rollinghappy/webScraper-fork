import html
import json
import re
import urllib.request
from urllib.parse import urlparse
import chardet
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

config_file = open('config.json')
parser_configs = json.load(config_file)
config_file.close()


class Scraper:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.google.com/'
    }

    def __init__(self, url, key):
        self.url = url
        self.key = key

    def fetch(self, type: str):
        response = self.fetchRequest(self.headers, type)
        if response.status_code >= 400:
            response = self.fetchURLlib(self.headers, type)
        else:
            response = response.content.decode(response.apparent_encoding)
        return self.parseResponse(response, type)

    def fetchRequest(self, headers: dict, type=""):
        if type == 'search':
            searchUrl = parser_configs[urlparse(self.url).netloc][type]['url']
            searchUrl = searchUrl.format(self.key)
            response = requests.get(searchUrl, headers=headers)
            return response
        response = requests.get(self.url, headers=headers)
        return response

    def fetchURLlib(self, headers: dict, type=""):
        searchUrl = self.url
        if type == 'search':
            searchUrl = parser_configs[urlparse(self.url).netloc][type]['url']
            searchUrl = searchUrl.format(self.key)
        request = urllib.request.Request(searchUrl)

        for header in headers:
            request.add_header(header, headers[header])
        with urllib.request.urlopen(request) as response:
            raw_data = response.read()
            detected_encoding = chardet.detect(raw_data)['encoding']
            encoding = detected_encoding if detected_encoding else 'utf-8'
            content = raw_data.decode(encoding)
            return content

    def parseResponse(self, response, type: str):
        parsedResponse = {}
        baseURL = urlparse(self.url).netloc
        if type == 'html':
            soup = BeautifulSoup(response, 'html5lib')
            config = parser_configs[baseURL]
            for tag in config:
                if tag in ['rss_config', 'homepage', 'search','deep-scrape']:
                    continue
                try:
                    parsedResponse[tag] = soup.find_all(class_=config[tag])[0]
                except:
                    parsedResponse[tag] = ''

        elif type == 'homepage' or type == 'search':
            soup = BeautifulSoup(response, 'html5lib')
            config = parser_configs[baseURL]
            tags = soup.select(config[type]['parent'] + " > " + config[type]['element'])
            links = []
            for tag in tags:
                links.append(tag['href'])
            return self.createLink(self.url, links)

        elif type == 'xml':
            temp = {}
            soup = BeautifulSoup(response, 'xml')
            rss_config = parser_configs[baseURL]['rss_config']
            tag = ''
            if rss_config:
                for tag in rss_config:
                    temp[tag] = soup.find_all(rss_config[tag])

            for i in range(len(temp[tag])):
                parsedResponse[i] = {}
                for tag in rss_config:
                    try:
                        parsedResponse[i][tag] = temp[tag][i]
                    except KeyError:
                        continue

        return parsedResponse

    def checkRSS(self, response):
        elements = ['a', 'span', 'div']
        links = []
        for element in elements:
            links += self.searchRssLink(response, element)

        links = self.createLink(self.url, links)

        if len(links) == 0:
            return {
                "rssFound": False
            }
        else:
            return {
                "rssFound": True,
                "links": links
            }

    @staticmethod
    def createLink(url: str, links: list):
        fullLinks = []
        httpRegex = 'https?'
        regexString = re.compile(httpRegex)
        for link in links:
            if regexString.match(link):
                fullLinks.append(link)
            else:
                scheme = urlparse(url).scheme
                baseURL = urlparse(url).netloc
                fullLinks.append(scheme + "://" + baseURL + link)
        return fullLinks

    @staticmethod
    def searchRssLink(response, element: str):
        rssRegex = 'rss(\s?feeds?)?'
        regexString = re.compile(rssRegex, re.IGNORECASE)
        links = []
        hrefs = response.find_all(element, string=regexString)
        for url in hrefs:
            try:
                links.append(url['href'])
            except KeyError:
                parent = url.find_parent()
                links.append(parent['href'])

        return links

    @staticmethod
    def cleanOutput(type: str, response: dict):
        if response is None:
            response = {}
        cleanOutput = {}
        if type == 'html':
            for key in response:
                cleanOutput[key] = ''
                for string in response[key]:
                    if string == '\n':
                        continue
                    string = string.text
                    cleanOutput[key] += string + '\n'
                    cleanOutput[key] = re.sub(r'^\s+|\s+$', '\n', cleanOutput[key], flags=re.MULTILINE)
                    cleanOutput[key] = re.sub(r'(\n\s*){2,}', '\n', cleanOutput[key])
                    cleanOutput[key] = re.sub(r'waitToLoadAds\.push\(function\(\) {[\s\S]*?}\);', '', cleanOutput[key])

        elif type == 'xml':
            regex = re.compile(r'<[^>]+>')
            for id in response:
                cleanOutput[id] = {}
                for tag in response[id]:
                    decoded_text = html.unescape(str(response[id][tag]))
                    cleanOutput[id][tag] = re.sub(regex, '', decoded_text)
                    cleanOutput[id][tag] = re.sub(r'\n+', '\n', cleanOutput[id][tag])

        return cleanOutput

    @staticmethod
    def saveToFile(parsedOutput: dict, type: str, fileName : str, mode : str):
        if type == 'html':
            with open(fileName, mode) as f:
                for key in parsedOutput:
                    f.write(key + ": " + parsedOutput[key] + '\n')
            f.close()

        elif type == 'xml':
            with open(fileName, mode) as f:
                for id in parsedOutput:
                    f.write(str(id) + '\n')
                    for key in parsedOutput[id]:
                        f.write(key + ": " + parsedOutput[id][key] + '\n')
                    f.write('\n')
            f.close()


class homePageScrape:

    def __init__(self, url, key):
        self.url = url
        self.key = key

    def deepScrape(self,count):

        path = Service(r"C:\Users\fnafb\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(service=path, options=options)


        baseURL = urlparse(self.url).netloc
        config = parser_configs[baseURL]['deep-scrape']
        website = config['link']
        driver.get(website)
        
        scrapedLinks=[]

        for i in range(count):
            allArticles = driver.find_elements(By.XPATH,config['parent'])


            for article in allArticles:
                link_tag = article.find_element(By.TAG_NAME, config['href'])
                href = link_tag.get_attribute('href')
                scrapedLinks.append(href)


            nextButton = driver.find_element(By.XPATH,config['next'])

            if(config['next-type']=='link'):
                nextLink = nextButton.get_attribute('href')
                driver.get(nextLink)
            else:
                nextButton.click()
        self.scrapedLinks = scrapedLinks
        return scrapedLinks
    
    def extractAndSave(self, fileName):
        links = self.scrapedLinks

        for url in links:
            scrapeArticle = Scraper(url, key='pfizer')
            response = scrapeArticle.fetch('html')
            cleanOutput = scrapeArticle.cleanOutput('html', response)
            scrapeArticle.saveToFile(cleanOutput, 'html', fileName, 'a')
            del scrapeArticle
        print('extraction successful and saved to file '+ fileName)