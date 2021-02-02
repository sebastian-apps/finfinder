"""
General Utilities for FinFinder
"""


from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from io import StringIO
from pdfrw import PdfReader
from datetime import date, datetime


def clean_utctime():
    """
    Give UTC time, cleaned. Great for filenames.
    """
    return str(datetime.utcnow()).replace(' ','-').replace(':','-').replace('.','-') # clean up datetime string


def clean_text(text):
    """
    FOR NAIVE-BAYES CLASSIFICATION
    Both the keyword generating algorithm (generate_keywords) and the Naive Bayes training algorithm (naive-bayes-train) should clean text to achieve same text.
    However, generate_keywords uses json from tabula and naive-bayes-train uses text from pdfminer.
    Therefore, warning - the text is treated differently. Be careful.
    """
    text = text.lower()
    text = ''.join([i for i in text if not i.isdigit()]) # remove all numbers/digits

    # Because it's from tabula json
    text = text.replace(u"\u2018", "'").replace(u"\u2019", "'").replace("\u2013","-").replace("\u2014","-")
    text = text.replace("..","")
    text = text.replace("  "," ").replace("- ","").replace(". ","").replace(". ","")
    text = text.replace("\n"," ").replace("\r"," ")

    # Remove the following punctuation
    text = text.replace(".","").replace(",","").replace("$","").replace("'","")
    text = text.replace("(","").replace(")","").replace("note","")

    # Remove all words with only 1 character
    words = text.split(" ")
    text = " ".join([word for word in words if len(word) > 1])

    # Remove all double spaces. This should be one of the last cleaning operations.
    while "  " in text:
        text = text.replace("  "," ")
    return text





def remove_file_extension(filename):
    name, ext = filename.split('.')
    return name


def clean_dir_name(dir, main_directory):
    return dir.replace('/','').replace('\\','').replace(main_directory,'')


def get_filename_without_path(filename):
    # The path sometimes contains both '/' and '\' directory delimiters.
    dirs = filename.replace("\\","/").split("/")
    return dirs[-1]





def convert_CSV_to_XLSX():
    print('Converting CSVs into XLSX...\n')
    for filename in glob.glob("*.csv"):
        print(filename)
        wb = Workbook()
        ws = wb.active
        with open(filename, 'r') as f:
            for row in csv.reader(f):
                ws.append(row)
        wb.save(remove_file_extension(filename)+ '.xlsx')
        os.remove(filename)

""" PDF UTILITIES """

def pdf_page_count(filepath):
    num_pages = len(PdfReader(filepath).pages)
    # old way below...
    # read_pdf = PyPDF2.PdfFileReader(filepath)
    # num_pages = read_pdf.getNumPages()
    return num_pages


def convert_pdf_to_txt(fp, pagenos):
    """
    can't read text in landscape layout
    pagenos={2}
    for windows...  python -m pip install pdfminer.six
    """
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr,  codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True

    for pagenumber, page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)):
        interpreter.process_page(page)

    text = retstr.getvalue()
    # fp.close()
    device.close()
    retstr.close()
    return str(text, 'utf-8')





