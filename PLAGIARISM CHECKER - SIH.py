import yake
from keybert import KeyBERT
from encodings import utf_8
from bs4 import BeautifulSoup as bs
import requests
import re
from difflib import SequenceMatcher
from flask import *
import PyPDF2
import pytesseract
from PIL import Image
from pytesseract import pytesseract
import operator
####

app = Flask(__name__)
@ app.route('/')
def upload():
    return render_template("text2.html")


@ app.route('/success', methods=["GET", "POST"])
def checl_plag():
    if request.method == 'POST':
        f = request.files['file']
        inp_txt = ''

        if('.pdf' in str(f)):
            pdfReader = PyPDF2.PdfFileReader(f)
            for i in range(pdfReader.numPages):
                inp_txt += str(pdfReader.getPage(i).extractText())

        if('.txt' in str(f)):
            inp_txt = f.read()

        if('.png' in str(f)):
            path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            image_path = r""
            img = Image.open(image_path)
            pytesseract.tesseract_cmd = path_to_tesseract
            text = pytesseract.image_to_string(img)
            inp_txt = text[:-1]
            
        if('.doc' in str(f)):
            # global doc
            para_all = doc.paragraphs
            len(para_all)
            for para in para_all:
                doc_list = para.text
                inp_txt = doc_list.read()

        language = "en"
        max_ngram_size = 3
        deduplication_threshold = 0.05
        numOfKeywords = 20
        kw_model = KeyBERT()

        custom_kw_extractor = yake.KeywordExtractor(
            lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
        keywords = custom_kw_extractor.extract_keywords(inp_txt)

        keywords += kw_model.extract_keywords(str(inp_txt))

        plag_score = {}

    for title in keywords:

        regex = re.compile(r'<[^>]+>')

        tup_url = ("https://en.wikipedia.org/wiki/", "https://www.britannica.com/topic/")
        
        for i in tup_url:
            get_url = tup_url(i) + title[0].capitalize().replace(' ', '_')
        # url1 = r"https://www.britannica.com/topic/cryptocurrency/" + title[0].capitalize().replace(' ', '_')
        result = requests.get(get_url)
        doc = bs(result.text, "html.parser")

        str_htm = ''
        for i in doc.find_all(['p', 'h']):
            str_htm += str(i)

        cmp_txt = regex.sub('', str_htm)
        # cmp_txt = remove_html(str_htm)
        similarity = SequenceMatcher(None, str(inp_txt), str(cmp_txt)).ratio()
        plag_score.update({similarity*100 : url })

        # return plag_score

        print(str(plag_score) + '\n')
        plag_value = max(plag_score.items(), key=operator.itemgetter(1))
        #ret_tup = (max(plag_score.items(), key = operator.itemgetter(1)))
        num_per = str(plag_value)
        result = num_per
        return render_template('text3.html',result=result)
if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    