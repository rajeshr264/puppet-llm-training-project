#!/usr/bin/env python3
"""
Full-scale Puppet LLM training with combined high-quality datasets
This creates the production-ready model
"""

from finetune_puppet_model import PuppetModelTrainer
import json
import os

def combine_datasets():
    """Combine all datasets with priority to high-quality DSL examples"""
    print("Combining datasets...")
    
    combined_data = []
    
    # Load high-quality DSL dataset (highest priority - duplicate for emphasis)
    if os.path.exists("../data_processing/puppet_dsl_training.json"):
        with open("../data_processing/puppet_dsl_training.json", 'r') as f:
            dsl_data = json.load(f)
            # Add DSL examples twice for stronger training signal
            combined_data.extend(dsl_data)
            combined_data.extend(dsl_data)
            print(f"Added {len(dsl_data)} DSL examples (duplicated for emphasis)")
    
    # Load original scraped data (lower priority)
    if os.path.exists("../data_processing/puppet_training_data.json"):
        with open("../data_processing/puppet_training_data.json", 'r') as f:
            original_data = json.load(f)
            combined_data.extend(original_data)
            print(f"Added {len(original_data)} original scraped examples")
    
    # Save combined dataset
    output_file = "../data_processing/puppet_combined_training.json"
    with open(output_file, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    print(f"Combined dataset saved: {len(combined_data)} total examples")
    return output_file

def main():
    print("=== Full-Scale Puppet LLM Training ===")
    
    # Check if base model exists
    if not os.path.exists("./stable-code-3b-base"):
        print("Error: Base model not found. Please run download_model.py first.")
        return False
    
    # Combine datasets
    dataset_file = combine_datasets()
    
    trainer = PuppetModelTrainer()
    
    # Train on combined dataset
    print("\nTraining on combined high-quality dataset...")
    trainer.train(
        dataset_file=dataset_file,
        output_dir="./puppet-model-production"
    )
    
    # Comprehensive testing
    print("\n=== Testing Production Model ===")
    test_prompts = [
        "# Create a Puppet file resource",
        "# Define a Puppet class for Apache web server",
        "# Create a Puppet service resource",
        "# Install and configure MySQL database",
        "# Create a user account with SSH key",
        "# Define a Puppet node for web server",
        "# Create a custom defined type for application deployment"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n[Test {i}/{len(test_prompts)}] Prompt: {prompt}")
        result = trainer.test_model("./puppet-model-production", prompt)
        print("-" * 70)
    
    print("\n✅ Production Puppet LLM training completed successfully!")
    print("Model saved to: ./puppet-model-production")
    return True

if __name__ == "__main__":
    main()
