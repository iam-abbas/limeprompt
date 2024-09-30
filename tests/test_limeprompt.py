import unittest
from unittest.mock import create_autospec, Mock, patch
from anthropic import Anthropic
from limeprompt import Limeprompt, LimepromptOutput, LimepromptError, InvalidInputError
from tests._types import SampleEmail


class TestLimeprompt(unittest.TestCase):
    def setUp(self):
        self.mock_anthropic = create_autospec(Anthropic)
        self.mock_anthropic.messages = Mock()
        self.mock_anthropic.messages.create = Mock()

        self.limeprompt = Limeprompt(
            model_client=self.mock_anthropic,
            model_name="test-model",
            prompt="Test prompt",
            variables={"test": "value"},
            output_model=SampleEmail,
            max_tokens=100,
        )

    def test_initialization(self):
        self.assertIsInstance(self.limeprompt, Limeprompt)

    def test_invalid_input(self):
        with self.assertRaises(InvalidInputError):
            Limeprompt(
                model_client="not_an_anthropic_instance",
                model_name="test-model",
                prompt="Test prompt",
                variables={"test": "value"},
                output_model=SampleEmail,
                max_tokens=100,
            )

    @patch("limeprompt.core.generate_prompt")
    @patch("limeprompt.core.extract_thinking")
    @patch("limeprompt.core.extract_output")
    def test_run_success(
        self, mock_extract_output, mock_extract_thinking, mock_generate_prompt
    ):
        mock_generate_prompt.return_value = "Generated prompt"
        mock_extract_thinking.return_value = "Chain of thought"
        mock_extract_output.return_value = '{"subject": "Test", "message": "Hello"}'

        mock_message = Mock()
        mock_message.content = [Mock(text="API response")]
        self.mock_anthropic.messages.create.return_value = mock_message

        result = self.limeprompt.run()

        self.assertIsInstance(result, LimepromptOutput)
        self.assertIsInstance(result.output, SampleEmail)
        self.assertEqual(result.output.subject, "Test")
        self.assertEqual(result.output.message, "Hello")
        self.assertEqual(result.chain_of_thought, "Chain of thought")

    @patch("limeprompt.core.generate_prompt")
    def test_run_api_error(self, mock_generate_prompt):
        mock_generate_prompt.return_value = "Generated prompt"
        self.mock_anthropic.messages.create.side_effect = Exception("API Error")

        with self.assertRaises(LimepromptError):
            self.limeprompt.run()


if __name__ == "__main__":
    unittest.main()
