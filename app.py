from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os

app = Flask(__name__)

# Cấu hình Affiliate mặc định
AFFILIATE_ID = "haudau-aff"  # 👉 Thay bằng mã affiliate của bạn nếu có
CSV_FILE = 'history.csv'

# Hàm xử lý gắn affiliate vào link Shopee
def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

# Hàm lấy thông tin sản phẩm Shopee (tên + giá)
def get_product_info(link):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        resp = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')

        title_tag = soup.find("title")
        title = title_tag.text.replace(" | Shopee Việt Nam", "").strip() if title_tag else "Không rõ"

        price_tag = soup.find("div", class_="pmm-price") or soup.find("div", class_="pqTWkA")
        price = price_tag.text.strip() if price_tag else "Không rõ"

        return title, price
    except Exception as e:
        print(f"Lỗi lấy thông tin sản phẩm: {e}")
        return "Không rõ", "Không rõ"

# Hàm lưu vào CSV
def save_to_csv(original_link, final_link):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link đã tạo'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_link, final_link])

# Trang chính
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_link = request.form.get('shopee_link')
        if not original_link:
            return render_template('index.html', error="Vui lòng nhập link Shopee.", now=datetime.now())

        final_link = add_affiliate(original_link)
        product_name, product_price = get_product_info(original_link)

        save_to_csv(original_link, final_link)

        return render_template(
            'preview.html',
            original=original_link,
            result=final_link,
            name=product_name,
            price=product_price,
            now=datetime.now()
        )
    return render_template('index.html', now=datetime.now())

# Chạy đúng cổng của Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
