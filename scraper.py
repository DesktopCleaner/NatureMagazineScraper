from bs4 import BeautifulSoup
import requests
from lxml import html
import os

# Scraped articles are saved and organized in folder "scraped_articles"
def scrape_article_list(url, page_from, page_to): # Scrape open access articles' links. Include both starting and ending pages
    nested_next_urls = []
    next_urls = []

    for page in range(page_from, page_to + 1):
        try:
            response = requests.get(f"{url}&page={page}")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f'Failed to retrieve {url} page {page}: {e}')
            continue
        
        if not response.content:
            print(f'No content to download from {url} page {page}')
            continue

        soup = BeautifulSoup(response.content, 'html.parser')
        article_list_rows = soup.find_all('li', {'class': 'app-article-list-row__item'}) 

        for row in article_list_rows:
            open_access_element = row.find('span', class_='u-color-open-access') # Find open access articles

            if open_access_element == None:
                continue

            link = row.find('a', class_= "c-card__link u-link-inherit") # Find link to the article
            next_url = 'https://www.nature.com/nature' + link["href"]
            next_urls.append(next_url)

        nested_next_urls.append(next_urls) # Store all open access articles urls from all pages
        next_urls = []
    
    return nested_next_urls
        
def scrape_article_content(url): # Scrape single articles
    text = ""

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f'Failed to retrieve {url}: {e}')
        return

    if not response.content:
        print(f'No content to download from {url}')
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    article_sections = soup.find_all('div', {'class': 'c-article-section__content'}) # Only scrape content

    for section in article_sections:
        ids = section.get('id', [])

        if "data-availability-content" in ids:
            break  
        
        paras = section.find_all("p") # Find all paragraphs

        for para in paras:
            if para:  # Check if the paragraph exists
                text += "*** " + para.get_text(strip=True) + "\n" + "\n" # Mark paragraphs in saved text files
            else:
                pass

    return text

# Input which year's articles to scrape
year = int(input("Which year's articles to scrape?"))
print("Scraping year:", year)
        
# Input starting and ending pages
page_from, page_to = map(int, input("Type page starting and ending page numbers for scraping:").split())
print("Starting at page:", page_from, ",Ending at page:", page_to)

# Research articles list url
url = 'https://www.nature.com/nature/research-articles?searchType=journalSearch&sort=PubDate&type=article'  

url += "&year=" + str(year) # Link to the specific year's page
nested_article_urls = scrape_article_list(url, page_from, page_to)

folder_name = os.path.join("scraped_articles", str(year))
for i, page_article_urls in enumerate(nested_article_urls):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        print("On page:", page_from + i)
        for n, article_url in enumerate(page_article_urls):
            print("     On article:", n + 1)

            text = scrape_article_content(article_url)

            # file name format: article_pagenum_articlenum
            filename = os.path.join(folder_name, 'article_' + str(page_from + i) + "_" + str(n + 1) + '.txt')
            with open(filename, 'w') as f:
                f.write(text)

print('Scraped articles from page', page_from, "to", page_to, ";", "Year=", year)
