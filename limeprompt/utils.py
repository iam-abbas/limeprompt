"""Utility functions for the Limeprompt library."""

import json
import re
from typing import Any, Dict, Type

from pydantic import BaseModel

from .exceptions import OutputExtractionError


def generate_prompt(
    prompt: str, variables: Dict[str, Any], output_model: Type[BaseModel]
) -> str:
    """
    Generate the full prompt with variables and output format instructions.

    Args:
        prompt (str): The prompt template.
        variables (Dict[str, Any]): The variables to use in the prompt.
        output_model (Type[BaseModel]): The Pydantic model for the output.

    Returns:
        str: The generated prompt.
    """
    variable_str = "\n".join(
        f"<{key}>\n{value}\n</{key}>" for key, value in variables.items()
    )

    output_format = json.dumps({field: "string" for field in output_model.model_fields})

    return f"""
    <rules>
    - You will follow the prompt strictly
    - You will adhere to output format strictly
    - Think before you perform the action, think through the <prompt> in chain of thought manner and clearly outline your thinking process in <thinking></thinking> tag
    - Output in provided format should be provided in <output></output> with strict json format with nothing more than pure json. No backquotes and no explanations. Always return json in provided format

    <prompt>
    {prompt}
    </prompt>

    <variables>
    {variable_str}
    </variables>

    <output_format_instructions>
    {output_format}
    </output_format_instructions>
    """


def extract_thinking(content: str) -> str:
    """
    Extract the thinking (chain of thought) from the API response.

    Args:
        content (str): The full API response content.

    Returns:
        str: The extracted thinking content.
    """
    thinking_match = re.search(r"<thinking>(.*?)</thinking>", content, re.DOTALL)
    return thinking_match.group(1).strip() if thinking_match else ""


def extract_output(content: str) -> str:
    """
    Extract the output JSON from the API response.

    Args:
        content (str): The full API response content.

    Returns:
        str: The extracted output JSON string.

    Raises:
        OutputExtractionError: If unable to extract the output.
    """
    output_match = re.search(r"<output>(.*?)</output>", content, re.DOTALL)
    if output_match:
        return output_match.group(1).strip()
    raise OutputExtractionError("Unable to extract output from API response")
