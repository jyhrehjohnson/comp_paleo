### Computational Paleobiology Course Repository
## Description:
This project consists of a collection of shell scripts from Weeks 1-4. The goal for Weeks 1-was to learn how to acquire, clean, and summarize data from the command line. The scripts were written over the first four weeks of this computational paleobiology course. They cover navigating file systems, text processing,  and manipulating real fossil data. The scripts are written to be read and reused by anyone.


## Course context
Course Name: Computational Paleobiology

Institution: The University of Texas at Austin

Semester: Fall 2026

## Repository structure

├── README.md              #current file

├── .gitignore             #excludes data files and OS files

└── part01_OS/

    ├── week01/            #File system navigation and basic shell commands
    
    ├── week02/            #Text processing with grep, cut, sort, uniq
    
    ├── week03/            #Data cleaning
    
    └── week04/            #Pipeline scripts

## Dependencies
- OS: macOS

- Shell: bash or zsh

- Tools: awk, sed, grep, sort, cut, curl

## Usage

Make Week04 scripts executable

    chmod +x [insert path to script]
    ./[script path]


Example 1: for loop that searches for and prints the specimen count by formation and provides the total number of specimens 

    INPUT

    chmod +x formation_counts.sh
    ./formation_counts.sh ~/comp_paleo/part01_OS/week03/otb_fossils.tsv

    OUTPUT
    Specimen counts by formation
    Dataset: otb_fossils.tsv
    ================================
    Koobi Fora            591
    Shungura              258
    Nachukui              182
    Nawata                2
    Kanapoi               188
    Usno                  22
    ================================
    TOTAL                 1242

Example 2: a for loop meant to count and return the .tsv fossils within the week03 folder

    INPUT 

    chmod +x batch_inspect.sh
    ./batch_inspect.sh ~/comp_paleo/part01_OS/week03/

    OUTPUT
    Filename                                 Rows   Columns
    --------                                 ----   -------
    eppe_fossils.tsv                        13716        31
    otb_fossils.tsv                          1242        30


## Data
The data for Weeks 1-4 are the Omo-Turkana Basin (OTB) and EPPE hominin fossil datasets from the Origins database. (https://paleocore.org/origins/)


## Author name and contact
Author: Jyhreh Johnson

Email: jyhrehj@utexas.edu
