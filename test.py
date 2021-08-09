
import finfinder
import lib.json_lib as jl




good = {
    "Loblaw Companies Limited": {
        "Audited annual financial statements - English-Feb 21 2019": {
            "Income": "5",
            "Balance Sheets": "8",
            "Cash Flows": "9"
        },
        "Audited annual financial statements - English-Feb 22 2018": {
            "Income": "4",
            "Balance Sheets": "7",
            "Cash Flows": "8"
        },
        "Audited annual financial statements - English-Feb 23 2017": {
            "Income": "4",
            "Balance Sheets": "7",
            "Cash Flows": "8"
        }
    },
    "TC Energy Corporation": {
        "Audited annual financial statements - English-Feb 14 2019": {
            "Income": "4",
            "Balance Sheets": "7",
            "Cash Flows": "6"
        },
        "Audited annual financial statements - English-Feb 15 2018": {
            "Income": "4",
            "Balance Sheets": "7",
            "Cash Flows": "6"
        },
        "Audited annual financial statements - English-Feb 16 2017": {
            "Income": "4",
            "Balance Sheets": "7",
            "Cash Flows": "6"
        }
    }
}




pages, _ = finfinder.get_statement_pages(jl.read_jsonfile("classifier-probs.json"), "companies")

# output results
print("RESULTS:")
jl.pretty_print(pages)

assert pages==good, f"Should be '{jl.pretty_string(good)}'"

print("All tests passed.")
