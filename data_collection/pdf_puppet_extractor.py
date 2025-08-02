# create file: pdf_puppet_extractor.py
import PyPDF2
import re
import json
from pathlib import Path

class PDFPuppetExtractor:
    def __init__(self, output_dir="pdf_puppet_examples"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def extract_from_pdf(self, pdf_path):
        """Extract Puppet code examples from PDF"""
        examples = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            current_section = ""
            code_buffer = []
            in_code_block = False
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                lines = text.split('\n')
                
                for line in lines:
                    # Detect section headers (adjust patterns based on your PDF)
                    if re.match(r'^(Chapter \d+|Section \d+|\d+\.\d+)', line):
                        current_section = line.strip()
                    
                    # Detect code blocks (common patterns in technical PDFs)
                    if re.match(r'^(class\s+\w+|define\s+\w+|node\s+|file\s*{|package\s*{|service\s*{|exec\s*{)', line.strip()):
                        in_code_block = True
                        code_buffer = [line]
                    elif in_code_block:
                        # Check if line is indented (part of code block) or contains code-like content
                        if line.startswith(' ') or line.startswith('\t') or '=>' in line or line.strip().endswith(',') or line.strip() == '}':
                            code_buffer.append(line)
                        else:
                            # End of code block
                            if code_buffer and len(code_buffer) > 2:  # Only save blocks with multiple lines
                                code = '\n'.join(code_buffer)
                                # Basic quality filter - ensure it contains Puppet syntax
                                if ('=>' in code or 'class ' in code or 'define ' in code) and len(code.strip()) > 50:
                                    examples.append({
                                        'code': code,
                                        'section': current_section,
                                        'page': page_num + 1,
                                        'description': f"From {current_section} on page {page_num + 1}",
                                        'source': f"PDF page {page_num + 1}"
                                    })
                            in_code_block = False
                            code_buffer = []
        
        # Save extracted examples
        output_file = self.output_dir / "pdf_examples.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(examples, f, indent=2)
        
        return examples

# First install PyPDF2:
# pip install PyPDF2

# Usage:
if __name__ == "__main__":
    extractor = PDFPuppetExtractor()
    # Replace with your PDF path
    examples = extractor.extract_from_pdf("puppet_8_book.pdf")
    print(f"Extracted {len(examples)} examples from PDF")