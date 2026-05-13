import os
from pathlib import Path
from markitdown import MarkItDown

def convert_library_to_markdown(input_dir: str, output_dir: str):
    """
    Scans a directory for PDFs and converts them to high-fidelity Markdown.
    """
    md_converter = MarkItDown()
    input_path = Path(input_dir)
    output_base = Path(output_dir)

    # Supported extensions
    extensions = {'.pdf', '.docx', '.pptx'}

    print(f"🚀 Starting conversion of library: {input_path}")

    for file in input_path.rglob('*'):
        if file.suffix.lower() in extensions:
            # Maintain folder hierarchy
            relative_path = file.relative_to(input_path)
            target_file = output_base / relative_path.with_suffix('.md')
            
            # Create directories
            target_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                print(f"📄 Converting: {file.name}...")
                result = md_converter.convert(str(file))
                
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                
                print(f"✅ Saved to: {target_file}")
            except Exception as e:
                print(f"❌ Failed to convert {file.name}: {e}")

if __name__ == "__main__":
    # Define your local paths here
    LOCAL_PDF_VAULT = "./books_pdf"
    MARKDOWN_REFERENCE = "./reference/books_markdown"
    
    convert_library_to_markdown(LOCAL_PDF_VAULT, MARKDOWN_REFERENCE)