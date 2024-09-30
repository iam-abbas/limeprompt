# Limeprompt 🍋

[![PyPI version](https://img.shields.io/pypi/v/limeprompt.svg)](https://pypi.org/project/limeprompt/)

Lightweight prompting and parsing library for LLM models.

## What is Limeprompt?

Limeprompt is an opinionated and lightweight prompting and parsing library for LLM models. It aims to make it easy to generate structured outputs from language models. The library is designed to be simple to use, with a single use-case in mind: generating structured outputs from language models. There wont be any support for multi-agent or complex prompting use-cases.

## Installation

```bash
pip install limeprompt
```

## Example Usage

Here's a simple example using Anthropic's Claude:

```python
import logging
from anthropic import Anthropic
from pydantic import BaseModel
from limeprompt import Limeprompt

# Define your output structure
class Email(BaseModel):
    subject: str
    message: str

# Set up your Anthropic client
anthropic_client = Anthropic(api_key='your-api-key')

# Create a Limeprompt instance
lp = Limeprompt(
    model_client=anthropic_client,
    model_name='claude-3-5-sonnet-20240620',
    prompt="Write an email to  about ",
    variables={"name": "Alice", "topic": "limes"},
    output_model=Email,
    max_tokens=1024,
    include_chain_of_thought=True,  # Set to False to disable chain of thought
    log_level=logging.INFO  # Set the desired log level
)

# Run and get your results
result = lp.run()

print(f"Subject: {result.output.subject}")
print(f"Message: {result.output.message}")
if result.chain_of_thought:
    print(f"\nChain of Thought:\n{result.chain_of_thought}")
```

Here's an example using OpenAI:

```python
import logging
from openai import OpenAI
from pydantic import BaseModel
from limeprompt import Limeprompt

# Define your output structure
class Email(BaseModel):
    subject: str
    message: str

# Set up your OpenAI client
openai_client = OpenAI(api_key='your-api-key')

# Create a Limeprompt instance
lp = Limeprompt(
    model_client=openai_client,
    model_name='gpt-3.5-turbo',
    prompt="Write an email to  about ",
    variables={"name": "Bob", "topic": "lemons"},
    output_model=Email,
    max_tokens=1024,
    include_chain_of_thought=False,  # Disable chain of thought
    log_level=logging.WARNING  # Set log level to WARNING
)

# Run and get your results
result = lp.run()

print(f"Subject: {result.output.subject}")
print(f"Message: {result.output.message}")
```

## Contributing

You are welcome to open issues or submit PRs. Here's my todo list for the library:

- [x] Add support for OpenAI
- [x] Add logging options
- [x] Add ability to disable chain of thought
- [ ] Modularize the prompting techniques
- [ ] Add support for few-shot prompting

## License

Limeprompt is released under the MIT License. Feel free to use it in your projects.
