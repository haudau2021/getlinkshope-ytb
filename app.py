from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import csv
import os
import requests
from datetime import datetime

app = Flask(__name__)
AFFILIATE_ID = "haudau-aff"
CSV_FILE = 'history.csv'

def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def save_to_csv(original_link, final_link, name, price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link đã tạo', 'Tên SP', 'Giá'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_link, final_link, name, price])

def get_product_info(link):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.title.string if soup.title else "Không rõ tên sản phẩm"
        og_title = soup.find("meta", property="og:title")
        og_price = soup.find("meta", property="product:price:amount")
        og_image = soup.find("meta", property="og:image")

        name = og_title["content"] if og_title else title.strip()
        price = og_price["content"] + " VND" if og_price else "Không rõ"
        image = og_image["content"] if og_image else ""

        return name, price, image
    except Exception as e:
        print("Lỗi khi lấy thông tin:", e)
        return "Không rõ", "Không rõ", ""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_link = request.form.get('shopee_link')
        if not original_link:
            return render_template('index.html', error="Vui lòng nhập link Shopee.")

        final_link = add_affiliate(original_link)
        name, price, image = get_product_info(original_link)
        save_to_csv(original_link, final_link, name, price)

        return render_template('preview.html', original=original_link, result=final_link, name=name, price=price, image=image)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
