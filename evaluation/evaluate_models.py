#!/usr/bin/env python3
"""
Comprehensive evaluation of Puppet LLM models
Compares different model versions and provides quality metrics
"""

from finetune_puppet_model import PuppetModelTrainer
import json
import re
import os
from datetime import datetime

class PuppetModelEvaluator:
    def __init__(self):
        self.trainer = PuppetModelTrainer()
        
    def puppet_syntax_score(self, text):
        """Score Puppet syntax quality (0-100)"""
        score = 0
        
        # Check for Puppet resource types
        puppet_resources = ['file', 'package', 'service', 'user', 'group', 'exec', 'cron']
        for resource in puppet_resources:
            if re.search(rf'{resource}\s*{{', text):
                score += 15
        
        # Check for proper Puppet syntax patterns
        patterns = [
            r'\w+\s*{\s*[\'"][^\'\"]+[\'"]:\s*',  # resource { 'name':
            r'ensure\s*=>\s*\w+',                 # ensure => value
            r'require\s*=>\s*\w+\[[\'"][^\'"]+[\'\"]\]',  # require => Resource['name']
            r'notify\s*=>\s*\w+\[[\'"][^\'"]+[\'\"]\]',   # notify => Resource['name']
            r'mode\s*=>\s*[\'"][0-9]{4}[\'"]',    # mode => '0644'
            r'owner\s*=>\s*[\'"][^\'\"]+[\'"]',   # owner => 'user'
            r'group\s*=>\s*[\'"][^\'\"]+[\'"]',   # group => 'group'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                score += 10
        
        # Penalty for Python-like syntax
        python_patterns = [
            r'def\s+\w+\(',     # def function(
            r'import\s+\w+',    # import module
            r'print\s*\(',      # print(
            r'if\s+\w+\s*==',   # if var ==
            r'for\s+\w+\s+in',  # for var in
        ]
        
        for pattern in python_patterns:
            if re.search(pattern, text):
                score -= 20
        
        return max(0, min(100, score))
    
    def evaluate_model(self, model_path, test_prompts):
        """Evaluate a model with comprehensive metrics"""
        print(f"\n{'='*60}")
        print(f"Evaluating Model: {model_path}")
        print(f"{'='*60}")
        
        results = []
        total_syntax_score = 0
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n[Test {i}/{len(test_prompts)}] {prompt}")
            
            # Generate response
            response = self.trainer.test_model(model_path, prompt, max_new_tokens=200)
            
            # Calculate syntax score
            syntax_score = self.puppet_syntax_score(response)
            total_syntax_score += syntax_score
            
            result = {
                'prompt': prompt,
                'response': response,
                'syntax_score': syntax_score,
                'length': len(response.split()),
                'has_puppet_resources': bool(re.search(r'\w+\s*{', response))
            }
            results.append(result)
            
            print(f"Syntax Score: {syntax_score}/100")
            print(f"Response Length: {result['length']} words")
            print(f"Has Puppet Resources: {result['has_puppet_resources']}")
            print("-" * 50)
        
        # Overall metrics
        avg_syntax_score = total_syntax_score / len(test_prompts)
        puppet_resource_rate = sum(1 for r in results if r['has_puppet_resources']) / len(results) * 100
        
        summary = {
            'model_path': model_path,
            'timestamp': datetime.now().isoformat(),
            'test_count': len(test_prompts),
            'average_syntax_score': round(avg_syntax_score, 2),
            'puppet_resource_rate': round(puppet_resource_rate, 2),
            'individual_results': results
        }
        
        print(f"\n{'='*60}")
        print(f"SUMMARY - {model_path}")
        print(f"{'='*60}")
        print(f"Average Syntax Score: {avg_syntax_score:.1f}/100")
        print(f"Puppet Resource Detection Rate: {puppet_resource_rate:.1f}%")
        print(f"Tests Passed: {len([r for r in results if r['syntax_score'] > 50])}/{len(test_prompts)}")
        
        return summary

def main():
    print("=== Puppet LLM Model Evaluation Suite ===")
    
    evaluator = PuppetModelEvaluator()
    
    # Test prompts covering various Puppet use cases
    test_prompts = [
        "# Create a Puppet file resource",
        "# Define a Puppet class for Apache web server",
        "# Create a Puppet service resource",
        "# Install nginx package with configuration",
        "# Create a user account with home directory",
        "# Define a Puppet node for database server",
        "# Create an exec resource for system update",
        "# Define a custom resource type for application",
    ]
    
    # Models to evaluate
    models_to_test = [
        "./puppet-model-test",        # Original small test model
        "./puppet-model-dsl",         # DSL-trained model
        "./puppet-model-production",  # Full production model (if exists)
    ]
    
    evaluation_results = []
    
    for model_path in models_to_test:
        if os.path.exists(model_path):
            result = evaluator.evaluate_model(model_path, test_prompts)
            evaluation_results.append(result)
        else:
            print(f"\nSkipping {model_path} - not found")
    
    # Save detailed results
    output_file = f"../evaluation/evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs("../evaluation", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(evaluation_results, f, indent=2)
    
    print(f"\n✅ Evaluation completed! Results saved to: {output_file}")
    
    # Print comparison
    if len(evaluation_results) > 1:
        print(f"\n{'='*60}")
        print("MODEL COMPARISON")
        print(f"{'='*60}")
        for result in evaluation_results:
            model_name = os.path.basename(result['model_path'])
            print(f"{model_name:25} | Syntax: {result['average_syntax_score']:5.1f} | Resources: {result['puppet_resource_rate']:5.1f}%")

if __name__ == "__main__":
    main()
