#
#  MIT License
#
#  (C) Copyright 2023 Hewlett Packard Enterprise Development LP
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#  OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#  ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#  OTHER DEALINGS IN THE SOFTWARE.
#
"""
Tests for the sls get_xnames function.
"""

import http
from dataclasses import dataclass
import mock
from click.testing import CliRunner
from libcsm.sls import get_xname
from libcsm.tests.mock_objects.mock_http import MockHTTPResponse

@dataclass()
class MockSetup:
    """
    Setup variables that are reused in tests
    """
    mock_components = [
        {
            'Parent': 'par1', 'Xname': 'xname1',
            'ExtraProperties': {'Aliases': ['ncn-w001'], 'A': 100}
        }, {
            'Parent': 'par2', 'Xname': 'xname2',
            'ExtraProperties': {'Aliases': ['ncn-s002'], 'A': 101}
        },
    ]
    mock_status = http.HTTPStatus.OK
    mock_http_response = MockHTTPResponse(mock_components, mock_status)


@mock.patch('kubernetes.config.load_kube_config')
@mock.patch('libcsm.api.Auth', spec=True)
@mock.patch('libcsm.sls.api.API.get_management_components_from_sls', spec=True)
class TestGetXname:
    """
    Testing the sls get_xnames function.
    """
    mock_setup = MockSetup

    def test_get_management_components_from_sls(self, mock_management_components, *_) -> None:
        """
        Tests successful run of get_xname main function.
        """
        mock_management_components.return_value = self.mock_setup.mock_http_response
        cli_runner = CliRunner()
        result = cli_runner.invoke(get_xname.main, ["--hostname", "ncn-w001"])
        assert result.exit_code == 0
        assert result.output == 'xname1\n'

    def test_get_management_components_from_sls_error(self, mock_management_components, *_) -> None:
        """
        Tests unsuccessful run of get_xname main function.
        """
        mock_management_components.return_value = self.mock_setup.mock_http_response
        cli_runner = CliRunner()
        result = cli_runner.invoke(get_xname.main, ["--hostname", "bad-hostname"])
        assert result.exit_code == 1
