from flask import Flask, render_template, request, redirect, url_for
import csv
from urllib.parse import urlparse, parse_qs, urlencode

app = Flask(__name__)

AFFILIATE_CODE = "haudau-aff"
CSV_FILE = "history.csv"

def shorten_link(original_url):
    parsed = urlparse(original_url)
    if "shopee.vn" not in parsed.netloc:
        return None

    path = parsed.path.rstrip("/")
    new_path = path if path else "/"
    base = f"https://shope.ee{new_path}"

    query = parse_qs(parsed.query)
    query["af_landing"] = ["1"]
    query["aff_sub"] = [AFFILIATE_CODE]

    return f"{base}?{urlencode(query, doseq=True)}"

def save_to_csv(original, short):
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([original, short])

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        link = request.form["link"]
        short_link = shorten_link(link)
        if short_link:
            save_to_csv(link, short_link)
            result = short_link
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
