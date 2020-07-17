# (C) Copyright [2020] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
from unittest import TestCase
from mock import patch

from textwrap import dedent
import tempfile
import requests
from hpecp import ContainerPlatformClient, ContainerPlatformClientException


class MockResponse:
    def __init__(
        self,
        json_data,
        status_code,
        headers,
        raise_for_status_flag=False,
        text_data="",
    ):
        self.json_data = json_data
        self.text = text_data
        self.status_code = status_code
        self.raise_for_status_flag = raise_for_status_flag
        self.headers = headers

    def raise_for_status(self):
        if self.raise_for_status_flag:
            self.text = "some error occurred"
            raise requests.exceptions.HTTPError()
        else:
            return

    def json(self):
        return self.json_data


class TestCreateFromProperties(TestCase):
    def test_create_from_config_file_factory_method(self):
        file_data = dedent(
            """[default]
                              api_host = 127.0.0.1
                              api_port = 8080
                              use_ssl = True
                              verify_ssl = False
                              warn_ssl = True
                              username = admin
                              password = admin123"""
        )

        tmp = tempfile.NamedTemporaryFile(delete=True)
        try:
            tmp.write(file_data.encode("utf-8"))
            tmp.flush()

            client = ContainerPlatformClient.create_from_config_file(
                config_file=tmp.name
            )
            self.assertEqual(client.username, "admin")
            self.assertEqual(client.password, "admin123")
            self.assertEqual(client.api_host, "127.0.0.1")
            self.assertEqual(client.api_port, 8080)
            self.assertEqual(client.use_ssl, True)
            self.assertEqual(client.verify_ssl, False)
            self.assertEqual(client.warn_ssl, True)
        finally:
            tmp.close()


class TestCreateFromEnvVar(TestCase):
    @patch.dict(os.environ, {"HPECP_USERNAME": "test_username"})
    def test_create_from_env_var_factory_method_with_missing_env_values(self):

        try:
            client = ContainerPlatformClient.create_from_env()
        except ContainerPlatformClientException as expected:
            self.assertEqual(
                expected.message,
                "Required env var 'HPECP_PASSWORD' not found.",
            )

    @patch.dict(
        os.environ,
        {
            "HPECP_USERNAME": "test_username",
            "HPECP_PASSWORD": "test_password",
            "HPECP_API_HOST": "test_apihost",
            "HPECP_API_PORT": "not_an_int",
            "HPECP_USE_SSL": "True",
            "HPECP_VERIFY_SSL": "True",
            "HPECP_WARN_SSL": "True",
        },
    )
    def test_create_from_env_var_factory_method_with_type_error(self):

        try:
            client = ContainerPlatformClient.create_from_env()
        except ContainerPlatformClientException as expected:
            self.assertEqual(
                expected.message,
                "invalid literal for int() with base 10: 'not_an_int'",
            )

    @patch.dict(
        os.environ,
        {
            "HPECP_USERNAME": "test_username",
            "HPECP_PASSWORD": "test_password",
            "HPECP_API_HOST": "test_apihost",
            "HPECP_API_PORT": "8080",
            "HPECP_USE_SSL": "True",
            "HPECP_VERIFY_SSL": "True",
            "HPECP_WARN_SSL": "True",
        },
    )
    def test_create_from_env_var_factory_method(self):

        client = ContainerPlatformClient.create_from_env()

        self.assertEqual(client.username, "test_username")
        self.assertEqual(client.password, "test_password")
        self.assertEqual(client.api_host, "test_apihost")
        self.assertEqual(client.api_port, 8080)
        self.assertEqual(client.use_ssl, True)
        self.assertEqual(client.verify_ssl, True)
        self.assertEqual(client.warn_ssl, True)


class TestAuth(TestCase):

    # pylint: disable=no-method-argument
    def mocked_requests_post(*args, **kwargs):
        if args[0] == "http://127.0.0.1:8080/api/v1/login":
            return MockResponse(
                json_data={},
                status_code=200,
                headers={
                    "location": (
                        "/api/v1/session/df1bfacb-xxxx-xxxx-xxxx-c8f57d8f3c71"
                    )
                },
            )
        raise RuntimeError("Unhandle POST request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post)
    def test_create_session(self, mock_post):

        client = ContainerPlatformClient(
            username="admin",
            password="admin123",
            api_host="127.0.0.1",
            api_port=8080,
            use_ssl=False,
        )

        self.assertIsInstance(client.create_session(), ContainerPlatformClient)

    @patch("requests.post", side_effect=mocked_requests_post)
    def test_create_session_chained(self, mock_post):

        client = ContainerPlatformClient(
            username="admin",
            password="admin123",
            api_host="127.0.0.1",
            api_port=8080,
            use_ssl=False,
        ).create_session()

        self.assertIsInstance(client, ContainerPlatformClient)

    def mocked_requests_post_ssl(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/login":
            return MockResponse(
                json_data={},
                status_code=200,
                headers={
                    "location": (
                        "/api/v1/session/df1bfacb-xxxx-xxxx-xxxx-c8f57d8f3c71"
                    )
                },
            )
        raise RuntimeError("Unhandle POST request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post_ssl)
    def test_auth_ssl(self, mock_post):

        client = ContainerPlatformClient(
            username="admin",
            password="admin123",
            api_host="127.0.0.1",
            api_port=8080,
            use_ssl=True,
        )
        client.create_session()

    def mocked_requests_post_return_500(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/login":
            return MockResponse(
                json_data={},
                status_code=500,
                headers={},
                raise_for_status_flag=True,
            )
        raise RuntimeError("Unhandle POST request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post_return_500)
    def test_auth_ssl_with_error(self, mock_post):

        client = ContainerPlatformClient(
            username="admin",
            password="admin123",
            api_host="127.0.0.1",
            api_port=8080,
            use_ssl=True,
        )

        with self.assertRaises(requests.exceptions.HTTPError):
            client.create_session()
