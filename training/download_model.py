# create file: download_model.py
from transformers import AutoModelForCausalLM, AutoTokenizer

print("Downloading Stable Code 3B model...")
model_name = "stabilityai/stable-code-3b"

# Download tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.save_pretrained("./stable-code-3b-base")

# Download model (this will take a while - ~5.4GB)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    trust_remote_code=True
)
model.save_pretrained("./stable-code-3b-base")

print("Model downloaded successfully!")