# create file: finetune_puppet_model.py
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    default_data_collator
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)
from datasets import Dataset
import json

class PuppetModelTrainer:
    def __init__(self, base_model_path="./stable-code-3b-base"):
        self.base_model_path = base_model_path
        
    def load_dataset(self, json_file):
        """Load the training dataset"""
        print(f"Loading dataset from {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to Hugging Face Dataset
        dataset = Dataset.from_list(data)
        return dataset
    
    def setup_model_and_tokenizer(self):
        """Setup model with QLoRA configuration"""
        print("Setting up QLoRA configuration...")
        
        # QLoRA configuration - 4-bit quantization optimized for RTX 5070 TI
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_storage=torch.bfloat16
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_path)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with quantization
        print("Loading model with 4-bit quantization...")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_path,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Prepare model for training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # LoRA configuration - optimized for code generation with stronger adaptation
        lora_config = LoraConfig(
            r=64,  # Higher rank for stronger adaptation
            lora_alpha=128,  # Higher alpha for stronger signal
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.1,  # Slightly higher dropout
            bias="none",
            task_type="CAUSAL_LM",
            inference_mode=False
        )
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        
        print("Model setup complete!")
        print(f"Trainable parameters: {self.model.print_trainable_parameters()}")
    
    def tokenize_function(self, examples):
        """Tokenize the examples"""
        # Tokenize the texts with padding
        tokenized = self.tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",  # Pad to max length
            max_length=512,
            return_tensors=None
        )
        
        # For causal LM, labels are the same as input_ids
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    def train(self, dataset_file, output_dir="puppet-finetuned-model"):
        """Main training function"""
        # Load dataset
        dataset = self.load_dataset(dataset_file)
        
        # Setup model
        self.setup_model_and_tokenizer()
        
        # Tokenize dataset
        print("Tokenizing dataset...")
        tokenized_dataset = dataset.map(
            self.tokenize_function, 
            batched=True,
            remove_columns=dataset.column_names  # Remove original columns
        )
        
        # Training arguments - optimized for RTX 5070 TI (16GB VRAM)
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=10,  # More epochs for small dataset
            per_device_train_batch_size=1,  # Smaller batch for better learning
            gradient_accumulation_steps=16,  # Maintain effective batch size
            warmup_steps=10,  # Fewer warmup steps for small dataset
            logging_steps=1,
            save_steps=25,
            eval_strategy="no",  # Fixed parameter name
            save_strategy="steps",
            learning_rate=5e-4,  # Higher learning rate for stronger signal
            weight_decay=0.01,
            max_grad_norm=1.0,
            fp16=True,
            dataloader_pin_memory=False,
            push_to_hub=False,
            report_to="none",  # Disable wandb/tensorboard for simplicity
            remove_unused_columns=True,  # Let trainer handle column removal
            seed=42
        )
        
        # Use default data collator since we're padding in tokenization
        data_collator = default_data_collator
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator
        )
        
        # Start training
        print("Starting training...")
        trainer.train()
        
        # Save the model
        print(f"Saving fine-tuned model to {output_dir}")
        trainer.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        print("Training complete!")
        
    def test_model(self, model_path, test_prompt="# Create a simple file resource"):
        """Test the fine-tuned model with a sample prompt"""
        print(f"\nTesting model with prompt: {test_prompt}")
        
        # Load the fine-tuned model
        model = AutoModelForCausalLM.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Generate text
        inputs = tokenizer(test_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Generated Puppet code:\n{generated_text}")
        return generated_text

# Usage:
if __name__ == "__main__":
    trainer = PuppetModelTrainer()
    
    # Check if base model exists
    import os
    if not os.path.exists("./stable-code-3b-base"):
        print("Error: Base model not found. Please run download_model.py first.")
        exit(1)
    
    # Check if training data exists
    if not os.path.exists("../data_processing/puppet_training_data.json"):
        print("Error: Training data not found. Please run create_training_dataset.py first.")
        exit(1)
    
    print("=== Starting Puppet LLM Fine-tuning with QLoRA ===")
    
    # Train on the full dataset (66 examples)
    trainer.train(
        dataset_file="../data_processing/puppet_training_data.json",
        output_dir="./puppet-finetuned-model"
    )
    
    # Test the model
    trainer.test_model("./puppet-finetuned-model")