# Folder Size Scanner

![Python](https://img.shields.io/badge/python-3.x-blue.svg)

A simple command-line utility to scan all immediate subfolders of a given directory and list those whose total size exceeds 50 MB, sorted in descending order.

---

## Table of Contents

* [Features](#features)  
* [Prerequisites](#prerequisites)  
* [Installation](#installation)  
* [Usage](#usage)  

---

## Features

- Recursively computes the size of each subfolder (excluding symbolic links).  
- Uses a thread pool (via `concurrent.futures.ThreadPoolExecutor`) for parallel scanning.  
- Skips over files or directories that raise errors (permissions, race conditions, etc.).  
- Prints progress in real time.  
- Filters and displays only those folders whose size ≥ 50 MB.  
- Cross-platform support: ensures UTF-8 console encoding on Windows.  

---

## Prerequisites

- Python **3.6** or higher  
- Standard library only (no external dependencies)  

---

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/KiriVoll/CheckFolderSize.git
   cd folder-size-scanner

## Usage

1. Run the script:
   ```bash
   python CheckFolderSize.py

At the prompt, enter the absolute or relative path to the directory you want to scan.

Type exit and press Enter to quit.
