"""Core functionality for the Limeprompt library."""

import json
import logging
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union

from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel, ValidationError

from .exceptions import InvalidInputError, LimepromptError
from .types import LimepromptOutput
from .utils import extract_output, extract_thinking, generate_prompt

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class Limeprompt(Generic[T]):
    """Main class for generating structured output using language models."""

    def __init__(
        self,
        model_client: Union[Anthropic, OpenAI],
        model_name: str,
        prompt: str,
        variables: Dict[str, Any],
        output_model: Type[T],
        max_tokens: int,
        include_chain_of_thought: bool = True,
        log_level: Optional[int] = None,
    ):
        """
        Initialize the Limeprompt instance.

        Args:
            model_client (Union[Anthropic, OpenAI]): The Anthropic or OpenAI client instance.
            model_name (str): The name of the model to use.
            prompt (str): The prompt template.
            variables (Dict[str, Any]): The variables to use in the prompt.
            output_model (Type[T]): The Pydantic model for the output.
            max_tokens (int): The maximum number of tokens for the response.
            include_chain_of_thought (bool): Whether to include chain of thought in the output.
            log_level (Optional[int]): The logging level to use (e.g., logging.INFO, logging.WARNING).

        Raises:
            InvalidInputError: If any of the input parameters are invalid.
        """
        self._validate_inputs(
            model_client=model_client,
            model_name=model_name,
            prompt=prompt,
            variables=variables,
            output_model=output_model,
            max_tokens=max_tokens,
        )

        self.model_client = model_client
        self.model_name = model_name
        self.prompt = prompt
        self.variables = variables
        self.output_model = output_model
        self.max_tokens = max_tokens
        self.include_chain_of_thought = include_chain_of_thought

        if log_level is not None:
            logger.setLevel(log_level)

    def _validate_inputs(
        self,
        model_client: Union[Anthropic, OpenAI],
        model_name: str,
        prompt: str,
        variables: Dict[str, Any],
        output_model: Type[T],
        max_tokens: int,
    ):
        if not isinstance(model_client, (Anthropic, OpenAI)):
            raise InvalidInputError(
                "model_client must be an instance of Anthropic or OpenAI"
            )
        if not isinstance(model_name, str):
            raise InvalidInputError("model_name must be a string")
        if not isinstance(prompt, str):
            raise InvalidInputError("prompt must be a string")
        if not isinstance(variables, dict):
            raise InvalidInputError("variables must be a dictionary")
        if not issubclass(output_model, BaseModel):
            raise InvalidInputError(
                "output_model must be a subclass of pydantic.BaseModel"
            )
        if not isinstance(max_tokens, int) or max_tokens <= 0:
            raise InvalidInputError("max_tokens must be a positive integer")

    def run(self, max_tokens: int = None) -> LimepromptOutput[T]:
        """
        Run the Limeprompt instance to generate output.

        Args:
            max_tokens (int, optional): Override the default max_tokens value.

        Returns:
            LimepromptOutput[T]: The generated output and chain of thought (if included).

        Raises:
            LimepromptError: If there's an error during the process.
        """
        try:
            generated_prompt = generate_prompt(
                self.prompt,
                self.variables,
                self.output_model,
                include_chain_of_thought=self.include_chain_of_thought,
            )

            logger.info("Sending request to API with model: %s", self.model_name)

            if isinstance(self.model_client, Anthropic):
                output_content = self._run_anthropic(generated_prompt, max_tokens)
            elif isinstance(self.model_client, OpenAI):
                output_content = self._run_openai(generated_prompt, max_tokens)
            else:
                raise LimepromptError("Unsupported model client")

            chain_of_thought = (
                extract_thinking(output_content)
                if self.include_chain_of_thought
                else None
            )
            json_str = extract_output(output_content)

            data = json.loads(json_str)
            output_model = self.output_model(**data)

            logger.info("Successfully generated and validated output")
            return LimepromptOutput(
                output=output_model, chain_of_thought=chain_of_thought
            )

        except json.JSONDecodeError as e:
            logger.error("JSON decoding error: %s", str(e))
            raise LimepromptError(f"Error decoding JSON response: {str(e)}") from e
        except ValidationError as e:
            logger.error("Pydantic validation error: %s", str(e))
            raise LimepromptError(f"Error validating output model: {str(e)}") from e
        except Exception as e:
            logger.error("Unexpected error: %s", str(e))
            raise LimepromptError(f"Unexpected error occurred: {str(e)}") from e

    def _run_anthropic(self, generated_prompt: str, max_tokens: int = None) -> str:
        message = self.model_client.messages.create(
            max_tokens=max_tokens or self.max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": generated_prompt,
                }
            ],
            model=self.model_name,
        )
        return message.content[0].text

    def _run_openai(self, generated_prompt: str, max_tokens: int = None) -> str:
        chat_completion = self.model_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": generated_prompt,
                }
            ],
            max_tokens=max_tokens or self.max_tokens,
        )
        return chat_completion.choices[0].message.content
