from flask import Flask, render_template, request
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os

app = Flask(__name__)

# --- Cấu hình ---
AFFILIATE_ID = "haudau-aff"
CSV_FILE = 'history.csv'

# --- Hàm gắn mã affiliate ---
def add_affiliate(link):
    parsed = urlparse(link)
    query = parse_qs(parsed.query)
    query['af_lid'] = AFFILIATE_ID
    query['af_siteid'] = AFFILIATE_ID
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse(parsed._replace(query=new_query))
    return new_url

# --- Lấy tên + giá sản phẩm ---
def get_product_info(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # Shopee hiển thị tên trong <title>
        title = soup.title.string.strip() if soup.title else "Không rõ tên"
        
        # Shopee có thể chứa giá ở thẻ meta hoặc script
        price = "Không rõ giá"
        price_meta = soup.find("meta", {"property": "product:price:amount"})
        if price_meta and price_meta.get("content"):
            price = price_meta["content"]
        else:
            # Dự phòng: tìm trong thẻ script JSON
            scripts = soup.find_all("script")
            for script in scripts:
                if '"price":"' in script.text:
                    import json, re
                    json_text = re.search(r'{.*}', script.text)
                    if json_text:
                        data = json.loads(json_text.group())
                        price = data.get("price", price)
                    break

        return title, price
    except Exception as e:
        print(f"Lỗi khi lấy info sản phẩm: {e}")
        return "Không rõ tên", "Không rõ giá"

# --- Lưu vào CSV ---
def save_to_csv(original_link, final_link):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Thời gian', 'Link gốc', 'Link đã tạo'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), original_link, final_link])

# --- Trang chủ ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_link = request.form.get('shopee_link')
        if not original_link:
            return render_template('index.html', error="Vui lòng nhập link Shopee.")

        final_link = add_affiliate(original_link)
        title, price = get_product_info(original_link)
        save_to_csv(original_link, final_link)

        return render_template(
            'preview.html',
            original=original_link,
            result=final_link,
            title=title,
            price=price
        )
    
    now = datetime.now()
    return render_template('index.html', now=now)

# --- Chạy app ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
