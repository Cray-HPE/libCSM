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
Submodule for interacting with CSM API services.
"""
from json import loads

from urllib import request
from urllib.parse import urlencode
import base64
from kubernetes import client
from kubernetes import config
from urllib3.exceptions import MaxRetryError

SECRET = 'admin-client-auth'


class AuthException(Exception):

    """
    An exception for authorization problems from the api.Auth object.
    """

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)


class Auth:

    """
    Class for handling CSM API credentials stored in Kubernetes secrets.

    The initialization of this class passes any provided arguments along to
    kubernetes.config.load_kube_config, allowing a user to override the config
    location.
    """

    def __init__(self, **kwargs) -> None:
        config.load_kube_config(**kwargs)
        self.core = client.CoreV1Api()
        self._token = None

    def _get_secret(self) -> dict:
        """
        Fetches the Kubernetes SECRET for admin authentication.
        :return: The data dict from the resolved V1Secret.
        """
        try:
            secret = self.core.read_namespaced_secret(SECRET, 'default').data
        except client.exceptions.ApiException as error:
            print(f'Failed to resolve Kubernetes secret [{SECRET}]: {error}')
        except MaxRetryError as error:
            print(f'Failed to contact Kubernetes: {error}')
        else:
            return secret
        return {}

    def refresh_token(self) -> None:
        """
        Refreshes the authentication token.
        """
        del self.token
        credentials = self._get_secret()
        if credentials == {}:
            raise AuthException('Could not resolve an API Token!')
        data = {
            'client_id': base64.b64decode(credentials['client-id']),
            'client_secret': base64.b64decode(credentials['client-secret']),
            'grant_type': b'client_credentials',
        }
        url = base64.b64decode(credentials['endpoint']).decode('ascii')
        payload = urlencode(data).encode('utf-8')
        message = request.Request(url)

        with request.urlopen(message, payload) as handle:
            response = handle.read()
            response_data = loads(response)
            token = response_data.get('access_token')
            if token is not None:
                self._token = token

    @property
    def token(self) -> str:
        """
        The authentication token.
        """
        return self._token

    @token.deleter
    def token(self) -> None:
        """
        Handles deleting the authentication token.
        """
        self._token = None
