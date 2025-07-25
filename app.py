from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create():
    title = request.form['title']
    image = request.form['image']
    affiliate_link = request.form['affiliate_link']
    return render_template('preview.html', title=title, image=image, link=affiliate_link)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
