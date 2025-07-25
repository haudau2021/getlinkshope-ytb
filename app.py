from flask import Flask, render_template, request

app = Flask(__name__)

# Cấu hình affiliate ID ở đây
AFFILIATE_ID = "ABC123"  # 👉 Thay mã affiliate của bạn vào đây

# Hàm tự động thêm affiliate ID vào link Shopee
def add_affiliate(link):
    if "shopee.vn" not in link:
        return None  # Không xử lý nếu không phải link Shopee
    if "?" in link:
        return link + f"&affiliate_id={AFFILIATE_ID}"
    else:
        return link + f"?affiliate_id={AFFILIATE_ID}"

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_link = request.form.get("shopee_link")
        final_link = add_affiliate(original_link)
        if final_link:
            return render_template("preview.html", link=final_link)
        else:
            return "⛔ Vui lòng nhập link Shopee hợp lệ.", 400
    return render_template("index.html")

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
