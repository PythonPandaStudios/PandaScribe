import os
import logging
from pathlib import Path
from markitdown import MarkItDown

# SILENCE PDF PERMISSION WARNINGS
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def convert_library_to_markdown(input_dir: str, output_dir: str):
    """
    Scans a directory for PDFs and converts them to high-fidelity Markdown.
    Silences non-critical metadata permission warnings.
    """
    md_converter = MarkItDown()
    input_path = Path(input_dir)
    output_base = Path(output_dir)

    # Supported extensions
    extensions = {'.pdf', '.docx', '.pptx'}

    print(f"🚀 PandaScribe starting conversion: {input_path}")

    for file in input_path.rglob('*'):
        if file.suffix.lower() in extensions:
            relative_path = file.relative_to(input_path)
            target_file = output_base / relative_path.with_suffix('.md')
            
            target_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                print(f"📄 Processing: {file.name}...")
                result = md_converter.convert(str(file))
                
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                
                print(f"✅ Saved to: {target_file}")
            except Exception as e:
                print(f"❌ Critical error converting {file.name}: {e}")

if __name__ == "__main__":
    # Update these to your local paths
    PDF_VAULT = "./books_pdf"
    MD_OUTPUT = "./reference/books_markdown"
    
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)