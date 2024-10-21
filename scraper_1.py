from bs4 import BeautifulSoup
import requests
from lxml import html
import os


def scrape_article_list(url, page_from, page_to):
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
            open_access_element = row.find('span', class_='u-color-open-access')

            if open_access_element == None:
                continue

            link = row.find('a', class_= "c-card__link u-link-inherit")
            next_url = 'https://www.nature.com/nature' + link["href"]
            next_urls.append(next_url)

        nested_next_urls.append(next_urls)
        next_urls = []
    
    return nested_next_urls
        
def scrape_article_content(url):
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
    article_sections = soup.find_all('div', {'class': 'c-article-section__content'})

    for section in article_sections:
        ids = section.get('id', [])
        # Check if "data-availability-section" is in the section IDs
        if "data-availability-content" in ids:  # {{ edit_1 }}
            #print("Stopping due to data-availability-section found.")
            break  # {{ edit_2 }}
        
        paras = section.find_all("p")

        for para in paras:
            if para:  # Check if the paragraph exists
                text += "*** " + para.get_text(strip=True) + "\n" + "\n"
            else:
                pass

    return text

        
# Example usage:
page_from, page_to = 5, 10
url = 'https://www.nature.com/nature/research-articles?searchType=journalSearch&sort=PubDate&type=article&year=2024'  # Replace with the actual URL
nested_article_urls = scrape_article_list(url, page_from, page_to)

folder_article_name = "scraped_articles"
for i, page_article_urls in enumerate(nested_article_urls):
        if not os.path.exists("scraped_articles"):
            os.makedirs(folder_article_name)

        print("On page:", page_from + i)
        for n, article_url in enumerate(page_article_urls):
            print("     On article:", n + 1)

            text = scrape_article_content(article_url)

            folder_page_name = 'scraped_articles_page_' + str(page_from + i)
            if not os.path.exists(os.path.join(folder_article_name, folder_page_name)):
                os.makedirs(os.path.join(folder_article_name, folder_page_name))
            filename = os.path.join(folder_article_name, folder_page_name, 'article_' + str(page_from + i) + "_" + str(n + 1) + '.txt')
            with open(filename, 'w') as f:
                f.write(text)
