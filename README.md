# FinFinder

FinFinder finds financial statements. The algorithm parses annual reports in PDF format and finds the page numbers corresponding to the Income Statement, Balance Sheet, and Cash Flow Statement. Statements are detected with a Naive Bayes classifier.

FinFinder is great where financial data are not readily available and organized in a database. For example, SEDAR.com provides all Canadian public securities documents in PDF format, but rarely in XBRL format. This is where FinFinder helps by locating important financial data. 

A test set of 278 annual report PDFs were analyzed, each containing an Income Statement, Balance Sheet, and Cash Flow Statement, for a total of 834 statements. Of those statements, 94% were correctly identified. 

Future versions of FinFinder will extract, transform, and load the financial data.


<br />

## Installation

Clone the repository.

```
git clone https://github.com/sebastian-apps/finfinder.git
```

Create the virtual environment.

```
cd finfinder
```
```
python -m venv finfinder_env
```

Activate the virtual environment <i>for OSX</i>.

```
source finfinder_env/bin/activate
```

Activate the virtual environment <i>for Windows</i>.

```
finfinder_env\Scripts\activate
```

Install dependencies. The installation works best with Python 3.7.7.

```
pip install -r requirements.txt
```


<br />

## How to Use

Run finfinder.py<br>
```
python finfinder.py
```
Results will be saved in a finfinder-report JSON file.

Some example PDFs are included. 
Also, test out your own PDFs. Go to www.sedar.com and download annual reports.
Under /finfinder/companies/, create a folder with the company name. Add the PDFs to that folder.
Run finfinder.py









