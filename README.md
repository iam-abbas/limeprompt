# Limeprompt 🍋

Lightweight prompting and parsing library for LLM models.

## What is Limeprompt?

Limeprompt is an opinionated and lightweight prompting and parsing library for LLM models. It aims to make it easy to generate structured outputs from language models. The library is designed to be simple to use, with a single use-case in mind: generating structured outputs from language models. There wont be any support for multi-agent or complex prompting use-cases.

## Installation

```bash
pip install limeprompt
```

## Example Usage

Here's a simple example to get you started:

```python
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
    prompt="Write an email to {name} about {topic}",
    variables={"name": "Alice", "topic": "limes"},
    output_model=Email,
    max_tokens=1024
)

# Run and get your zesty results!
result = lp.run()

print(f"Subject: {result.output.subject}")
print(f"Message: {result.output.message}")
```

## Not

## Contributing

You are welcome to open issues or submit PRs. Here's my todo list for the library:

- [ ] Add support for OpenAI
- [ ] Modularize the prompting techniques
- [ ] Add support for few-shot prompting

## License

Limeprompt is released under the MIT License. Feel free to use it in your projects.
