# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Felix Zailskas <felixzailskas@gmail.com>

from mock_components import get_database_mock

from database.models import Lead


def test_parser():
    leads = get_database_mock().get_all_leads()
    for lead in leads:
        assert type(lead) == Lead
