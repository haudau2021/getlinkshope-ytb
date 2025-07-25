from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import csv
import os

app = Flask(__name__)

AFFILIATE_ID = "haudau-aff"
CSV_FILE = "history.csv"

def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query["af_lid"] = AFFILIATE_ID
    query["af_siteid"] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def get_product_info(link):
    try:
        session = requests.Session()
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = session.head(link, headers=headers, allow_redirects=True, timeout=10)
        real_url = resp.url

        res = session.get(real_url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "Không rõ"

        price_tag = soup.find("meta", property="product:price:amount")
        price = price_tag["content"] if price_tag else "Không rõ"

        return title, price
    except Exception as e:
        print(f"Lỗi khi lấy thông tin sản phẩm: {e}")
        return "Không rõ", "Không rõ"

def save_to_csv(original, affiliate):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Thời gian", "Link gốc", "Link đã gắn Affiliate"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original, affiliate])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_link = request.form.get("shopee_link")
        if not original_link:
            return render_template("index.html", error="Vui lòng nhập link Shopee.")

        final_link = add_affiliate(original_link)
        title, price = get_product_info(original_link)
        save_to_csv(original_link, final_link)

        return render_template("preview.html",
                               original=original_link,
                               result=final_link,
                               title=title,
                               price=price,
                               now=datetime.now())
    return render_template("index.html", now=datetime.now())

# === Khởi chạy Flask App ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)
