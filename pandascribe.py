import os
import re
import logging
from pathlib import Path
import fitz  # PyMuPDF
import pymupdf4llm
from tqdm import tqdm

# Silence general PyMuPDF warnings
fitz.TOOLS.mupdf_display_errors(False)

def post_process_markdown(md_text: str) -> str:
    """
    A robust cleaner pipeline that un-flattens Python REPL outputs 
    and wraps them in proper Markdown code blocks.
    """
    # 1. Unflatten squashed code blocks by forcing line breaks
    md_text = md_text.replace(">>> ", "\n>>> ")
    md_text = md_text.replace("Traceback (most recent call last):", "\nTraceback (most recent call last):")
    md_text = re.sub(r'(File "<[^>]+>", line \d+, in <module>)', r'\n  \1\n    ', md_text)
    
    error_patterns = r'(TypeError:|ValueError:|SyntaxError:|NameError:|AttributeError:|IndentationError:|KeyError:|ModuleNotFoundError:|ImportError:)'
    md_text = re.sub(error_patterns, r'\n\1', md_text)
    
    # 2. Line-by-Line State Machine to wrap the blocks
    lines = md_text.split('\n')
    processed_lines = []
    in_repl = False
    
    for line in lines:
        stripped = line.strip()
        
        # Start the code block
        if stripped.startswith(">>> "):
            if not in_repl:
                processed_lines.append("```python")
                in_repl = True
            processed_lines.append(line)
            
        # Continue the code block if it looks like an error trace
        elif in_repl and (
            stripped.startswith("Traceback") or 
            stripped.startswith("File") or 
            any(err in stripped for err in ["TypeError:", "ValueError:", "SyntaxError:", "NameError:", "AttributeError:", "IndentationError:", "KeyError:"]) or
            stripped.startswith("...")
        ):
            processed_lines.append(line)
            # If we just appended the actual error output, close the block
            if any(err in stripped for err in ["TypeError:", "ValueError:", "SyntaxError:", "NameError:", "AttributeError:", "IndentationError:", "KeyError:"]):
                processed_lines.append("```")
                in_repl = False
                
        # Handle normal text
        else:
            # If we were in a code block but hit normal text or an empty line, close it
            if in_repl and stripped != "":
                processed_lines.append("```")
                in_repl = False
            processed_lines.append(line)
            
    # Safety catch if the document ends while inside a code block
    if in_repl:
        processed_lines.append("```")
        
    # Clean up excessive newlines caused by unflattening
    md_text = "\n".join(processed_lines)
    md_text = re.sub(r'\n{3,}', '\n\n', md_text)
    return md_text

def convert_library_to_markdown(input_dir: str, output_dir: str) -> None:
    input_path = Path(input_dir)
    output_base = Path(output_dir)

    files_to_process: list[Path] = list(input_path.rglob('*.pdf'))

    if not files_to_process:
        print(f"⚠️ No PDF documents found in: {input_path}")
        return

    print(f"🚀 PandaScribe v2.2 starting batch conversion...")

    for file in files_to_process:
        relative_path: Path = file.relative_to(input_path)
        target_file: Path = output_base / relative_path.with_suffix('.md')
        target_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create a dedicated assets folder for THIS specific book
        assets_dir_name = f"{target_file.stem}_assets"
        file_assets_dir = target_file.parent / assets_dir_name
        file_assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Absolute path required for PyMuPDF to physically write the files
        abs_assets_dir = str(file_assets_dir.resolve())
        
        short_name = file.name[:30]

        try:
            doc = fitz.open(str(file))
            total_pages = len(doc)
            doc.close()
            
            markdown_content = ""

            with tqdm(total=total_pages, desc=f"🔄 Processing: {short_name}", unit="page", colour="cyan", leave=False) as pbar:
                for page_num in range(total_pages):
                    
                    # EXTRACT TEXT AND IMAGES
                    page_md = pymupdf4llm.to_markdown(
                        str(file), 
                        pages=[page_num],
                        write_images=True,
                        image_path=abs_assets_dir,
                        image_format="png"
                    )
                    
                    # Force relative pathing for the Markdown links so they work in Obsidian/VSC
                    page_md = page_md.replace(abs_assets_dir, assets_dir_name)
                    # Catch Windows backslash variants
                    page_md = page_md.replace(abs_assets_dir.replace("\\", "/"), assets_dir_name)
                    
                    markdown_content += page_md + "\n\n"
                    pbar.update(1)

            # Route through our State Machine Cleaner
            cleaned_markdown = post_process_markdown(markdown_content)

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(cleaned_markdown)
            
            tqdm.write(f"✅ Success: {file.name} ({total_pages} pages + images)")
            
        except Exception as e:
            tqdm.write(f"❌ Error in {file.name}: {e}")

if __name__ == "__main__":
    PDF_VAULT: str = "./books_pdf"
    MD_OUTPUT: str = "./reference/books_markdown"
    
    convert_library_to_markdown(PDF_VAULT, MD_OUTPUT)