import json
import os
from typing import Dict, Any
from configs import DEFAULT_LANG


class LanguageManager:
    _instance = None
    _languages: Dict[str, Dict[str, Any]] = {}
    _default_lang = DEFAULT_LANG

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LanguageManager, cls).__new__(cls)
            cls._instance._load_languages()
        return cls._instance

    def _load_languages(self):
        """Load all language files from the languages directory"""
        languages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "languages")

        if not os.path.exists(languages_dir):
            os.makedirs(languages_dir)

        for file_name in os.listdir(languages_dir):
            if file_name.endswith('.json'):
                lang_code = file_name.split('.')[0]
                file_path = os.path.join(languages_dir, file_name)

                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        self._languages[lang_code] = json.load(file)
                except Exception as e:
                    print(f"Error loading language file {file_name}: {e}")

    def _get_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """
        Get a value from nested dictionaries using dot notation
        Example: "user.messages.start" -> data["user"]["messages"]["start"]
        """
        if "." not in key_path:
            return data.get(key_path)

        parts = key_path.split(".")
        current = data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def get_text(self, key: str, lang: str = None, **kwargs) -> str:
        """
        Get a text by key in the specified language.
        Falls back to default language if key not found.
        Supports nested keys with dot notation: "user.messages.start"

        Args:
            key: The text key with optional dot notation
            lang: Language code (e.g., 'en', 'uk')
            **kwargs: Format parameters for the text

        Returns:
            Translated text
        """
        lang = lang or self._default_lang

        if lang in self._languages:
            text = self._get_nested_value(self._languages[lang], key)
            if text is not None:
                pass
            elif self._default_lang in self._languages:
                text = self._get_nested_value(self._languages[self._default_lang], key)
            else:
                return key
        else:
            text = self._get_nested_value(self._languages.get(self._default_lang, {}), key)
            if text is None:
                return key

        try:
            return text.format(**kwargs)
        except KeyError:
            return text

    def get_available_languages(self) -> list:
        """Get list of available language codes"""
        return list(self._languages.keys())


language_manager = LanguageManager()
