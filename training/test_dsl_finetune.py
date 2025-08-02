#!/usr/bin/env python3
"""
Test fine-tuning with high-quality Puppet DSL dataset
This should produce much better Puppet code output
"""

from finetune_puppet_model import PuppetModelTrainer
import os

def main():
    print("=== Testing QLoRA Fine-tuning with High-Quality Puppet DSL Dataset ===")
    
    # Check if base model exists
    if not os.path.exists("./stable-code-3b-base"):
        print("Error: Base model not found. Please run download_model.py first.")
        return False
    
    # Check if DSL data exists
    if not os.path.exists("../data_processing/puppet_dsl_training.json"):
        print("Error: Puppet DSL training data not found. Please run create_puppet_dsl_dataset.py first.")
        return False
    
    trainer = PuppetModelTrainer()
    
    # Train on high-quality DSL dataset
    print("Training on high-quality Puppet DSL dataset (15 examples)...")
    trainer.train(
        dataset_file="../data_processing/puppet_dsl_training.json",
        output_dir="./puppet-model-dsl"
    )
    
    # Test the model with the same prompts as Sonnet 4
    print("\n=== Testing DSL Fine-tuned Model ===")
    test_prompts = [
        "# Create a Puppet file resource",
        "# Define a Puppet class for Apache web server", 
        "# Create a Puppet service resource"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        result = trainer.test_model("./puppet-model-dsl", prompt)
        print("-" * 60)
    
    print("High-quality DSL fine-tuning test completed!")
    return True

if __name__ == "__main__":
    main()
