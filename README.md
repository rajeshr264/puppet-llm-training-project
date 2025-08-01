# Puppet LLM Training Project

A machine learning project for training language models on Puppet configuration management code.

## Project Structure

```
puppet-llm-training-project/
├── data_collection/     # Scripts for collecting training data
├── data_processing/     # Data preprocessing and cleaning
├── deployment/          # Model deployment scripts
├── evaluation/          # Model evaluation and metrics
├── models/             # Trained models and model artifacts
├── processed_data/     # Processed training data
├── raw_data/           # Raw data collection
├── scripts/            # Utility scripts
└── training/           # Model training scripts
```

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

### Prerequisites
- Python 3.12+
- uv package manager

### Installation

1. Install uv (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone <your-repo-url>
cd puppet-llm-training-project
```

3. Install dependencies:
```bash
uv sync
```

4. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate     # On Windows
```

## Usage

[Add usage instructions here]

## Contributing

[Add contributing guidelines here]

## License

[Add license information here]