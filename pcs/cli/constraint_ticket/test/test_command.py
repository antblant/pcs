from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from unittest import TestCase

from pcs.test.tools.pcs_mock import mock
from pcs.cli.common.errors import CmdLineInputError
from pcs.cli.constraint_ticket import command

class AddTest(TestCase):
    @mock.patch("pcs.cli.constraint_ticket.command.parse_args.parse_add")
    def test_call_library_with_correct_attrs(self, mock_parse_add):
        mock_parse_add.return_value = (
            "ticket", "resource_id", "", {"loss-policy": "fence"}
        )
        lib = mock.MagicMock()
        lib.constraint_ticket = mock.MagicMock()
        lib.constraint_ticket.add = mock.MagicMock()

        command.add(lib, ["argv"], {"force": True, "autocorrect": True})

        mock_parse_add.assert_called_once_with(["argv"])
        lib.constraint_ticket.add.assert_called_once_with(
            "ticket", "resource_id", {"loss-policy": "fence"},
            autocorrection_allowed=True,
            resource_in_clone_alowed=True,
            duplication_alowed=True,
        )

    @mock.patch("pcs.cli.constraint_ticket.command.parse_args.parse_add")
    def test_refuse_resource_role_in_options(self, mock_parse_add):
        mock_parse_add.return_value = (
            "ticket", "resource_id", "resource_role", {"rsc-role": "master"}
        )
        lib = None
        self.assertRaises(
            CmdLineInputError,
            lambda: command.add(
                lib,
                ["argv"],
                {"force": True, "autocorrect": True},
            )
        )

    @mock.patch("pcs.cli.constraint_ticket.command.parse_args.parse_add")
    def test_put_resource_role_to_options_for_library(self, mock_parse_add):
        mock_parse_add.return_value = (
            "ticket", "resource_id", "resource_role", {"loss-policy": "fence"}
        )
        lib = mock.MagicMock()
        lib.constraint_ticket = mock.MagicMock()
        lib.constraint_ticket.add = mock.MagicMock()

        command.add(lib, ["argv"], {"force": True, "autocorrect": True})

        mock_parse_add.assert_called_once_with(["argv"])
        lib.constraint_ticket.add.assert_called_once_with(
            "ticket", "resource_id",
            {"loss-policy": "fence", "rsc-role": "resource_role"},
            autocorrection_allowed=True,
            resource_in_clone_alowed=True,
            duplication_alowed=True,
        )
