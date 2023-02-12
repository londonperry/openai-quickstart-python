import os
import openai
from bs4 import BeautifulSoup
import requests
from flask import Flask, render_template, request, redirect, url_for
import urllib.parse as urlparse

def summarize_url(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    p_tags = soup.find_all("p")
    text = '\n'.join([p.text for p in p_tags])

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Please summarize the contents of the URL: {url}\n\n{text}",
        temperature=0.5,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    return response.choices[0].text

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        url = request.form["url"]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        parsed_url = urlparse.urlparse(url)
        domain = parsed_url.hostname.split(".")[-2].upper()
        title = soup.find("h1").text.strip()
        summary = summarize_url(url)
        response = f"Source: {domain}\n.Article Title: {title}\n\n.{summary}"
        return redirect(url_for("index", result=response))

    result = request.args.get("result")
    return render_template("index.html", result=result)
