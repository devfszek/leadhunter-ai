from flask import Flask, render_template, request
from scraper import buscar_leads

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    leads = []

    if request.method == "POST":
        busca = request.form["busca"]

        leads = buscar_leads(busca)

    return render_template("index.html", leads=leads)

if __name__ == "__main__":
    app.run(debug=True)