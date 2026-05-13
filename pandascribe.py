import os
import logging
from pathlib import Path
from markitdown import MarkItDown
from tqdm import tqdm

# SILENCE PDF PERMISSION WARNINGS
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def convert_library_to_markdown(input_dir: str, output_dir: str) -> None:
    """
    Scans a directory for PDFs and converts them to high-fidelity Markdown.
    Includes a progress bar for visual feedback during batch processing.

    Args:
        input_dir (str): The local directory containing PDFs/Docs to convert.
        output_dir (str): The local directory where Markdown files will be saved.
    """
    md_converter = MarkItDown()
    input_path = Path(input_dir)
    output_base = Path(output_dir)

    # Supported extensions for conversion
    extensions: set[str] = {'.pdf', '.docx', '.pptx'}

    # 1. Collect all matching files first to establish total count for progress bar
    files_to_process: list[Path] = [
        f for f in input_path.rglob('*') if f.suffix.lower() in extensions
    ]

    if not files_to_process:
        print(f"⚠️ No matching documents found in: {input_path}")
        return

    print(f"🚀 PandaScribe starting conversion: {input_path} ({len(files_to_process)} files)")

    # 2. Iterate through files with a tqdm progress bar
    for file in tqdm(files_to_process, desc="🔄 Converting Docs", unit="file"):
        relative_path: Path = file.relative_to(input_path)
        target_file: Path = output_base / relative_path.with_suffix('.md')
        
        # Ensure the sub-directory exists in the output folder
        target_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            # Perform the conversion
            result = md_converter.convert(str(file))
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(result.text_content)
            
            # Use tqdm.write to prevent print statements from breaking the progress bar
            tqdm.write(f"✅ Processed: {file.name}")
        except Exception as e:
            tqdm.write(f"❌ Critical error converting {file.name}: {e}")

if __name__ == "__main__":
    # Update these to your local paths as needed
    PDF_VAULT: str = "./books_pdf"
    MD_OUTPUT: str = "./reference/books_markdown"
    
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)