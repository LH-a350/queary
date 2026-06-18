# 📁 Question Browser

> A graphical tool for browsing and running Python programming question solutions

## 📖 Introduction

This is a lightweight Python question manager that provides both **GUI** and **command-line** interfaces. It allows you to:

- 📂 Browse questions organized in categorized folders (e.g., CSPJ, EILC, OP, etc.)
- 📄 View Python solution code (question descriptions are written as comments within the code)
- ▶️ Run code directly and see the output
- 📋 Copy file paths to clipboard

> ⚠️ **Current Status**: This is a basic version, and the question bank is continuously being updated. Currently, only Python solutions are provided, and the interface language is **Chinese**.

## 🚀 Quick Start

### Prerequisites

- Python 3.6+
- Dependencies: `pyperclip`

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/LH-a350/queary.git
cd queary

# 2. Install dependencies
pip install pyperclip

# 3. Run the application
python frontend_launcher.py   # GUI version (recommended)
# or
python main.py                # Command-line version