import os
import logging
from pathlib import Path
import fitz  # PyMuPDF
import pymupdf4llm
from tqdm import tqdm

# Silence general PyMuPDF warnings for clean console
fitz.TOOLS.mupdf_display_errors(False)

def convert_library_to_markdown(input_dir: str, output_dir: str) -> None:
    """
    Scans a directory for PDFs and converts them to high-fidelity Markdown
    using PyMuPDF4LLM. Features a true page-by-page progress bar.

    Args:
        input_dir (str): The local directory containing source PDFs.
        output_dir (str): The local directory where Markdown files will be saved.
    """
    input_path = Path(input_dir)
    output_base = Path(output_dir)
    
    # PyMuPDF4LLM is strictly optimized for PDFs
    files_to_process: list[Path] = list(input_path.rglob('*.pdf'))

    if not files_to_process:
        print(f"⚠️ No PDF documents found in: {input_path}")
        return

    print(f"🚀 PandaScribe starting batch conversion...")

    for file in files_to_process:
        relative_path: Path = file.relative_to(input_path)
        target_file: Path = output_base / relative_path.with_suffix('.md')
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        short_name = file.name[:30]

        try:
            # 1. Open the document rapidly just to count the pages
            doc = fitz.open(str(file))
            total_pages = len(doc)
            doc.close()
            
            markdown_content = ""

            # 2. Initialize a true page-level progress bar for this specific file
            with tqdm(total=total_pages, desc=f"🔄 Processing: {short_name}", unit="page", colour="cyan", leave=False) as pbar:
                
                # 3. Iterate and convert page by page
                for page_num in range(total_pages):
                    # Extract Markdown for just this specific page
                    page_md = pymupdf4llm.to_markdown(str(file), pages=[page_num])
                    markdown_content += page_md + "\n\n"
                    
                    # Update the bar in real-time
                    pbar.update(1)

            # 4. Save the compiled Markdown
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(markdown_content)
            
            tqdm.write(f"✅ Success: {file.name} ({total_pages} pages)")
            
        except Exception as e:
            tqdm.write(f"❌ Error in {file.name}: {e}")

if __name__ == "__main__":
    # Update these to your local paths as needed
    PDF_VAULT: str = "./books_pdf"
    MD_OUTPUT: str = "./reference/books_markdown"
    
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)