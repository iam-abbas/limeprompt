import unittest
import logging
from unittest.mock import create_autospec, Mock, patch
from anthropic import Anthropic
from openai import OpenAI
from limeprompt import Limeprompt, LimepromptOutput, LimepromptError, InvalidInputError
from tests._types import SampleEmail


class TestLimeprompt(unittest.TestCase):
    def setUp(self):
        self.mock_anthropic = create_autospec(Anthropic)
        self.mock_anthropic.messages = Mock()
        self.mock_anthropic.messages.create = Mock()

        self.mock_openai = create_autospec(OpenAI)
        self.mock_openai.chat = Mock()
        self.mock_openai.chat.completions = Mock()
        self.mock_openai.chat.completions.create = Mock()

        self.limeprompt_anthropic = Limeprompt(
            model_client=self.mock_anthropic,
            model_name="test-model",
            prompt="Test prompt",
            variables={"test": "value"},
            output_model=SampleEmail,
            max_tokens=100,
            include_chain_of_thought=True,
            log_level=logging.WARNING,
        )

        self.limeprompt_openai = Limeprompt(
            model_client=self.mock_openai,
            model_name="test-model",
            prompt="Test prompt",
            variables={"test": "value"},
            output_model=SampleEmail,
            max_tokens=100,
            include_chain_of_thought=False,
            log_level=logging.INFO,
        )

    def test_initialization(self):
        self.assertIsInstance(self.limeprompt_anthropic, Limeprompt)
        self.assertIsInstance(self.limeprompt_openai, Limeprompt)

    def test_invalid_input(self):
        with self.assertRaises(InvalidInputError):
            Limeprompt(
                model_client="not_a_valid_client",
                model_name="test-model",
                prompt="Test prompt",
                variables={"test": "value"},
                output_model=SampleEmail,
                max_tokens=100,
            )

    @patch("limeprompt.core.generate_prompt")
    @patch("limeprompt.core.extract_thinking")
    @patch("limeprompt.core.extract_output")
    def test_run_success_anthropic(
        self, mock_extract_output, mock_extract_thinking, mock_generate_prompt
    ):
        mock_generate_prompt.return_value = "Generated prompt"
        mock_extract_thinking.return_value = "Chain of thought"
        mock_extract_output.return_value = '{"subject": "Test", "message": "Hello"}'

        mock_message = Mock()
        mock_message.content = [Mock(text="API response")]
        self.mock_anthropic.messages.create.return_value = mock_message

        result = self.limeprompt_anthropic.run()

        self.assertIsInstance(result, LimepromptOutput)
        self.assertIsInstance(result.output, SampleEmail)
        self.assertEqual(result.output.subject, "Test")
        self.assertEqual(result.output.message, "Hello")
        self.assertEqual(result.chain_of_thought, "Chain of thought")

    @patch("limeprompt.core.generate_prompt")
    @patch("limeprompt.core.extract_thinking")
    @patch("limeprompt.core.extract_output")
    def test_run_success_openai(
        self, mock_extract_output, mock_extract_thinking, mock_generate_prompt
    ):
        mock_generate_prompt.return_value = "Generated prompt"
        mock_extract_thinking.return_value = "Chain of thought"
        mock_extract_output.return_value = '{"subject": "Test", "message": "Hello"}'

        mock_completion = Mock()
        mock_completion.choices = [Mock(message=Mock(content="API response"))]
        self.mock_openai.chat.completions.create.return_value = mock_completion

        result = self.limeprompt_openai.run()

        self.assertIsInstance(result, LimepromptOutput)
        self.assertIsInstance(result.output, SampleEmail)
        self.assertEqual(result.output.subject, "Test")
        self.assertEqual(result.output.message, "Hello")
        self.assertIsNone(result.chain_of_thought)

    @patch("limeprompt.core.generate_prompt")
    def test_run_api_error_anthropic(self, mock_generate_prompt):
        mock_generate_prompt.return_value = "Generated prompt"
        self.mock_anthropic.messages.create.side_effect = Exception("API Error")

        with self.assertRaises(LimepromptError):
            self.limeprompt_anthropic.run()

    @patch("limeprompt.core.generate_prompt")
    def test_run_api_error_openai(self, mock_generate_prompt):
        mock_generate_prompt.return_value = "Generated prompt"
        self.mock_openai.chat.completions.create.side_effect = Exception("API Error")

        with self.assertRaises(LimepromptError):
            self.limeprompt_openai.run()

    @patch("limeprompt.core.logger")
    def test_logging_level(self, mock_logger):
        Limeprompt(
            model_client=self.mock_anthropic,
            model_name="test-model",
            prompt="Test prompt",
            variables={"test": "value"},
            output_model=SampleEmail,
            max_tokens=100,
            log_level=logging.DEBUG,
        )
        mock_logger.setLevel.assert_called_with(logging.DEBUG)


if __name__ == "__main__":
    unittest.main()
