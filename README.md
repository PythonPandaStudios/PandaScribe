# 🐼 PandaScribe

**PandaScribe** is a high-fidelity document-to-markdown conversion engine designed to streamline document ingestion for modern AI workflows. It is optimized for preparing technical data for use with **Gemini Notebooks**, **ChatGPT Projects**, **Claude Projects**, and other large-context LLM interfaces.

Developed by **Python Panda Studios**, this tool transforms technical PDFs, documentation, and office files into clean, structured Markdown, allowing developers to leverage their local libraries as immediate, high-accuracy context.

---

## 🛠️ Prerequisites & Installation

To use PandaScribe, you need **FFmpeg** installed on your system (required by the underlying `pydub` library for multimedia processing) and the **MarkItDown** Python package.

### 1. Install FFmpeg
# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg -y

# macOS (Homebrew)
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

### 2. Setup Environment & Dependencies
# Clone the repository
git clone https://github.com/PythonPandaStudios/PandaScribe.git
cd PandaScribe

# Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install markitdown
```

---

## 📂 Usage

1. Place your PDFs in an input directory (e.g., `./books_pdf`).
2. Update the `PDF_VAULT` and `MD_OUTPUT` paths in `pandascribe.py`.
3. Run the conversion engine:

```bash
python pandascribe.py
```

---

## ⚙️ Features
- **Modern AI Integration:** Specifically formatted for use with Gemini, ChatGPT, and Claude project environments.
- **Recursive Processing:** Scans subfolders automatically to preserve your existing library structure.
- **Clean Ingestion:** Strips legacy PDF formatting to maximize token efficiency in large context windows.
- **Error Silencing:** Automatically suppresses non-critical PDF metadata and FFmpeg runtime warnings for a cleaner console experience.

---

## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.
