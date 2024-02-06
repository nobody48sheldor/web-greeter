import os
from flask import Flask, render_template, request, url_for, redirect
import requests
import openai
import sys
from datetime import date 
from datetime import timedelta
import newspaper
import subprocess
import tempfile

today = date.today()
yesterday = str(today - timedelta(days = 3))

openai.organization = "" # for https://openai.com/

client = openai.OpenAI()

today = date.today()
yesterday = str(today - timedelta(days = 3))

API_KEY = "" # for https://newsapi.org/

query="world and tech news"

def get_news(query):
    Url = url+"?q="+query+"&from="+yesterday+"&sortBy=popularity&apiKey="+API_KEY
    r = requests.get(Url)
    R = r.json()
    news = []

    for i in R["articles"]:
        news.append((i["title"], i["description"], i["url"]))

    latest = []
    for j in range(5):
        latest.append(news[j])
    return(latest)

def summary_plz(url):
    article = newspaper.Article(url, language="en")

    article.download()
    article.parse()
    text = article.text

    text = text.replace('"', ' ')
    text = text.replace("'", ' ')
    text = text.replace("’", ' ')
    text = text.replace("‘", ' ')
    text = text.replace("$", ' ')
    text = text.replace("%", ' in pourcent ')
    text = text.replace("“", ' ')
    text = text.replace("”", ' ')
    text = text.replace("\n", ' ')

    print(text)



    cmd = """curl http://localhost:11434/api/generate -d '{"model": "mistral", "prompt": " """ + "sumarize in less than 100 words the following text : " + text + """ ", "stream": false }'"""

    print()
    #print(cmd)
    print()

    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(cmd, stdout=tempf,shell=True)
        proc.wait()
        tempf.seek(0)
        print()
        m = str(tempf.read())[80:]
        print(m)
        print()

    m_ = ""
    for i in m:
        if i != '"':
            m_ += i
        else:
            break

    print()
    print(m_)

    m=m_

    path = os.getcwd()
    speech_file_path = path+"speech.mp3"
    response = client.audio.speech.create(model="tts-1", voice="alloy", input=m)

    response.stream_to_file(speech_file_path)
    os.system("mpv "+ speech_file_path)
    return 0

latest = get_news(query)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()

@app.route("/")
def home():
    return(render_template("index.html"))

@app.route("/", methods=["GET", "POST"])
def search():
    value = request.form["searched"]
    return(redirect("https://www.google.com/search?client=firefox-b-d&q={}".format(value)))

@app.route("/news")
def news():
    return(render_template("news.html", value=latest))

@app.route("/news", methods=["GET", "POST"])
def topic_news():
    value_topic = request.form.get("topic",None)
    value_summary = request.form.get("summary",None)
    if value_topic:
        print(value_topic)
        l= get_news(value_topic)
        return(render_template("news.html", value=l))
    if value_summary:
        print(value_summary)
        summary_plz(value_summary)
    return(render_template("news.html", value=latest))

if __name__ == "__main__":
    app.run(debug=True)
