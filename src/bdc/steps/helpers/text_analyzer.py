# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

import difflib

from autocorrect import Speller
from pylanguagetool import api as ltp
from spellchecker import SpellChecker

from logger import get_logger

log = get_logger()


class TextAnalyzer:
    """
    A class that provides text analysis functionalities such as spell checking, correction, and error detection.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.spell_checker_insts = {}
        self.speller_insts = {}
        self.plt_insts = {}

    def _get_spell_checker(self, lang_setting):
        """
        Get an instance of SpellChecker for the specified language.

        Args:
            lang_setting (str): The language setting.

        Returns:
            SpellChecker: An instance of SpellChecker for the specified language, or None if the language is not supported.
        """
        if lang_setting not in self.spell_checker_insts:
            try:
                self.spell_checker_insts[lang_setting] = SpellChecker(
                    language=lang_setting
                )
            except Exception:
                log.warn(
                    f"Language '{lang_setting}' is not supported or does not exist."
                )
                return None
        return self.spell_checker_insts[lang_setting]

    def _get_speller(self, lang_setting):
        """
        Get an instance of Speller for the specified language.

        Args:
            lang_setting (str): The language setting.

        Returns:
            Speller: An instance of Speller for the specified language, or None if the language is not supported.
        """
        if lang_setting not in self.speller_insts:
            try:
                self.speller_insts[lang_setting] = Speller(lang=lang_setting)
            except Exception:
                log.warn(
                    f"Language '{lang_setting}' is not supported or does not exist."
                )
                return None
        return self.speller_insts[lang_setting]

    def _find_differences(self, text1, text2):
        """
        Compare two texts and return a list of differences.

        Args:
            text1 (str): The first text.
            text2 (str): The second text.

        Returns:
            list: A list of differences.
        """
        diff = difflib.ndiff(text1.splitlines(), text2.splitlines())
        return list(diff)

    def correct_text(self, text, language="en"):
        """
        Correct the spelling of the given text using the specified language.

        Args:
            text (str): The text to be corrected.
            language (str, optional): The language setting. Defaults to "en".

        Returns:
            str: The corrected text.
        """
        speller = self._get_speller(language)
        spell_checker = self._get_spell_checker(language)

        if speller is None and spell_checker is None:
            log.warn(
                f"Could not find a spell checker or speller for language '{language}'."
            )
            return text

        speller_corrected_text = speller(text) if speller is not None else text
        log.info(f"Speller corrected text: {speller_corrected_text}")
        split_word = speller_corrected_text.split()
        log.info(f"Split word: {split_word}")
        spell_checker_corrected_text = (
            " ".join(
                spell_checker.correction(word)
                if spell_checker.correction(word) is not None
                else word
                for word in speller_corrected_text.split()
            )
            if spell_checker is not None
            else text
        )
        log.info(f"Spell checker corrected text: {spell_checker_corrected_text}")

        return spell_checker_corrected_text

    def find_number_of_spelling_errors(self, text, language="en"):
        """
        Find the number of spelling errors in the given text using the specified language.

        Args:
            text (str): The text to be checked.
            language (str, optional): The language setting. Defaults to "en".

        Returns:
            int: The number of spelling errors.
        """
        return len(self.find_spelling_errors(text, language))

    def find_spelling_errors(self, text, language="en"):
        """
        Find the spelling errors in the given text using the specified language.

        Args:
            text (str): The text to be checked.
            language (str, optional): The language setting. Defaults to "en".

        Returns:
            list: A list of spelling errors.
        """
        corrected_text = self.correct_text(text, language)
        differences = self._find_differences(text, corrected_text)
        return differences

    def find_number_of_grammatical_errors(self, inp_text, language="en"):
        """
        Finds the number of grammatical errors in the input text.

        Args:
            inp_text (str): The input text to be analyzed.
            language (str, optional): The language of the text. Defaults to "en".

        Returns:
            int: The number of grammatical errors found in the text.
        """
        if inp_text is None or len(inp_text) == 0:
            return None
        errors = ltp.check(
            inp_text, api_url="https://languagetool.org/api/v2/", lang=language
        )
        log.info(f"Errors: {errors['matches']}")
        return len(errors)
