import os
import logging
import time
import itertools
import concurrent.futures
from pathlib import Path
from markitdown import MarkItDown
from tqdm import tqdm

# SILENCE PDF PERMISSION WARNINGS
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def _process_single_file(md_converter: MarkItDown, file_path: Path) -> str:
    """
    Isolated worker function for the thread executor.
    
    Args:
        md_converter (MarkItDown): The active conversion engine instance.
        file_path (Path): Path to the target document.
        
    Returns:
        str: The extracted markdown text content.
    """
    result = md_converter.convert(str(file_path))
    return result.text_content

def convert_library_to_markdown(input_dir: str, output_dir: str) -> None:
    """
    Scans a directory for documents and converts them to Markdown.
    Utilizes concurrent.futures to maintain a responsive, real-time UI 
    spinner while blocking MarkItDown conversions run in the background.

    Args:
        input_dir (str): The local directory containing source documents.
        output_dir (str): The local directory where Markdown files will be saved.
    """
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

    # Braille spinner for high-visibility terminal activity
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])

    with tqdm(total=len(files_to_process), desc="📊 Total Progress", unit="file", colour="green") as pbar:
        for file in files_to_process:
            relative_path: Path = file.relative_to(input_path)
            target_file: Path = output_base / relative_path.with_suffix('.md')
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            short_name = file.name[:30]

            try:
                # Dispatch the heavy conversion to a background worker thread
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_process_single_file, md_converter, file)
                    
                    # While the background thread works, animate the UI on the main thread
                    while not future.done():
                        pbar.set_description(f"🔄 Processing {next(spinner)} {short_name}")
                        time.sleep(0.1)  # Control the animation frame rate
                    
                    # Retrieve the result once the thread finishes
                    markdown_content = future.result()
                
                # Write the output
                with open(target_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                
                # Update UI state for success
                pbar.set_description(f"✅ Finished: {short_name}")
                pbar.update(1)
                tqdm.write(f"✅ Success: {file.name}")
                
            except Exception as e:
                tqdm.write(f"❌ Error in {file.name}: {e}")
                pbar.update(1)

if __name__ == "__main__":
    PDF_VAULT: str = "./books_pdf"
    MD_OUTPUT: str = "./reference/books_markdown"
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)