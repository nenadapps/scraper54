from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

base_url = 'https://scindedawk.com'

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url, category):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('h1.h2')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      
    
    try:
        raw_text = html.select('.product-description')[0].get_text().strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
        
    try:
        price = html.select('#productPrice-product-template .visually-hidden')[-1].get_text().strip()
        price = price.replace('$', '').strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
        
    try:
        sold = 0
        sold_href = html.find_all('link', attrs={'itemprop':'availability'})[0].get('href')
        if 'OutOfStock' in sold_href:
            sold = 1
        stamp['sold'] = sold
    except:
        stamp['sold'] = None          
    
    stamp['category'] = category      

    stamp['currency'] = 'USD'
    
    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.product-photo-thumb')
        for image_item in image_items:
            img_temp = image_item.get('href').replace('//', 'https://')
            img_parts = img_temp.split('?')
            img = img_parts[0]
            if img not in images:
                images.append(img)
                
        if not len(images):
            image_item = html.select('#productPhotoImg')[0]
            if image_item:
                img_temp = image_item.get('src').replace('//', 'https://')
                img_parts = img_temp.split('?')
                img = img_parts[0]
                if img not in images:
                    images.append(img)
            
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):

    items = []
    next_url = ''
    
    try:
        html = get_html(url)
    except:
        return items, next_url
    
    try:
        for item in html.select('.product-grid-item'):
            item_link = base_url + item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_url_cont = html.find_all('link', attrs={'rel':'next'})[0]
        next_url_href = next_url_cont.get('href')
        if next_url_href:
            next_url = base_url + next_url_href
    except:
        pass
    
    shuffle(items)
    
    return items, next_url

def get_categories():
    
    items = {}

    try:
        html = get_html(base_url)
    except:
        return items

    try:
        item_cont = html.select('.site-nav--dropdown')[-1]
        for item in item_cont.select('li a'):
            item_href = item.get('href')
            item_link = base_url + item_href
            item_text = item.get_text().strip()
            if item_link not in items: 
                items[item_text] = item_link
    except: 
        pass
    
    return items

categories = get_categories()  
for key in categories:
    print(key + ': ' + categories[key])   

selected_category = input('Choose category: ')

page_url = categories[selected_category]
while(page_url):
    page_items, page_url = get_page_items(page_url)
    for page_item in page_items:
        stamp = get_details(page_item, selected_category) 
