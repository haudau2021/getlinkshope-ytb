from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
import csv
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

AFFILIATE_ID = "haudau-aff"
CSV_FILE = 'history.csv'

def resolve_redirect(short_url):
    try:
        response = requests.head(short_url, allow_redirects=True, timeout=5)
        return response.url
    except Exception:
        return short_url

def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def save_to_csv(original_link, final_link):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link đã tạo'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_link, final_link])

def get_product_info(link):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("title").text.strip() if soup.find("title") else "Không tìm thấy"
        price_tag = soup.find("meta", property="product:price:amount")
        price = f"{int(float(price_tag['content'])):,.0f} VND" if price_tag else "Không rõ"

        return title, price
    except Exception:
        return "Không tìm thấy", "Không rõ"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get("shopee_link")
        if not link:
            return render_template("index.html", error="Vui lòng nhập link.", now=datetime.now())

        original_link = resolve_redirect(link)
        affiliate_link = add_affiliate(original_link)
        product_name, price = get_product_info(original_link)
        save_to_csv(original_link, affiliate_link)

        return render_template("preview.html",
                               original=original_link,
                               result=affiliate_link,
                               product=product_name,
                               price=price,
                               now=datetime.now())
    return render_template("index.html", now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)
