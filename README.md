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
Make a script executable once, then run it from the repository root:

chmod +x part01_OS/week03/[script_name].sh

./part01_OS/week03/[script_name].sh [arguments] 

#part01 is named as part1 in my files, but I know for you they are under part01


Example 1: [what it does]

./part01_OS/week0N/[script1].sh [args] 

#part01 is named as part1 in my files, but I know for you they are under part01


Example 2: [what it does]

./part01_OS/week0N/[script2].sh [args]


Scripts expect input data in `data/raw/` and write results to `data/processed/`. Both directories are ignored by Git (see Data below), so create them locally:


mkdir -p data/raw data/processed


## Data
Data files are not stored in this repository. To reproduce the analyses, download them yourself:



### Author name and contact
Author: Jyhreh Johnson

Email: jyhrehj@utexas.edu
