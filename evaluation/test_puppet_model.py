# create file: test_puppet_model.py
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig

class PuppetModelTester:
    def __init__(self, model_path="puppet-model-test"):
        self.model_path = model_path
        self.load_model()
    
    def load_model(self):
        """Load the fine-tuned model"""
        print("Loading fine-tuned model...")
        
        # Load config to get base model name
        config = PeftConfig.from_pretrained(self.model_path)
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            config.base_model_name_or_path,
            device_map="auto",
            torch_dtype=torch.float16,
            trust_remote_code=True
        )
        
        # Load LoRA weights
        self.model = PeftModel.from_pretrained(self.model, self.model_path)
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        
        print("Model loaded!")
    
    def generate_puppet_code(self, instruction):
        """Generate Puppet code from instruction"""
        # Format the prompt for Stable Code (comment-driven)
        prompt = f"# {instruction}\n"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=256,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the generated code (remove the prompt)
        if prompt in generated:
            response = generated.replace(prompt, "", 1).strip()
        else:
            response = generated
        
        return response
    
    def test_examples(self):
        """Test with various examples"""
        test_instructions = [
            "Write a Puppet class to install and configure Apache web server",
            "Create a Puppet manifest to manage a user account named 'webadmin'",
            "Write Puppet code to ensure nginx service is running",
            "Create a file resource that manages /etc/motd with custom content",
            "Write a Puppet class that installs MySQL and creates a database"
        ]
        
        for instruction in test_instructions:
            print(f"\n{'='*60}")
            print(f"Instruction: {instruction}")
            print(f"{'='*60}")
            
            code = self.generate_puppet_code(instruction)
            print("Generated Code:")
            print(code)
            
            input("\nPress Enter to continue to next example...")

# Usage:
if __name__ == "__main__":
    tester = PuppetModelTester()
    tester.test_examples()