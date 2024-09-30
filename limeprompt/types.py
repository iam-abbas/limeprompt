"""Type definitions for the Limeprompt library."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LimepromptOutput(Generic[T]):
    """
    A class to represent the output of a Limeprompt run.

    Attributes:
        output (T): The generated output, an instance of the provided Pydantic model.
        chain_of_thought (str): The chain of thought reasoning behind the generated output.
    """

    def __init__(self, output: T, chain_of_thought: str):
        self.output = output
        self.chain_of_thought = chain_of_thought
