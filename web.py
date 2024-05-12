from flask import Flask, request , render_template
from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup
import cloudscraper
import requests
scraper = cloudscraper.create_scraper()
app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    global query 
    query = request.form.get('query')
    products_marjane  = []
    products_electroplanet = []
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.set_default_timeout(50000)
        page.goto('https://www.marjane.ma/search/{query}')
        page.wait_for_timeout(5000)
        res = page.locator("css=li.jsx-665482499.jsx-1583737155.list").all()
        for elt in res:
            product = []
            product.append(elt.locator("css=h2.jsx-3277950657.title").inner_text())
            product.append(elt.locator("span.jsx-3054832242.price").inner_text())
            products_marjane.append(product)
        browser.close()
    
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.set_default_timeout(50000)
        page.goto('https://www.electroplanet.ma/recherche?q={query}')
        page.wait_for_timeout(5000)
        res = page.query_selector_all("li.item.product.product-item")
        for elt in res:
            product = []
            product.append(elt.query_selector("a.product-item-link").inner_text())
            if(len(elt.query_selector_all("span.price-wrapper"))>1):
                product.append(elt.query_selector("span.special-price span.price-wrapper").inner_text())
            else:
                product.append(elt.query_selector("span.price-wrapper").inner_text())
            products_electroplanet.append(product)
        browser.close()
    res1 = scraper.get(f'https://www.avito.ma/fr/maroc/{query}')
    res2 = requests.get(f'https://www.marocannonces.com/maroc.html?kw={query}')
    res3 = requests.get(f'https://www.jumia.ma/catalog/?q={query}')
    items1 = []
    items2 = []
    items3 = []
    soup1 = BeautifulSoup(res1.text, 'html.parser')
    soup2 = BeautifulSoup(res2.text, 'html.parser')
    soup3 = BeautifulSoup(res3.text, 'html.parser')
    
    results1 = soup1.find_all("div", class_="sc-b57yxx-1 kBlnTB")
    results2 = soup2.find("div", class_="used-cars")
    results3 = soup3.find_all("article", class_="prd _fb col c-prd")
    


    for result in results1:
        item1 = []
        item1.append(result.find("p", class_="sc-1x0vz2r-0 czqClV").string)
        spans = result.select("span[dir='auto']")
        for span in spans:
            item1.append(span.string.replace(",", ""))
        items1.append(item1)

    for result in results2.select('ul.cars-list li:not(.adslistingpos)'):
        item2 = []
        item2.append(result.select("div.holder h3")[0].string.replace("\r\n","").strip())
        spans = result.select("strong.price")
        for span in spans:
            item2.append(span.string.replace("DH", "").replace(" ", ""))
            
        items2.append(item2)
    for result in results3:
        item3 = []
        spans = result.select("div.info h3.name")
        for span in spans:
            item3.append(span.string)
        spanss = result.select("div.info div.prc")
        for span in spanss:
            item3.append(span.string.replace(",", "").replace("Dhs", "").replace(" ", ""))
        items3.append(item3)
    return render_template('index.html', data1=items1,data2=items2,data3=items3,data4=products_marjane,data6=products_electroplanet,flag=1,query=query)


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')






