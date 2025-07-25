from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import csv, os
import requests
from bs4 import BeautifulSoup
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

def save_to_csv(original, affiliate):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link Affiliate'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original, affiliate])

def resolve_redirect(link):
    try:
        res = requests.get(link, allow_redirects=True, timeout=5)
        return res.url
    except:
        return link

def get_product_info(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')

        title = soup.find('title')
        product_name = title.text.strip() if title else "Không tìm thấy"

        price_tag = soup.find("div", class_="pmmZf2") or soup.find("div", class_="pqTWkA")
        price = price_tag.text.strip() if price_tag else "Không rõ"

        return product_name, price
    except:
        return "Không tìm thấy", "Không rõ"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        link = request.form.get("shopee_link")
        if not link:
            return render_template("index.html", error="Vui lòng nhập link.")

        original_link = resolve_redirect(link)
        affiliate_link = add_affiliate(original_link)
        product_name, price = get_product_info(original_link)
        save_to_csv(original_link, affiliate_link)

        return render_template("preview.html",
                               original=original_link,
                               result=affiliate_link,
                               product=product_name,
                               price=price)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


# --- Chạy trên Render ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
