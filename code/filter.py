import csv
import re

def filter_csv(input_file, output_file):
    # Regular expression to match "רחוב + only number"
    # This regex checks for the word "רחוב" followed by space(s) and then just digits
    pattern = re.compile(r'^רחוב\s+\d+$')

    with open(input_file, mode='r', encoding='utf-8') as infile, \
         open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        for row in reader:
            # Assuming each row is a single column with the address
            if row and not pattern.match(row[0]):
                writer.writerow(row)

# Usage
input_csv_file = 'street_names.csv'  # Name of the input CSV file
output_csv_file = 'streeet_no_number_name.csv'  # Name where the filtered results will be saved
filter_csv(input_csv_file, output_csv_file)
