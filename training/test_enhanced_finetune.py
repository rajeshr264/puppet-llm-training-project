#!/usr/bin/env python3
"""
Test fine-tuning with enhanced Puppet DSL dataset
"""

from finetune_puppet_model import PuppetModelTrainer
import os

def main():
    print("=== Testing QLoRA Fine-tuning with Enhanced Dataset ===")
    
    # Check if base model exists
    if not os.path.exists("./stable-code-3b-base"):
        print("Error: Base model not found. Please run download_model.py first.")
        return False
    
    # Check if enhanced data exists
    if not os.path.exists("../data_processing/puppet_enhanced_training.json"):
        print("Error: Enhanced training data not found. Please run create_enhanced_dataset.py first.")
        return False
    
    trainer = PuppetModelTrainer()
    
    # Train on enhanced dataset
    print("Training on enhanced Puppet DSL dataset (15 examples)...")
    trainer.train(
        dataset_file="../data_processing/puppet_enhanced_training.json",
        output_dir="./puppet-model-enhanced"
    )
    
    # Test the model with specific Puppet prompts
    print("\n=== Testing Enhanced Fine-tuned Model ===")
    test_prompts = [
        "# Install nginx package",
        "# Create a file resource",  
        "# Define a class for web server",
        "# Manage apache2 service",
        "# Create a user account"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        result = trainer.test_model("./puppet-model-enhanced", prompt)
        print("-" * 50)
    
    print("Enhanced fine-tuning test completed!")
    return True

if __name__ == "__main__":
    main()
