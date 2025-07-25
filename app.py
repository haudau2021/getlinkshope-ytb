from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os

app = Flask(__name__)

# --- Cấu hình ---
AFFILIATE_ID = "haudau-aff"  # 👈 Sửa nếu cần
CSV_FILE = "history.csv"

# --- Gắn mã affiliate ---
def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

# --- Lấy thông tin sản phẩm ---
def get_product_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        title_tag = soup.find("title")
        name = title_tag.text.strip().replace(" | Shopee Việt Nam", "") if title_tag else "Không tìm thấy"

        price_tag = soup.find("div", class_="pqTWkA")
        price = price_tag.text.strip() if price_tag else "Không rõ"

        return name, price
    except:
        return "Không tìm thấy", "Không rõ"

# --- Lưu vào file CSV ---
def save_to_csv(original, final, name, price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link rút gọn', 'Tên sản phẩm', 'Giá'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original, final, name, price])

# --- Trang chính ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original = request.form.get("shopee_link")
        if not original:
            return render_template("index.html", error="Vui lòng nhập link Shopee.")

        final_link = add_affiliate(original)
        name, price = get_product_info(original)
        save_to_csv(original, final_link, name, price)

        return render_template("preview.html", original=original, result=final_link, name=name, price=price)

    return render_template("index.html")

# --- Chạy trên Render ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
