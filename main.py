# Import libraries
import ssl
import json
import time
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # A new automatic driver management library.

with open('urls.txt', 'w+') as url:
    ctx = ssl.create_default_context()                # ssl-This module provides access to Transport Layer Security.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # initialise
    final_dict = {}
    a = 0
    # Driver arguments
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager(path=r'bin').install(), options=options)

    def scrape_urls():
        product = input("Input product:-")
        product = product.replace(" ", "+")
        products = 'https://www.amazon.com/s?k='+product
        driver.get(products)
        req = urllib.request.Request(products, data=None, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'})
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for links in soup.findAll('a', attrs={'class': 'a-link-normal a-text-normal'}):
            url.write(links['href']+"\n")
    scrape_urls()
with open('urls.txt', 'r') as url:
    for urls in url:
        a += 1
        product_json = {}
        # Driver call
        final_url = "https://www.amazon.com"+urls
        driver.get(final_url)
        time.sleep(5)
        req = urllib.request.Request(final_url, data=None, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        })
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # Defining functions
        def scrape(soup):
            for spans in soup.findAll('span', attrs={'id': 'productTitle'}):
                name_of_product = spans.text.strip()
                product_json['name'] = name_of_product
                break
            for divs in soup.findAll('div'):
                try:
                    price = str(divs['data-asin-price'])
                    product_json['price'] = '$' + price
                    break
                except:
                    product_json['price'] = ''
            for divs in soup.findAll('div', attrs={'id': 'rwImages_hidden'}):
                for img_tag in divs.findAll('img', attrs={'style': 'display:none;'}):
                    product_json['img-url'] = img_tag['src']
                    break
            for i_tags in soup.findAll('i', attrs={'data-hook': 'average-star-rating'}):
                for spans in i_tags.findAll('span', attrs={'class': 'a-icon-alt'}):
                    product_json['star-rating'] = spans.text.strip()
                    break
            for spans in soup.findAll('span', attrs={'id': 'acrCustomerReviewText'}):
                if spans.text:
                    review_count = spans.text.strip()
                    product_json['customer-reviews-count'] = review_count
                    break
            product_json['details'] = []
            for ul_tags in soup.findAll('ul', attrs={'class': 'a-unordered-list a-vertical a-spacing-none'}):
                for li_tags in ul_tags.findAll('li'):
                    for spans in li_tags.findAll('span', attrs={'class': 'a-list-item'}, text=True,recursive=False):
                        product_json['details'].append(spans.text.strip())
            product_json['short-reviews'] = []
            for a_tags in soup.findAll('a',attrs={'class':'a-size-base a-link-normal review-title a-color-base a-text-bold'}):
                short_review = a_tags.text.strip()
                product_json['short-reviews'].append(short_review)
            product_json['long-reviews'] = []
            for divs in soup.findAll('div', attrs={'data-hook': 'review-collapsed'}):
                long_review = divs.text.strip()
                product_json['long-reviews'].append(long_review)
            final_dict[a]= product_json
            return  final_dict
        #calling functions
        scrape(soup)

        #Storing data in JSON
        with open('product.json', 'w+') as outfile:
            json.dump(final_dict, outfile, indent=4)
    print('----------script has been executed successfully.----------')