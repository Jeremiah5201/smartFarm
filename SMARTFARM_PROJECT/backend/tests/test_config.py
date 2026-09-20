from pathlib import Path
import tempfile
import unittest

from app.config import load_settings


class ConfigTests(unittest.TestCase):
    def test_loads_local_env_and_creates_sms_client(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "SMS_PROVIDER=africastalking",
                        "AFRICASTALKING_USERNAME=sandbox",
                        "AFRICASTALKING_API_KEY=test-key",
                        "AFRICASTALKING_BASE_URL=https://api.sandbox.africastalking.com/version1/messaging",
                        "SMS_SENDER_ID=SMARTFARM",
                    ]
                ),
                encoding="utf-8",
            )

            settings = load_settings(env_path, environ={})
            client = settings.create_sms_client()

            self.assertEqual(settings.africastalking_username, "sandbox")
            self.assertEqual(settings.africastalking_api_key, "test-key")
            self.assertEqual(client._endpoint, settings.africastalking_base_url)

    def test_process_environment_overrides_env_file(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "SMS_PROVIDER=africastalking\n"
                "AFRICASTALKING_USERNAME=file-user\n"
                "AFRICASTALKING_API_KEY=file-key\n",
                encoding="utf-8",
            )

            settings = load_settings(
                env_path,
                environ={
                    "SMS_PROVIDER": "africastalking",
                    "AFRICASTALKING_USERNAME": "process-user",
                    "AFRICASTALKING_API_KEY": "process-key",
                },
            )

            self.assertEqual(settings.africastalking_username, "process-user")
            self.assertEqual(settings.africastalking_api_key, "process-key")

    def test_requires_sms_credentials(self):
        with self.assertRaisesRegex(ValueError, "AFRICASTALKING_API_KEY"):
            load_settings(
                environ={
                    "SMS_PROVIDER": "africastalking",
                    "AFRICASTALKING_USERNAME": "sandbox",
                }
            )
