# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from .generate_hash_leads import LeadHashGenerator
from .text_analyzer import TextAnalyzer

_lead_hash_generator = None


def get_lead_hash_generator() -> LeadHashGenerator:
    global _lead_hash_generator

    if _lead_hash_generator is None:
        _lead_hash_generator = LeadHashGenerator()

    return _lead_hash_generator
