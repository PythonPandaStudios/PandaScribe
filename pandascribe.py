import os
import logging
import time
from pathlib import Path
from markitdown import MarkItDown
from tqdm import tqdm

# SILENCE PDF PERMISSION WARNINGS
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def convert_library_to_markdown(input_dir: str, output_dir: str) -> None:
    md_converter = MarkItDown()
    input_path = Path(input_dir)
    output_base = Path(output_dir)
    extensions: set[str] = {'.pdf', '.docx', '.pptx'}

    files_to_process: list[Path] = [
        f for f in input_path.rglob('*') if f.suffix.lower() in extensions
    ]

    if not files_to_process:
        print(f"⚠️ No matching documents found in: {input_path}")
        return

    print(f"🚀 PandaScribe starting batch conversion...")

    # Main progress bar for the overall task
    with tqdm(total=len(files_to_process), desc="📊 Total Progress", unit="file", colour="green") as pbar:
        for file in files_to_process:
            # Update description so the user knows WHICH file is being processed
            pbar.set_description(f"🔄 Converting: {file.name[:30]}...")
            
            relative_path: Path = file.relative_to(input_path)
            target_file: Path = output_base / relative_path.with_suffix('.md')
            target_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                # The "thinking" happens here
                result = md_converter.convert(str(file))
                
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(result.text_content)
                
                # Update total bar once file is complete
                pbar.update(1)
                tqdm.write(f"✅ Success: {file.name}")
                
            except Exception as e:
                tqdm.write(f"❌ Error in {file.name}: {e}")
                pbar.update(1) # Still move the bar forward even on failure

if __name__ == "__main__":
    PDF_VAULT: str = "./books_pdf"
    MD_OUTPUT: str = "./reference/books_markdown"
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)