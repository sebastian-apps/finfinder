"""

FinFinder parses annual reports in PDF format and finds the page numbers corresponding to the Income Statement, Balance Sheet, and Cash Flow Statement. 
Page numbers are detected with a Naive Bayes classifier.

FinFinder is great where financial data are not readily available and organized in a database. 
For example, SEDAR.com provides all Canadian public securities documents in PDF format, but rarely in XBLR format. 
This is where FinFinder helps by locating important financial data.

A testing set of 278 annual report PDFs were analyzed, each containing an Income Statement, Balance Sheet, and Cash Flow Statement, for a total of 834 statements. 
Of those statements, 94% were correctly identified.

Future versions of FinFinder will extract, transform, and load the financial data.


"""

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter  # pip install pdfminer2
from pdfminer.converter import HTMLConverter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
from io import StringIO
import os, glob
from datetime import date, datetime
import lib.json_lib as jl
import lib.utils as u



DIRECTORY = "companies"


def main():

    nbc_probs = jl.read_jsonfile("classifier-probs.json") # Naive Bayes classifier probabilities
    key_pages = {}  # All of the found pages. We are looking to fill this up.
    filenum = 0 # File number being processed
    errors_page = 0 # Number of errors involving page errors
    errors_file = 0 # Number of errors involving the file itself
    exceptions_details = [] # Details of exceptions
    count_loners = 0 # Number of "loner" values found

    for dir in glob.glob(f"{DIRECTORY}/*/"): # Loop through every company directory
        company = u.clean_dir_name(dir, DIRECTORY)
        print("\nDIRECTORY: ", dir)
        print("COMPANY: ", company, "\n")
        # create new dictionary for the company
        key_pages.update({company: {}})


        # loop through every financial PDF
        # file is path + filename + extension from local folder where this script is running
        for file in glob.glob(f"{DIRECTORY}/{company}/*.pdf"):

            if "._" not in file:  # ignore hidden files
                try:
                    print(f"Extracting: {company}: {file}")
                    doc_name = u.get_filename_without_path(u.remove_file_extension(file))
                    key_pages.get(company).update({doc_name: {}}) # create new doc dictionary for the company
                    maxpages = u.pdf_page_count(file)
                    print("No. pages in doc: ", maxpages)
                    fp = open(file, 'rb')  # rb instead of r

                    # Initialize probability lists
                    prob_list_income = []
                    prob_list_balancesheets = []
                    prob_list_cashflow = []

                    # for every page in the PDF doc, perform Bayesian analysis for the financial statements
                    for pagenum in range(0, maxpages):
                        print(f"\n{file}, 1-Based Page Number: {pagenum + 1}")
                        try:
                            # Extract text from PDF
                            text = u.convert_pdf_to_txt(fp, {pagenum})
                            text = u.clean_text(text)

                            print("posterior = likelihood * prior / evidence")
                            # do Income Statement
                            posterior_income = bayesian(text, nbc_probs, "Income", "is_class")
                            prob_list_income.append(posterior_income)
                            # do Balance Sheets
                            posterior_balancesheets = bayesian(text, nbc_probs, "Balance Sheets", "is_class")
                            prob_list_balancesheets.append(posterior_balancesheets)
                            # do Cashflow Statement
                            posterior_cashflow = bayesian(text, nbc_probs, "Cash Flows", "is_class")
                            prob_list_cashflow.append(posterior_cashflow)

                        except Exception as e:
                            errors_page += 1
                            exceptions_details.append(e)
                            print('Page Exception: ', e)


                    # Sort pages from best to worst based on their posterior, where a higher posterior is better.
                    pages_income = get_sorted_pages(prob_list_income)
                    pages_balancesheets = get_sorted_pages(prob_list_balancesheets)
                    pages_cashflow = get_sorted_pages(prob_list_cashflow)
                    # From the sorted list, get the best page, taking into account "loners".
                    page_income, page_balancesheets, page_cashflow, count_loners = get_best_page(pages_income, pages_balancesheets, pages_cashflow, count_loners)

                    # converting pages numbers to string to match labeled data
                    key_pages.get(company).get(doc_name).update({"Income": str(page_income)})      # forcing integer to string. maybe bad idea
                    print("Income page no.: ", page_income)

                    key_pages.get(company).get(doc_name).update({"Balance Sheets": str(page_balancesheets)}) # forcing integer to string. maybe bad idea
                    print("Balance Sheets page no.: ", page_balancesheets)

                    key_pages.get(company).get(doc_name).update({"Cash Flows": str(page_cashflow)}) # forcing integer to string. maybe bad idea
                    print("Cash Flows page no.: ", page_cashflow)


                # Done going through pages
                except Exception as e:
                    errors_file += 1
                    exceptions_details.append(e)
                    print('File Exception: ', e)

                print('\n')
                filenum += 1  # tally total files processed
                fp.close()



        # End for loop

    jl.pretty_print(key_pages)
    jl.write_jsonfile(key_pages, f"finfinder-report-{u.clean_utctime()}.json")


    data = {
        #"Exceptions details": exceptions_details,
        "Page errors": errors_page,
        "File errors": errors_file,
        "Loners found": count_loners,
        "Total files processed": filenum,
        }
    print(data)
    return key_pages, data




