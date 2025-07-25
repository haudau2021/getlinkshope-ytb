from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import csv
from datetime import datetime
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# === Cấu hình ===
AFFILIATE_ID = "haudau-aff"
CSV_FILE = "history.csv"

# === Hàm gắn affiliate vào link ===
def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

# === Hàm lưu thông tin vào CSV ===
def save_to_csv(original, final, name, price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Thời gian", "Link gốc", "Link đã tạo", "Tên SP", "Giá SP"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            original, final, name, price
        ])

# === Lấy thông tin sản phẩm Shopee ===
def get_product_info(link):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find("title")
        name = title_tag.text.strip() if title_tag else "Không rõ"

        price_meta = soup.find("meta", property="product:price:amount")
        price = price_meta["content"] if price_meta else "Không rõ"

        image_meta = soup.find("meta", property="og:image")
        image = image_meta["content"] if image_meta else None

        return name, price, image
    except Exception as e:
        print("Lỗi khi lấy thông tin sản phẩm:", e)
        return "Không rõ", "Không rõ", None

# === Trang chính ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original = request.form.get("shopee_link")
        if not original:
            return render_template("index.html", error="Vui lòng nhập link Shopee.", now=datetime.now())

        final = add_affiliate(original)
        name, price, image = get_product_info(original)
        save_to_csv(original, final, name, price)
        return render_template("preview.html", original=original, result=final, name=name, price=price, image=image)

    return render_template("index.html", now=datetime.now())

# === Khởi chạy Flask App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
