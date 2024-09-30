from anthropic import Anthropic
from pydantic import BaseModel
from limeprompt import Limeprompt


# Define your output structure
class Email(BaseModel):
    subject: str
    message: str


def main():
    # Set up your Anthropic client
    anthropic_client = Anthropic(api_key="your-api-key")

    # Create a Limeprompt instance
    lp = Limeprompt(
        model_client=anthropic_client,
        model_name="claude-3-5-sonnet-20240620",
        prompt="Write an email to <name> about <topic>",
        variables={"name": "Alice", "topic": "limes"},
        output_model=Email,
        max_tokens=1024,
    )

    # Run and get your results
    result = lp.run()

    print(f"Subject: {result.output.subject}")
    print(f"Message: {result.output.message}")
    print(f"\nChain of Thought:\n{result.chain_of_thought}")


if __name__ == "__main__":
    main()
