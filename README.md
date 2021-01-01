# finfinder

Finfinder parses annual reports in PDF format and finds the page numbers corresponding to the Income Statement, Balance Sheet, and Cash Flow Statement. Page numbers are detected with a Naive Bayes classifier.

Finfinder is great where financial data are not readily available and organized in a database. For example, SEDAR.com offers all Canadian public securities documents in PDF format, but rarely in XBLR format. This is where Finfinder helps by parsing through PDFs to detect the location of important financial data. 

A testing set of 278 PDFs were analyzed, each containing an Income Statement, Balance Sheet, and Cash Flow Statement, for a total of 834 statements. Of those, 94% were correctly identified. 

Future versions of Finfinder will extract, transform, and load the financial data.



