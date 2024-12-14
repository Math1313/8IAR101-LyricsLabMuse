# AudioCraft Environment Setup Guide

This guide provides step-by-step instructions for setting up the AudioCraft environment for the LyricsLabMuse project.

## Prerequisites

- Python 3.9 installed on your system
  - To check if Python 3.9 is installed: `python3.9 --version`
  - If not installed, download from [Python's official website](https://www.python.org/downloads/release/python-3913/)

## Environment Setup

### 1. Create Virtual Environment

First, create a dedicated virtual environment for AudioCraft:

```bash
# Windows
py -3.9 -m venv .venv_audiocraft

# Unix/MacOS
python3.9 -m venv .venv_audiocraft
```

### 2. Activate Virtual Environment

```bash
# Windows
.\.venv_audiocraft\Scripts\activate 

# Unix/MacOS
source .venv_audiocraft/bin/activate
```

### 3. Install Dependencies

Install all required packages using the requirements file:

```bash
pip install -r requirements.txt
```

## Verification

To verify your installation:

1. Activate the virtual environment (if not already activated)
2. Run Python and try importing the required packages:

```python
import torch
import audiocraft
```

If no errors occur, the setup is successful.

## Common Issues and Solutions

### 1. PyTorch Installation Issues
If you encounter issues with PyTorch installation:
```bash
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

### 2. Numpy Version Conflicts
If you see Numpy version conflicts:
```bash
pip uninstall numpy
pip install numpy==1.24.3
```

## Environment Management

### Switching Between Environments

The project uses two separate environments:
- Main RAG/LLM environment (`.venv`)
- AudioCraft environment (`.venv_audiocraft`)

To switch between environments:

1. First, deactivate current environment:
```bash
deactivate
```

2. Then activate desired environment:
```bash
# For AudioCraft
.venv_audiocraft\Scripts\activate  # Windows
source .venv_audiocraft/bin/activate  # Unix/MacOS

# For main environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/MacOS
```

### Checking Active Environment
To verify which environment is active:
```bash
# Windows
where python

# Unix/MacOS
which python
```

## Additional Notes

- Always ensure you're in the correct virtual environment before running AudioCraft-related code
- The CPU version of PyTorch is installed by default. For GPU support, modify the installation command accordingly
- This setup is optimized for CPU usage. For production environments, consider GPU support for better performance

## Troubleshooting

If you encounter any issues:
1. Ensure Python 3.9 is correctly installed
2. Verify you're in the correct virtual environment
3. Try removing and recreating the virtual environment
4. Check for any conflicting Python installations

For additional help, please open an issue in the project repository.