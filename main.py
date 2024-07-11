from Scraper import homePageScrape

urls = [
    'https://pharmaceutical-journal.com',
    'https://pharmatimes.com',
    'http://www.drugdiscoverytoday.com',
    'https://www.fiercepharma.com',
    'https://www.nature.com/nrd',
    'https://www.biopharmadive.com'
]

rss_urls = [
    'https://www.fiercepharma.com/rss/xml',
    'https://pharmatimes.com/news/rss/',
]

url = 'https://pharmatimes.com/'
scrapeArticles = homePageScrape(url, key='pfizer')
response = scrapeArticles.deepScrape(4)

scrapeArticles.extractAndSave('my_file.txt')
#cleanOutput = scrapeArticle.cleanOutput('html', response)
#scrapeArticle.saveToFile(cleanOutput, 'html')

# print(scrapeArticle.cleanOutput('xml', response))
# article = scrapeArticle.cleanOutput('html', response)
# scrapeArticle.saveToFile(article)
# for art in article:
#     print(art + "\n")
# print(scrapeArticle.checkRSS(response))
# article = scrapeArticle.fetch('rss')
# content = scrapeArticle.cleanString('rss', text=article)
# for text in content:
#     print(text)
