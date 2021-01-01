"""

For error checking,
Input key_pages from finfinder.py and compare with pages-labeled.json

"""


import finfinder
import os, glob
from datetime import date, datetime
import lib.json_lib as jl
import lib.utils as u



key_pages, data = finfinder.main()
print("DATA", data)
errors_page = data.get("Page errors")
errors_file = data.get("File errors")
count_loners = data.get("Loners found")
filenum = data.get("Total files processed")



# ERROR CHECKING
print("\nComparing pages with labeled pages...\n")
label_pages = jl.read_jsonfile("pages-labeled.json") # labeled data

total_matches = 0
statement_matches = 0
total_statements = 0
category_accuracy = {}

for company in key_pages.keys():
    for doc in key_pages.get(company).keys():
        try:
            predicted = key_pages.get(company).get(doc)
            actual = label_pages.get(company).get(doc)
            if predicted == actual:  # If all statements in the document match
                total_matches += 1
            else:
                print(f"Mismatch: {company}\\{doc}")
                print(f"Predicted: {predicted} vs.\nActual   : {actual}\n")

            for category, predicted_val in predicted.items():
                total_statements += 1

                if category not in category_accuracy:
                    category_accuracy.update({category: {"accurate": 0, "total": 1}})
                else:
                    category_accuracy.get(category).update({"total": category_accuracy.get(category).get("total") + 1})

                if predicted_val == actual.get(category):
                    statement_matches += 1
                    category_accuracy.get(category).update({"accurate": category_accuracy.get(category).get("accurate") + 1})

        except Exception as e:
            print('Exception: ', e)

report = {
    #"Exceptions details": exceptions_details,
    # many of these variables (errors_page) come from finfinder
    "Page errors": errors_page,
    "File errors": errors_file,
    "Loners found": count_loners,
    "Total matches": total_matches,
    "Total files processed": filenum,
    "Accuracy": round(total_matches/filenum,4),
    "Statement matches": statement_matches,
    "Total statements": total_statements,
    "Statement accuracy": round(statement_matches/total_statements,4),
    "Balance Sheets accuracy": round(category_accuracy.get("Balance Sheets").get("accurate")/category_accuracy.get("Balance Sheets").get("total"),4),
    "Cash Flow accuracy": round(category_accuracy.get("Cash Flows").get("accurate")/category_accuracy.get("Cash Flows").get("total"),4),
    "Income accuracy": round(category_accuracy.get("Income").get("accurate")/category_accuracy.get("Income").get("total"),4),
}
jl.pretty_print(report)
key_pages.update({"report": report})
