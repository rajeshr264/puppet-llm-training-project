# create file: create_training_dataset.py
import json
import re
from pathlib import Path
import random

class PuppetDatasetCreator:
    def __init__(self):
        self.training_examples = []
        
    def clean_puppet_code(self, code):
        """Clean and standardize Puppet code"""
        # Remove extra whitespace
        code = re.sub(r'\n\s*\n', '\n\n', code)
        
        # Ensure consistent indentation (2 spaces)
        lines = code.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Count leading spaces
            stripped = line.lstrip()
            if stripped:
                indent_level = (len(line) - len(stripped)) // 2
                cleaned_lines.append('  ' * indent_level + stripped)
            else:
                cleaned_lines.append('')
        
        return '\n'.join(cleaned_lines)
    
    def create_instruction_format(self, description, code):
        """Create format for Stable Code - using code completion style"""
        # Stable Code works best with:
        # 1. Direct code completion
        # 2. Comment-driven generation
        # 3. Fill-in-the-middle (FIM) format
        
        # Option 1: Comment-driven (RECOMMENDED)
        formatted = f"""# {description}
{code}"""
        
        # Option 2: FIM format (for code completion scenarios)
        # formatted = f"<fim_prefix>{code[:len(code)//2]}<fim_suffix>{code[len(code)//2:]}<fim_middle>"
        
        return formatted
    
    def process_github_files(self, raw_data_dir):
        """Process files downloaded from GitHub"""
        raw_data_path = Path(raw_data_dir)
        
        for pp_file in raw_data_path.rglob("*.pp"):
            with open(pp_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract class/define name and create description
            class_match = re.search(r'class\s+(\w+)', content)
            define_match = re.search(r'define\s+(\w+)', content)
            
            if class_match:
                name = class_match.group(1)
                description = f"Write a Puppet class named {name}"
            elif define_match:
                name = define_match.group(1)
                description = f"Write a Puppet defined type named {name}"
            else:
                # Generic description
                description = "Write Puppet code for system configuration"
            
            # Look for comments at the beginning for better description
            comment_match = re.search(r'^#\s*(.+?)$', content, re.MULTILINE)
            if comment_match:
                description = comment_match.group(1)
            
            cleaned_code = self.clean_puppet_code(content)
            
            self.training_examples.append({
                'instruction': description,
                'output': cleaned_code,
                'source': str(pp_file)
            })
    
    
    
    def process_pdf_examples(self, json_file):
        """Process examples from PDF extractor"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                examples = json.load(f)
                
            for example in examples:
                # Basic filtering
                if len(example['code']) < 30:
                    continue
                    
                cleaned_code = self.clean_puppet_code(example['code'])
                
                self.training_examples.append({
                    'instruction': example['description'],
                    'output': cleaned_code,
                    'source': example['source']
                })
        except FileNotFoundError:
            print(f"PDF examples file not found: {json_file}")
        except Exception as e:
            print(f"Error processing PDF examples: {e}")

    def process_web_examples(self, json_file):
        """Process examples from web scraper with deduplication and filtering"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                examples = json.load(f)
        except FileNotFoundError:
            print(f"Web examples file not found: {json_file}")
            return
        except Exception as e:
            print(f"Error loading web examples: {e}")
            return

        seen_codes = set()
        
        for example in examples:
            # Quality filters
            if example.get('puppet_score', 0) < 3:
                continue
            if len(example['code']) < 30:
                continue
            if example['code'] in seen_codes:
                continue
                
            seen_codes.add(example['code'])
            
            # Generate better descriptions
            code = example['code']
            description = example['description']
            
            # Extract better context from code if description is generic
            if description in ['Classes', 'Puppet', ''] or len(description) < 10:
                if 'class ' in code:
                    match = re.search(r'class\s+(\w+)', code)
                    if match:
                        description = f"Puppet class {match.group(1)}"
                elif 'define ' in code:
                    match = re.search(r'define\s+(\w+)', code)
                    if match:
                        description = f"Puppet defined type {match.group(1)}"
                elif 'node ' in code:
                    description = "Puppet node definition"
                elif 'include ' in code:
                    description = "Including Puppet classes"
                else:
                    description = "Puppet configuration code"
            
            cleaned_code = self.clean_puppet_code(code)
            
            self.training_examples.append({
                'instruction': description,
                'output': cleaned_code,
                'source': example['source']
            })
    
    def create_final_dataset(self, output_file="puppet_training_data.json"):
        """Create final training dataset"""
        # Remove duplicates based on code similarity
        unique_examples = []
        seen_codes = set()
        
        for example in self.training_examples:
            # Simple deduplication based on normalized code
            normalized = re.sub(r'\s+', ' ', example['output'])
            if normalized not in seen_codes:
                seen_codes.add(normalized)
                unique_examples.append(example)
        
        # Shuffle for better training
        random.shuffle(unique_examples)
        
        # Format for training - Stable Code expects 'text' field
        formatted_examples = []
        for example in unique_examples:
            # For Stable Code, use comment-driven format
            text = f"# {example['instruction']}\n{example['output']}"
            formatted_examples.append({'text': text})
        
        # Save dataset
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_examples, f, indent=2)
        
        print(f"Created dataset with {len(formatted_examples)} examples")
        print(f"Saved to: {output_file}")
        
        # Also create a smaller test dataset
        test_size = min(50, len(formatted_examples) // 10)
        test_examples = formatted_examples[:test_size]
        
        with open("puppet_test_data.json", 'w', encoding='utf-8') as f:
            json.dump(test_examples, f, indent=2)
        
        print(f"Created test dataset with {len(test_examples)} examples")

# Usage:
if __name__ == "__main__":
    creator = PuppetDatasetCreator()
    
    # Process all data sources
    creator.process_github_files("../raw_data/raw_puppet_data")
    creator.process_web_examples("../data_collection/web_puppet_examples/puppet_docs_examples.json")
    creator.process_pdf_examples("../data_collection/pdf_puppet_examples/pdf_examples.json")
    
    # Create final dataset
    creator.create_final_dataset()