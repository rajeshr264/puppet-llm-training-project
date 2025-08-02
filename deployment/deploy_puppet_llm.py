#!/usr/bin/env python3
"""
Deployment utilities for Puppet LLM model
Provides easy-to-use inference interface
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json
import os
from datetime import datetime

class PuppetLLMDeployment:
    def __init__(self, base_model_path="./stable-code-3b-base", adapter_path="./puppet-model-production"):
        """Initialize the deployed Puppet LLM"""
        print("Loading Puppet LLM for deployment...")
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True
        )
        
        # Load LoRA adapter if exists
        if os.path.exists(adapter_path):
            print(f"Loading LoRA adapter from: {adapter_path}")
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            self.model = self.model.merge_and_unload()  # Merge for inference speed
        else:
            print(f"Warning: Adapter not found at {adapter_path}, using base model only")
        
        self.model.eval()
        print("✅ Puppet LLM loaded successfully!")
    
    def generate_puppet_code(self, prompt, max_tokens=300, temperature=0.7):
        """Generate Puppet code from a prompt"""
        # Format prompt consistently
        if not prompt.startswith("#"):
            prompt = f"# {prompt}"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        if torch.cuda.is_available():
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.1
            )
        
        # Decode and clean
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (after the prompt)
        if prompt in response:
            generated = response[len(prompt):].strip()
        else:
            generated = response.strip()
        
        return generated
    
    def batch_generate(self, prompts, max_tokens=300):
        """Generate Puppet code for multiple prompts"""
        results = []
        for i, prompt in enumerate(prompts, 1):
            print(f"Generating {i}/{len(prompts)}: {prompt}")
            result = self.generate_puppet_code(prompt, max_tokens)
            results.append({
                'prompt': prompt,
                'generated_code': result,
                'timestamp': datetime.now().isoformat()
            })
        return results
    
    def save_generated_code(self, results, output_file):
        """Save generated code to file"""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Generated code saved to: {output_file}")

def main():
    """Interactive deployment demo"""
    print("=== Puppet LLM Deployment Demo ===")
    
    # Initialize deployment
    puppet_llm = PuppetLLMDeployment()
    
    # Demo prompts
    demo_prompts = [
        "Create a Puppet file resource for /etc/motd",
        "Define a Puppet class for Apache web server",
        "Create a Puppet service resource for nginx",
        "Install and configure MySQL database server",
        "Create a user account with sudo privileges",
        "Define a Puppet node for production web server",
        "Create a defined type for deploying web applications"
    ]
    
    print(f"\n{'='*60}")
    print("PUPPET LLM GENERATION DEMO")
    print(f"{'='*60}")
    
    # Generate examples
    results = puppet_llm.batch_generate(demo_prompts)
    
    # Display results
    for i, result in enumerate(results, 1):
        print(f"\n[Example {i}] {result['prompt']}")
        print("-" * 50)
        print(result['generated_code'])
        print("=" * 60)
    
    # Save results
    output_dir = "../deployment"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/demo_generated_puppet_code.json"
    puppet_llm.save_generated_code(results, output_file)
    
    # Interactive mode
    print(f"\n{'='*60}")
    print("INTERACTIVE MODE (type 'quit' to exit)")
    print(f"{'='*60}")
    
    while True:
        try:
            user_prompt = input("\nEnter Puppet task description: ").strip()
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_prompt:
                print("\nGenerating Puppet code...")
                generated = puppet_llm.generate_puppet_code(user_prompt)
                print("-" * 50)
                print(generated)
                print("-" * 50)
        
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
    print("\n✅ Puppet LLM deployment demo completed!")

if __name__ == "__main__":
    main()