def bayesian(text, nbc_probs, category, nb_class):
    """
    INPUTS:
    text (str): the text in a page of PDF
    nbc_probs (dict): the dictionary containing all Naive Bayes classifier probabilities
    category (str): "Income" or "Balance Sheets" or "Cash Flows"
    nb_class (str): "in_class" or "not_in_class", whether or not it belongs to the category

    OUTPUT:
    the posterior of the Bayes equation


    EQUATION: POSTERIOR = (LIKELIHOOD * PRIOR) / EVIDENCE
    LIKELIHOOD: For all keywords that were found, multiply their probabilities (either from "in_class" or "not_in_class")
    PRIOR: The overall probability of "in_class" or "not_in_class" occurring.
    EVIDENCE: For all keywords found, multiply their overall probabilities of occurring *regardless* of "in_class" or "not_in_class".
    (Another name is the Predictor Prior Probability)

    Alternatives to the equation (but didn't seem to work well):
    Option 1) posterior = likelihood + prior   ....evidence eliminated
    Option 2) Using log of probabilities


    Can be improved by sending only the relevant portion of nbc_probs
    """

    # Search for all relevant keywords in text
    keyword_list = [keyword for keyword in nbc_probs.get(category).get(nb_class).keys() if keyword in text]
    # Calculate for ALL keywords, not just the ones found, as is above code.
    #keyword_list = [keyword for keyword in nbc_probs.get(category).get(nb_class).keys()]

    # Calculate Likelihood and Evidence
    likelihood = 1
    p_list = []
    evidence = 1
    for keyword in keyword_list:
        p = likelihood*nbc_probs.get(category).get(nb_class).get(keyword)
        if round(p,1) != 0.0:  # Zero will give a likelihood of zero and thus a posterior of zero. Not desired.
            p_list.append(p)
            likelihood = (likelihood*p)
        evidence = evidence*nbc_probs.get(category).get("evidence").get(keyword)

    if likelihood == 0.0:
        print("Likelihood value is zero. p_list:", p_list)
    if evidence == 0.0:
        print("Evidence value is zero. p_list:", p_list)

    # Get Prior
    prior = nbc_probs.get(category).get("prior")
    # Calculate Posterior
    posterior = likelihood * prior / evidence
    print(f"{category} posterior: {posterior} = {likelihood} * {prior} / {evidence}")
    return posterior




def get_sorted_pages(prob_list):
    """ Sort pages from best to worst based on their posterior, where a higher posterior is better. """
    # Sort all listed probabilities highest to lowest, with page number in tuple.
    templist = sorted([(prob, pagenum) for pagenum, prob in enumerate(prob_list)], reverse=True)
    # The pages are now in order, sorted by highest probability. We only need the sorted page numbers from here on.
    # Keep only page numbers in this sorted list.
    return [pagenum for _, pagenum in templist]




def get_best_page(pages_income, pages_balancesheets, pages_cashflow, count_loners):
    """
    The best page for a category (Income, Balance Sheets, Cash Flow) is often the page associated with
    the highest Bayesian posterior. In an annual report, all 3 pages are always closely located
    and occasionally we come up with a "loner" page far away from the others. Hence, in this case, the
    page with the highest posterior is not chosen, and the next one in the sorted list is inspected.
    """
    # We'll start with the first page numbers and work our way back if there are loner values.
    count_income = 0
    count_balancesheets = 0
    count_cashflow = 0
    loner = 999

    while loner is not None:
        count_loners += 1
        a = pages_income[count_income]
        b = pages_balancesheets[count_balancesheets]
        c = pages_cashflow[count_cashflow]
        contenders = [a, b, c]
        print("contenders:", contenders)
        loner = is_loner_present(contenders, 6)  # tried 10, got 0.48 accuracy
        if loner is not None:
            print("loner:", loner)
        if loner == 0:
            count_income += 1
        elif loner == 1:
            count_balancesheets += 1
        elif loner == 2:
            count_cashflow += 1

    page_income = a + 1
    page_balancesheets = b + 1
    page_cashflow = c + 1
    return page_income, page_balancesheets, page_cashflow, count_loners





def is_loner_present(num_list, threshold):
    """
    In a group of three numbers, is one a loner?
    More specifically, does one value have a distance greater than threshold w.r.t
    to all other values?
    Income, Balance Sheets, and Cash Flow statements are always just a few pages apart.
    """

    try:
        a = int(num_list[0])
        b = int(num_list[1])
        c = int(num_list[2])
    except:
        return None

    #print("Internal A B C:", a,b,c)
    d_ab = abs(a - b)
    d_ac = abs(a - c)
    d_bc = abs(b - c)
    #print("differences: ", d_ab, ",", d_ac, ",", d_bc)

    if d_ab >= threshold and d_ac >= threshold and d_bc < threshold:
        num_pos = 0  # a is the loner
    elif d_ab >= threshold and d_ac < threshold and d_bc >= threshold:
        num_pos = 1 # b is the loner
    elif d_ab < threshold and d_ac >= threshold and d_bc >= threshold:
        num_pos = 2 # c is the loner
    else:
        # Everyone is close enough, or all three are spread apart.
        return None
    return num_pos




if __name__ == "__main__":
    main()
