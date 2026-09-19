#!/usr/bin/env python3
"""
fix_newlines.py
Reads a CSV file, removes embedded newlines from all fields,
and writes the result as a tab-separated (TSV) file.

Usage: python3 fix_newlines.py input.csv output.tsv
"""

import csv  #Imports the csv module, which handles comma-separated fields
import sys  #Imports the sys module, this is needed for command-line arguments

def fix_newlines(input_path, output_path): #Defines a function that takes an input file path and an output file path
    rows_fixed = 0  #Creates/starts a counter to track how many rows are contained an embedded newline

    with open(input_path, newline='', encoding='utf-8') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        #Opens the input file for reading and the output file for writing;
        #newline='' is required so the csv module can handle line endings

        reader = csv.reader(infile) #Creates a CSV reader that will read the infile row by row into lists of fields
        writer = csv.writer(outfile, delimiter='\t') #Creates a CSV writer for outfile that separates fields with tabs

        for i, row in enumerate(reader): #Creates a loop over each row from the reader, enumerate also gives the row's index number as i
            cleaned = [] #Starts an empty list to hold this row's cleaned field values
            row_had_newline = False #Notes whether any field in this row needs fixing

            for field in row: #Creates a loop over each individual field in the current row
                if '\n' in field or '\r' in field: #Checks whether this field contains a newline or carriage-return character
                    cleaned.append(field.replace('\n', ' ').replace('\r', '').strip())
                    #Replaces embedded newlines with a space, drop carriage returns, and strips leading/trailing whitespace, then saves the cleaned field
                    row_had_newline = True  #Marks that this row required cleaning
                else:
                    cleaned.append(field) #Records what field was already clean, so keeps it unchanged

            if row_had_newline: #After checking all fields, this sees if this row needs any fixing
                rows_fixed += 1 #If it needs fixing, it adds the running total of fixed rows
                print(f"  Row {i}: embedded newline removed", file=sys.stderr)
                #Print to stderr so it doesn't mix in with normal program output, it shows which row index was fixed

            writer.writerow(cleaned) #Writes the row out to the TSV output file

    print(f"Done. {rows_fixed} row(s) fixed.")  #Prints the total number of rows that were fixed
    print(f"Output written to: {output_path}")  #Prints where the cleaned output file was saved

if __name__ == '__main__':  #Only run the following block if this file is executed directly
    if len(sys.argv) != 3:  #sys.argv includes the script name plus its arguments
        print("Usage: python3 fix_newlines.py input.csv output.tsv") #Prints to the user the correct way to call the script
        sys.exit(1) #Exits the program with a non-zero status code to signal an error occurred

    fix_newlines(sys.argv[1], sys.argv[2]) #Calls the function, passing in the input path (argv[1]) and output path (argv[2])
