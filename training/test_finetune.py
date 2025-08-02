#!/usr/bin/env python3
"""
Quick test script for fine-tuning on small dataset
Run this first to verify everything works before full training
"""

from finetune_puppet_model import PuppetModelTrainer
import os

def main():
    print("=== Testing QLoRA Fine-tuning on Small Dataset ===")
    
    # Check if base model exists
    if not os.path.exists("./stable-code-3b-base"):
        print("Error: Base model not found. Please run download_model.py first.")
        return False
    
    # Check if test data exists
    if not os.path.exists("../data_processing/puppet_test_data.json"):
        print("Error: Test data not found. Please run create_training_dataset.py first.")
        return False
    
    trainer = PuppetModelTrainer()
    
    # Train on smaller test dataset (6 examples) for quick validation
    print("Training on test dataset (6 examples)...")
    trainer.train(
        dataset_file="../data_processing/puppet_test_data.json",
        output_dir="./puppet-model-test"
    )
    
    # Test the model
    print("\n=== Testing Fine-tuned Model ===")
    test_prompts = [
        "# Create a Puppet file resource",
        "# Define a Puppet class for Apache web server",
        "# Create a Puppet service resource"
    ]
    
    for prompt in test_prompts:
        trainer.test_model("./puppet-model-test", prompt)
        print("-" * 50)
    
    print("Test fine-tuning completed successfully!")
    return True

if __name__ == "__main__":
    main()
