import yake
from keybert import KeyBERT
from bs4 import BeautifulSoup as bs
import requests
import re
from difflib import SequenceMatcher
from flask import *
import os.path
import pathlib
from flask import Flask, session, abort, redirect, request
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from PIL import Image
import PyPDF2
import pytesseract

app = Flask("Google Login App")
app.secret_key = "SIH2022AI"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "824135687740-s7siaanvlm13t1ak8ko50dsg0nf1eijq.apps.googleusercontent.com"
client_secrets_file = os.path.join(
    pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request = token_request,
        audience = GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/upload")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return render_template("index.html")


@ app.route('/upload')
def upload():
    return render_template("upload.html")


@app.route("/success", methods=["GET", "POST"])
@login_is_required
def check_plag():
    if request.method == 'POST':
        f = request.files['file']
        inp_txt = ''
        if('.txt' in str(f)):
            inp_txt = f.read()
            
        if('.pdf' in str(f)):
            pdfReader = PyPDF2.PdfFileReader(f)
            for i in range(pdfReader.numPages):
                inp_txt += str(pdfReader.getPage(i).extractText())
        
        if('.png' in str(f)):
            path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            image_path = r"C:/Finalday/img2.png"
            img = Image.open(image_path)
            pytesseract.tesseract_cmd = path_to_tesseract
            text = pytesseract.image_to_string(img)
            inp_txt = text[:-1]
            

        language = "en"
        max_ngram_size = 3
        deduplication_threshold = 0.05
        numOfKeywords = 20
        kw_model = KeyBERT()

        custom_kw_extractor = yake.KeywordExtractor(
            lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(inp_txt)

        keywords += kw_model.extract_keywords(str(inp_txt))

        def get_key(val):
            for key, value in plag_score.items():
                if val == value:
                    return key
        
        plag_score = {}

        for title in keywords:

            regex = re.compile(r'<[^>]+>')

            url = [r"https://en.wikipedia.org/wiki/", r"https://www.britannica.com/topic/", r"https://deletionpedia.org/en/",
                   r"https://en.citizendium.org/wiki/", r"https://www.infoplease.com/encyclopedia/science/engineering/computer/"]

            for site in url:
                if 'wikipedia' or 'deletionpedia' or 'citizendium' in site:
                    site = site+title[0].capitalize().replace(' ', '_')
                elif 'britannica' or 'encyclopedia' in site:
                    site = site+title[0].replace(' ', '-')

                result = requests.get(site)
                doc = bs(result.text, "html.parser")

                str_htm = ''
                for i in doc.find_all(['p', 'h']):
                    str_htm += str(i)

                cmp_txt = regex.sub('', str_htm)

                similarity = SequenceMatcher(
                    None, str(inp_txt), str(cmp_txt)).ratio()
        plag_score.update({site: similarity*100})
      
        save_path = 'C:/Finalday/Folder/'

        name_of_file = input("What is the name of the file: ")
        completeName = os.path.join(save_path, name_of_file+".txt")
        file1 = open(completeName, "w")
        toFile = inp_txt
        file1.write(str(toFile))

        #print(str(plag_score) + '\n')
    max_value = max(plag_score.values())
    max_key = get_key(max_value)
    # num_per = str(max_value) + str(max_key)
    # result = num_per
    print(plag_score)
    return render_template('check.html', result1 = max_key, result2 = max_value)


if __name__ == "__main__":
    app.run(debug=True)
    
    
    
