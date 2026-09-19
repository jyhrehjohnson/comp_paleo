### Computational Paleobiology Course Repository
## Description:
This project consists of a collection of shell scripts from Weeks 1-4. The goal for Weeks 1-was to learn how to acquire, clean, and summarize data from the command line. The scripts were written over the first four weeks of this computational paleobiology course. They cover navigating file systems, text processing,  and manipulating real fossil data. The scripts are written to be read and reused by anyone.


## Course context
Course Name: Computational Paleobiology

Institution: The University of Texas at Austin

Semester: Fall 2026

## Repository structure

├── README.md              # current file

├── .gitignore             # excludes data files and OS files

└── part01_OS/

    ├── week01/            # [File system navigation and basic shell commands]

    ├── week02/            # [Text processing with grep, cut, sort, uniq]

    ├── week03/            # [Data cleaning]

    └── week04/            # [Pipeline scripts]

## Dependencies — what software is needed to run these scripts (bash version, OS, any tools like awk/sed)
- OS: macOS

- Shell: bash or zsh

- Tools: awk, sed, grep, sort, cut, curl

## Usage — how to run the scripts, with at least two concrete examples
Make a script executable once, then run it from the repository root:

```bash

chmod +x part01_OS/week03/[script_name].sh

./part01_OS/week03/[script_name].sh [arguments]

```

**Example 1: [what it does]**

```bash

./part01_OS/week0N/[script1].sh [args]

```

**Example 2: [what it does]**

```bash

./part01_OS/week0N/[script2].sh [args]

```

Scripts expect input data in `data/raw/` and write results to `data/processed/`. Both directories are ignored by Git (see Data below), so create them locally:

```bash

mkdir -p data/raw data/processed

```

## Data — where to obtain the datasets the scripts expect (PBDB API URL, Origins database URL)
Data files are not stored in this repository. To reproduce the analyses, download them yourself:



### Author name and contact
Author: Jyhreh Johnson
Email: jyhrehj@utexas.edu
