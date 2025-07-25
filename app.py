from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
import csv
import os
from datetime import datetime

app = Flask(__name__)
AFFILIATE_ID = "haudau-aff"
CSV_FILE = "history.csv"

# Gắn mã affiliate vào link Shopee
def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

# Lấy tên và giá sản phẩm từ trang Shopee
def get_product_info(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string if soup.title else "Không lấy được tên sản phẩm"
        name = title.split(" | ")[0] if " | " in title else title.strip()
        price_tag = soup.find("div", class_="pmmxKx") or soup.find("div", class_="pqTWkA")
        price = price_tag.text.strip() if price_tag else "Không rõ"
        return name, price
    except:
        return "Không lấy được tên sản phẩm", "Không rõ"

# Lưu lịch sử vào CSV
def save_to_csv(original, final):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Thời gian", "Link gốc", "Link đã tạo"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original, final])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original = request.form.get("shopee_link")
        if not original:
            return render_template("index.html", error="Vui lòng nhập link Shopee.")
        final = add_affiliate(original)
        name, price = get_product_info(original)
        save_to_csv(original, final)
        return render_template("preview.html", original=original, result=final, name=name, price=price, now=datetime.now())
    return render_template("index.html", now=datetime.now())

if __name__ == "__main__":
    app.run(debug=True)

# --- Chạy app ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
