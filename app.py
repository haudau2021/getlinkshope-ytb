from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
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
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

def get_product_info(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        name = soup.find("title").text.strip()
        price_tag = soup.find("meta", {"itemprop": "price"})
        price = price_tag["content"] if price_tag else "Không rõ"
        return name, price
    except Exception as e:
        return "Không lấy được tên", "Không rõ"

def save_to_csv(original_link, final_link):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Thời gian", "Link gốc", "Link đã tạo"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_link, final_link])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_link = request.form.get("shopee_link")
        if not original_link:
            return render_template("index.html", error="Vui lòng nhập link Shopee.")

        final_link = add_affiliate(original_link)
        save_to_csv(original_link, final_link)
        name, price = get_product_info(original_link)
        return render_template("preview.html", original=original_link, result=final_link, name=name, price=price)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)