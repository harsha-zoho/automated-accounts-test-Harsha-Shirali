  # automated-accounts-test-Harsha-Shirali
  Fastapi PDF extractor

  Building a system for processing scanned receipts automatically.
  This app extracts relevant details from PDF receipts using OCR/AI techniques and store the extracted data in a structured format.

  i/p: collection of scanned receipts in PDF format

  Processing stepos: categorized into directories based on the year of purchase. 

  o/p: automate the extraction of information from these scanned receipts and store it efficiently in a SQLite database.

  REST APIs that can:

  Upload scanned receipts in PDF format. The files can be stored in a local directory.

  Validate the uploaded files to ensure they are valid PDFs.

  Extract key details from the receipts using OCR/AI-based text extraction techniques.

  Store extracted information in a structured database schema.

  Provide APIs for managing and retrieving receipts and their extracted data.

  Fastapi OCR/AI library is used to implement the current solution.

  The xtracted information is stored in an SQLite database (receipts.db).

  1. Receipt File Table (receipt_file)
  Stores metadata of uploaded receipt files.


>> id

>> file_name	

>> file_path	

>> is_valid	

>> invalid_reason	

>> is_processed	

>> created_at	

>> updated_at	

  2. Receipt Table (receipt)
  Stores extracted information from valid receipt files.

  stores additional information extracted from the receipts like transaction details, purchased items details, payment details and other information.

>> id	

>> purchased_at	

>> merchant_name	

>> total_amount	

>> file_path	

>> created_at	

>> updated_at	

APi's
>> 1. /upload (POST)

>> 2. /validate (POST)

>> 3. /process (POST)

>> 4. /receipts (GET)

>> 5. /receipts/{id} (GET)
