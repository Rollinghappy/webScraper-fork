# Website Scraper

## How to set up

- Clone the repository.
- Create a new python virtual environment
- Activate the virtual environment
- Run `pip install -r requirements.txt`

## Configuration
The scraper uses a config.json file to manage parsing configurations for different websites. 
This JSON file should contain parsing rules for each supported website, including CSS selectors for extracting data.

# Example Usage
Create an instance of the Scraper class by providing a URL and a keyword (optional)

```
url = 'https://www.fiercepharma.com/pharma/sarepta-duchenne-elevidys-label-expansion-fda-decision'
scrapeArticle = Scraper(url, key='pfizer')
response = scrapeArticle.fetch('html')
cleanOutput = scrapeArticle.cleanOutput('html', response)
scrapeArticle.saveToFile(cleanOutput, 'html')
```

__A configuration for the website must be in the config.json file.__

## Modes Supported

- HTML
  - This mode is used for fetching and parsing HTML content from a given webpage.
  The HTML content is parsed using BeautifulSoup based on the configuration specified in the config.json file for the specific website.
  Example usage: Fetching an article from a news website.
- Homepage
  - This mode is used for fetching and parsing the main page or homepage of a website.
    The scraper looks for specific elements on the homepage based on the configuration specified in the config.json file.
    It extracts links from specified parent elements and returns a list of absolute URLs.
- Search
  - This mode is used for performing a search on a website and parsing the search results.
    The scraper constructs a search URL using the search term (provided as key) and the URL pattern specified in the config.json file.
    It extracts and returns a list of links from the search results.
- XML
  - This mode is used for fetching and parsing XML content, such as RSS feeds.
    The XML content is parsed using BeautifulSoup based on the configuration specified in the config.json file for the specific website.
    The parsed content is cleaned to remove XML tags and other unwanted characters.

## Breakdown of Class Methods
 - fetch(type: str): Determines the mode and fetches the data using either fetchRequest or fetchURLlib based on the response status code.
    Calls parseResponse to parse the fetched content.


- fetchRequest(headers: dict, type: str): Uses the requests library to perform an HTTP GET request.
    Constructs the search URL if the type is search.


- fetchURLlib(headers: dict, type: str): Uses the urllib library to perform an HTTP GET request.
    Constructs the search URL if the type is search.


- parseResponse(response: str, type: str): Parses the fetched HTML or XML content using BeautifulSoup.
    Handles parsing based on the specified type (html, homepage, search, xml).


- checkRSS(response): Searches for RSS feed links in the HTML content.
    Returns a dictionary indicating whether RSS links were found and the links themselves.


- createLink(url: str, links: list): Generates absolute URLs from relative links found during parsing.


- searchRssLink(response, element: str): Searches for RSS feed links within specified HTML elements.


- cleanOutput(type: str, response: dict): Cleans the parsed HTML or XML content, removing unnecessary tags and whitespace.


- saveToFile(parsedOutput: dict, type: str): Saves the cleaned output to a file.