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
import sys
import unittest
from textwrap import dedent
import json
import yaml

import requests
from mock import patch

from hpecp import ContainerPlatformClient
from hpecp.exceptions import APIItemNotFoundException
import tempfile
from hpecp.base_resource import ResourceList

from .base_test import BaseTestCase
import six


class MockResponse:
    def __init__(
        self,
        json_data,
        status_code,
        headers,
        raise_for_status_flag=False,
        raise_connection_error=False,
        text_data="",
    ):
        self.json_data = json_data
        self.text = text_data
        self.status_code = status_code
        self.raise_for_status_flag = raise_for_status_flag
        self.raise_connection_error = raise_connection_error
        self.headers = headers

    def raise_for_status(self):
        if self.raise_for_status_flag:
            self.text = "some error occurred"
            raise requests.exceptions.HTTPError()
        if self.raise_connection_error:
            self.text = "Simulating a connection error"
            raise requests.exceptions.ConnectionError()
        else:
            return

    def json(self):
        return self.json_data


def get_client():
    client = ContainerPlatformClient(
        username="admin",
        password="admin123",
        api_host="127.0.0.1",
        api_port=8080,
        use_ssl=True,
    )
    client.create_session()
    return client


def session_mock_response():
    return MockResponse(
        json_data={},
        status_code=200,
        headers={
            "location": "/api/v1/session/df1bfacb-xxxx-xxxx-xxxx-c8f57d8f3c71"
        },
    )


def mocked_requests_get(*args, **kwargs):
    if args[0] == "https://127.0.0.1:8080/api/v1/catalog/99":
        return MockResponse(
            json_data={
                "_links": {
                    "self": {"href": "/api/v1/catalog/99"},
                    "feed": [
                        {
                            "href": (
                                "https://s3.amazonaws.com/bluedata-catalog/"
                                "bundles/catalog/external/docker/EPIC-5.0/"
                                "feeds/feed.json"
                            ),
                            "name": (
                                "BlueData EPIC-5.0 catalog feed for docker"
                            ),
                        }
                    ],
                },
                "id": "/api/v1/catalog/99",
                "distro_id": "bluedata/spark240juphub7xssl",
                "label": {
                    "name": "Spark240",
                    "description": (
                        "Spark240 multirole with Jupyter Notebook, Jupyterhub"
                        " with SSL and gateway node"
                    ),
                },
                "version": "2.8",
                "timestamp": 0,
                "isdebug": False,
                "osclass": ["centos"],
                "logo": {
                    "checksum": "1471eb59356066ed4a06130566764ea6",
                    "url": (
                        "http://10.1.0.53/catalog/logos/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "documentation": {
                    "checksum": "52f53f1b2845463b9e370d17fb80bea6",
                    "mimetype": "text/markdown",
                    "file": (
                        "/opt/bluedata/catalog/documentation/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "state": "initialized",
                "state_info": "",
            },
            status_code=200,
            headers=dict(),
        )
    if args[0] == "https://127.0.0.1:8080/api/v1/catalog/100":
        return MockResponse(
            json_data={
                "_links": {
                    "self": {"href": "/api/v1/catalog/100"},
                    "feed": [
                        {
                            "href": (
                                "https://s3.amazonaws.com/bluedata-catalog/"
                                "bundles/catalog/external/docker/EPIC-5.0/"
                                "feeds/feed.json"
                            ),
                            "name": (
                                "BlueData EPIC-5.0 catalog feed for docker"
                            ),
                        }
                    ],
                },
                "id": "/api/v1/catalog/100",
                "distro_id": "bluedata/spark240juphub7xssl",
                "label": {
                    "name": "Spark240",
                    "description": (
                        "Spark240 multirole with Jupyter Notebook, Jupyterhub"
                        " with SSL and gateway node"
                    ),
                },
                "version": "2.8",
                "timestamp": 0,
                "isdebug": False,
                "osclass": ["centos"],
                "logo": {
                    "checksum": "1471eb59356066ed4a06130566764ea6",
                    "url": (
                        "http://10.1.0.53/catalog/logos/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "documentation": {
                    "checksum": "52f53f1b2845463b9e370d17fb80bea6",
                    "mimetype": "text/markdown",
                    "file": (
                        "/opt/bluedata/catalog/documentation/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "state": "initialized",
                "state_info": "",
            },
            status_code=200,
            headers=dict(),
        )
    if args[0] == "https://127.0.0.1:8080/api/v1/catalog/101":
        raise APIItemNotFoundException(
            message="catalog not found with id: " + "/api/v1/catalog/101",
            request_method="get",
            request_url=args[0],
        )
    raise RuntimeError("Unhandle GET request: " + args[0])


def mocked_requests_post(*args, **kwargs):
    if args[0] == "https://127.0.0.1:8080/api/v1/login":
        return session_mock_response()
    raise RuntimeError("Unhandle POST request: " + args[0])


class TestCatalogGet(unittest.TestCase):
    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_catalog_id_type(self, mock_get, mock_post):

        with self.assertRaisesRegexp(
            AssertionError, "'id' must be provided and must be a str",
        ):
            get_client().catalog.get(123)

        with self.assertRaisesRegexp(
            AssertionError, "'id' must be provided and must be a str",
        ):
            get_client().catalog.get(False)

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_catalog_id_format(self, mock_get, mock_post):

        with self.assertRaisesRegexp(
            AssertionError, "'id' does not start with '/api/v1/catalog'"
        ):
            get_client().catalog.get("garbage")

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_catalog(self, mock_get, mock_post):

        catalog = get_client().catalog.get("/api/v1/catalog/99")

        with self.assertRaisesRegexp(
            APIItemNotFoundException,
            "'catalog not found with id: " + r"\/api\/v1\/catalog\/101",
        ):
            get_client().catalog.get("/api/v1/catalog/101")

    @patch("requests.get", side_effect=mocked_requests_get)
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_get_catalog_attributes(self, mock_get, mock_post):

        catalog = get_client().catalog.get("/api/v1/catalog/99")
        self.assertEqual(catalog.distro_id, "bluedata/spark240juphub7xssl")
        self.assertEqual(
            catalog.documentation_checksum, "52f53f1b2845463b9e370d17fb80bea6"
        )
        self.assertEqual(
            catalog.documentation_file,
            "/opt/bluedata/catalog/documentation/bluedata-spark240juphub7xssl-2.8",
        )
        self.assertEqual(catalog.documentation_mimetype, "text/markdown")
        self.assertEqual(
            catalog.feed,
            [
                {
                    "href": "https://s3.amazonaws.com/bluedata-catalog/bundles/catalog/external/docker/EPIC-5.0/feeds/feed.json",
                    "name": "BlueData EPIC-5.0 catalog feed for docker",
                }
            ],
        )
        self.assertEqual(catalog.id, "/api/v1/catalog/99")
        self.assertEqual(catalog.isdebug, False)
        self.assertEqual(
            catalog.label_description,
            "Spark240 multirole with Jupyter Notebook, Jupyterhub with SSL and gateway node",
        )
        self.assertEqual(catalog.label_name, "Spark240")
        self.assertEqual(
            catalog.logo_checksum, "1471eb59356066ed4a06130566764ea6"
        )
        self.assertEqual(
            catalog.logo_url,
            "http://10.1.0.53/catalog/logos/bluedata-spark240juphub7xssl-2.8",
        )
        self.assertEqual(catalog.osclass, ["centos"])
        self.assertEqual(catalog.self_href, "/api/v1/catalog/99")
        self.assertEqual(catalog.state, "initialized")
        self.assertEqual(catalog.state_info, "")
        self.assertEqual(catalog.timestamp, 0)
        self.assertEqual(catalog.version, "2.8")


catalog_list_json = {
    "_links": {
        "self": {"href": "/api/v1/catalog/"},
        "feedlog": {"href": "/api/v1/catalog/feedlog"},
        "feed": [
            {
                "href": "http://127.0.0.1:8080/api/v1/feed/local",
                "name": "Feed generated from local bundles.",
            },
            {
                "href": (
                    "https://s3.amazonaws.com/bluedata-catalog/bundles/"
                    "catalog/external/docker/EPIC-5.0/feeds/feed.json"
                ),
                "name": "BlueData EPIC-5.0 catalog feed for docker",
            },
        ],
    },
    "catalog_api_version": 6,
    "feeds_refresh_period_seconds": 86400,
    "feeds_read_counter": 5,
    "catalog_write_counter": 5,
    "_embedded": {
        "independent_catalog_entries": [
            {
                "_links": {
                    "self": {"href": "/api/v1/catalog/29"},
                    "feed": [
                        {
                            "href": (
                                "https://s3.amazonaws.com/bluedata-catalog/"
                                "bundles/catalog/external/docker/EPIC-5.0/"
                                "feeds/feed.json"
                            ),
                            "name": (
                                "BlueData EPIC-5.0 catalog feed for docker"
                            ),
                        }
                    ],
                },
                "distro_id": "bluedata/spark240juphub7xssl",
                "label": {
                    "name": "Spark240",
                    "description": (
                        "Spark240 multirole with Jupyter Notebook, Jupyterhub"
                        " with SSL and gateway node"
                    ),
                },
                "version": "2.8",
                "timestamp": 0,
                "isdebug": False,
                "osclass": ["centos"],
                "logo": {
                    "checksum": "1471eb59356066ed4a06130566764ea6",
                    "url": (
                        "http://10.1.0.53/catalog/logos/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "documentation": {
                    "checksum": "52f53f1b2845463b9e370d17fb80bea6",
                    "mimetype": "text/markdown",
                    "file": (
                        "/opt/bluedata/catalog/documentation/"
                        "bluedata-spark240juphub7xssl-2.8"
                    ),
                },
                "state": "initialized",
                "state_info": "",
            }
        ]
    },
}


class TestCatalogList(unittest.TestCase):
    def mocked_requests_list(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog":
            return MockResponse(
                json_data=catalog_list_json, status_code=200, headers=dict(),
            )
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.get", side_effect=mocked_requests_list)
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_list(self, mock_get, mock_post):

        catalog_list = get_client().catalog.list()
        self.assertIsInstance(catalog_list, ResourceList)


class TestCatalogInstall(BaseTestCase):
    def mocked_requests_install(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog/99":
            return MockResponse(json_data={}, status_code=204, headers=dict())
        if args[0] == "https://127.0.0.1:8080/api/v1/login":
            return session_mock_response()
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_install)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_install(self, mock_get, mock_post):

        client = get_client()

        with self.assertRaisesRegexp(
            AssertionError, "'id' must be provided and must be a str",
        ):
            client.catalog.install(999)

        with self.assertRaisesRegexp(
            AssertionError, "'id' does not start with '/api/v1/catalog'",
        ):
            client.catalog.install("garbage")

        with self.assertRaisesRegexp(
            APIItemNotFoundException,
            "'catalog not found with id: /api/v1/catalog/101'",
        ):
            client.catalog.install("/api/v1/catalog/101")

        client.catalog.install("/api/v1/catalog/99")

    @patch("requests.post", side_effect=mocked_requests_install)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_install_cli_with_parameter_assertion_error(
        self, mock_get, mock_post
    ):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.install("garbage")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = "'id' does not start with '/api/v1/catalog'"

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(stderr.endswith(expected_stderr))

    @patch("requests.post", side_effect=mocked_requests_install)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_install_cli_with_catalog_id_not_found(
        self, mock_get, mock_post
    ):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.install("/api/v1/catalog/101")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = "catalog not found with id: /api/v1/catalog/101"

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(
            stderr.endswith(expected_stderr),
            (
                "stderr = `{}`\n".format(stderr)
                + "stderr does not end with `{}`".format(expected_stderr)
            ),
        )

    @patch("requests.post", side_effect=mocked_requests_install)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_install_cli_success(self, mock_get, mock_post):

        try:
            hpecp = self.cli.CLI()
            hpecp.catalog.install("/api/v1/catalog/99")
        except Exception:
            self.fail("Unexpected exception")

        stdout = self.out.getvalue().strip()

        # successful refresh should not output anything
        expected_stdout = ""

        self.assertEqual(stdout, "")


class TestCatalogRefresh(BaseTestCase):
    def mocked_requests_refresh(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog/99":
            return MockResponse(json_data={}, status_code=204, headers=dict())
        if args[0] == "https://127.0.0.1:8080/api/v1/login":
            return session_mock_response()
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_refresh)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_refresh(self, mock_get, mock_post):

        client = get_client()

        with self.assertRaisesRegexp(
            AssertionError, "'id' must be provided and must be a str",
        ):
            client.catalog.install(999)

        with self.assertRaisesRegexp(
            AssertionError, "'id' does not start with '/api/v1/catalog'",
        ):
            client.catalog.refresh("garbage")

        with self.assertRaisesRegexp(
            APIItemNotFoundException,
            "'catalog not found with id: /api/v1/catalog/101'",
        ):
            client.catalog.refresh("/api/v1/catalog/101")

        client.catalog.refresh("/api/v1/catalog/99")

    @patch("requests.post", side_effect=mocked_requests_refresh)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_refresh_cli_with_parameter_assertion_error(
        self, mock_get, mock_post
    ):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.refresh("garbage")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = "'id' does not start with '/api/v1/catalog'"

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(stderr.endswith(expected_stderr))

    @patch("requests.post", side_effect=mocked_requests_refresh)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_refresh_cli_with_catalog_id_not_found(
        self, mock_get, mock_post
    ):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.refresh("/api/v1/catalog/101")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = "catalog not found with id: /api/v1/catalog/101"

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(
            stderr.endswith(expected_stderr),
            (
                "stderr = `{}`\n".format(stderr)
                + "stderr does not end with `{}`".format(expected_stderr)
            ),
        )

    @patch("requests.post", side_effect=mocked_requests_refresh)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_catalog_refresh_cli_success(self, mock_get, mock_post):

        try:
            hpecp = self.cli.CLI()
            hpecp.catalog.refresh("/api/v1/catalog/99")
        except Exception:
            self.fail("Unexpected exception")

        stdout = self.out.getvalue().strip()

        # successful refresh should not output anything
        expected_stdout = ""

        self.assertEqual(stdout, "")


class TestCLIList(BaseTestCase):
    def mocked_requests_get(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog":
            return MockResponse(
                json_data=catalog_list_json, status_code=200, headers=dict(),
            )
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_list_with_columns_and_table_output(self, mock_post, mock_get):

        self.maxDiff = None

        hpecp = self.cli.CLI()
        hpecp.catalog.list(columns=["label_name", "label_description"])

        output = self.out.getvalue().strip()

        self.assertEqual(
            output,
            "+------------+--------------------------------------------------------------------------------+\n"
            + "| label_name |                               label_description                                |\n"
            + "+------------+--------------------------------------------------------------------------------+\n"
            + "|  Spark240  | Spark240 multirole with Jupyter Notebook, Jupyterhub with SSL and gateway node |\n"
            + "+------------+--------------------------------------------------------------------------------+",
        )

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_list_with_columns_and_text_output(self, mock_post, mock_get):

        self.maxDiff = None

        with patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"}):
            hpecp = self.cli.CLI()
            hpecp.catalog.list(
                columns=["label_name", "distro_id"], output="text"
            )

        output = self.out.getvalue().strip()
        self.assertEqual(output, "Spark240  bluedata/spark240juphub7xssl")

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_list_with_query_and_json_ouput(self, mock_post, mock_get):

        self.maxDiff = None

        hpecp = self.cli.CLI()
        hpecp.catalog.list(
            query="[?state!='installed' && state!='installing'] | [*].[_links.self.href] | []",
            output="json",
        )

        output = self.out.getvalue().strip()

        try:
            json.loads(output)
        except Exception:
            self.fail("Output should be valid json")

        self.assertEqual(output, '["/api/v1/catalog/29"]')

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_list_with_query_and_text_output(self, mock_post, mock_get):

        self.maxDiff = None

        with patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"}):
            hpecp = self.cli.CLI()
            hpecp.catalog.list(
                query="[?state!='installed' && state!='installing'] | [*].[_links.self.href] | []",
                output="text",
            )

        output = self.out.getvalue().strip()

        self.assertEqual(output, "/api/v1/catalog/29")


class TestCLIGet(BaseTestCase):
    def mocked_requests_get(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog/100":
            return MockResponse(
                json_data={
                    "_links": {
                        "self": {"href": "/api/v1/catalog/100"},
                        "feed": [
                            {
                                "href": (
                                    "https://s3.amazonaws.com/bluedata-catalog/"
                                    "bundles/catalog/external/docker/EPIC-5.0/"
                                    "feeds/feed.json"
                                ),
                                "name": (
                                    "BlueData EPIC-5.0 catalog feed for docker"
                                ),
                            }
                        ],
                    },
                    "id": "/api/v1/catalog/100",
                    "distro_id": "bluedata/spark240juphub7xssl",
                    "label": {
                        "name": "Spark240",
                        "description": ("The description"),
                    },
                    "version": "2.8",
                    "timestamp": 0,
                    "isdebug": False,
                    "osclass": ["centos"],
                    "logo": {
                        "checksum": "1471eb59356066ed4a06130566764ea6",
                        "url": (
                            "http://10.1.0.53/catalog/logos/"
                            "bluedata-spark240juphub7xssl-2.8"
                        ),
                    },
                    "documentation": {
                        "checksum": "52f53f1b2845463b9e370d17fb80bea6",
                        "mimetype": "text/markdown",
                        "file": (
                            "/opt/bluedata/catalog/documentation/"
                            "bluedata-spark240juphub7xssl-2.8"
                        ),
                    },
                    "state": "initialized",
                    "state_info": "",
                },
                status_code=200,
                headers=dict(),
            )
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog/101":
            raise APIItemNotFoundException(
                message="catalog not found with id: " + "/api/v1/catalog/101",
                request_method="get",
                request_url=args[0],
            )
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_get_output_is_valid_yaml(self, mock_post, mock_get):

        self.maxDiff = None

        hpecp = self.cli.CLI()
        hpecp.catalog.get("/api/v1/catalog/100")

        output = self.out.getvalue().strip()
        try:
            yaml.load(output, Loader=yaml.FullLoader)
        except Exception:
            self.fail("Output should be valid yaml")

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_get_yaml_output_is_valid(self, mock_post, mock_get):

        self.maxDiff = None

        hpecp = self.cli.CLI()
        hpecp.catalog.get("/api/v1/catalog/100")

        output = self.out.getvalue().strip()
        try:
            yaml.load(output, Loader=yaml.FullLoader)
        except Exception:
            self.fail("Output should be valid yaml")

        expected_yaml = dedent(
            """\
_links:
    feed:
         - href: https://s3.amazonaws.com/bluedata-catalog/bundles/catalog/external/docker/EPIC-5.0/feeds/feed.json
           name: BlueData EPIC-5.0 catalog feed for docker
    self:
        href: /api/v1/catalog/100
distro_id: bluedata/spark240juphub7xssl
documentation:
    checksum: 52f53f1b2845463b9e370d17fb80bea6
    file: /opt/bluedata/catalog/documentation/bluedata-spark240juphub7xssl-2.8
    mimetype: text/markdown
id: /api/v1/catalog/100
isdebug: false
label:
    description: The description
    name: Spark240
logo:
    checksum: 1471eb59356066ed4a06130566764ea6
    url: http://10.1.0.53/catalog/logos/bluedata-spark240juphub7xssl-2.8
osclass:
     - centos
state: initialized
state_info: ''
timestamp: 0
version: '2.8'"""
        )

        # remove spaces to make testing easier
        self.assertEqual(
            yaml.dump(yaml.load(output, Loader=yaml.FullLoader)),
            yaml.dump(yaml.load(expected_yaml, Loader=yaml.FullLoader)),
        )

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_get_json_output(self, mock_post, mock_get):

        self.maxDiff = None

        hpecp = self.cli.CLI()
        hpecp.catalog.get("/api/v1/catalog/100", output="json")

        output = self.out.getvalue().strip()

        # remove spaces to make testing easier
        self.assertEqual(
            json.loads(output),
            {
                "timestamp": 0,
                "logo": {
                    "url": "http://10.1.0.53/catalog/logos/bluedata-spark240juphub7xssl-2.8",
                    "checksum": "1471eb59356066ed4a06130566764ea6",
                },
                "osclass": ["centos"],
                "id": "/api/v1/catalog/100",
                "state_info": "",
                "isdebug": False,
                "documentation": {
                    "mimetype": "text/markdown",
                    "checksum": "52f53f1b2845463b9e370d17fb80bea6",
                    "file": "/opt/bluedata/catalog/documentation/bluedata-spark240juphub7xssl-2.8",
                },
                "distro_id": "bluedata/spark240juphub7xssl",
                "label": {
                    "name": "Spark240",
                    "description": "The description",
                },
                "state": "initialized",
                "version": "2.8",
                "_links": {
                    "feed": [
                        {
                            "href": "https://s3.amazonaws.com/bluedata-catalog/bundles/catalog/external/docker/EPIC-5.0/feeds/feed.json",
                            "name": "BlueData EPIC-5.0 catalog feed for docker",
                        }
                    ],
                    "self": {"href": "/api/v1/catalog/100"},
                },
            },
        )

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_get)
    def test_get_output_with_invalid_catalog_id(self, mock_post, mock_get):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.get("/api/v1/catalog/101")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = "catalog not found with id: /api/v1/catalog/101"

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(
            stderr.endswith(expected_stderr),
            "expected: `{}` actual: `{}`".format(expected_stderr, stderr),
        )

    def mocked_requests_garbage_data(*args, **kwargs):
        if args[0] == "https://127.0.0.1:8080/api/v1/catalog/100":
            return MockResponse(
                json_data={"garbage"}, status_code=200, headers=dict(),
            )
        raise RuntimeError("Unhandle GET request: " + args[0])

    @patch("requests.post", side_effect=mocked_requests_post)
    @patch("requests.get", side_effect=mocked_requests_garbage_data)
    def test_get_output_with_unknown_exception(self, mock_post, mock_get):

        with self.assertRaises(SystemExit) as cm:
            hpecp = self.cli.CLI()
            hpecp.catalog.get("/api/v1/catalog/101")

        self.assertEqual(cm.exception.code, 1)

        stdout = self.out.getvalue().strip()
        stderr = self.err.getvalue().strip()

        expected_stdout = ""  # we don't want error output going to stdout
        expected_stderr = (
            "Unknown error. To debug run with env var LOG_LEVEL=DEBUG"
        )

        self.assertEqual(stdout, expected_stdout)

        # coverage seems to populate standard error (issues 93)
        self.assertTrue(stderr.endswith(expected_stderr))


class TestCLIDelete(BaseTestCase):
    @patch("requests.post", side_effect=mocked_requests_post)
    def test_delete(self, mock_post):

        with self.assertRaisesRegexp(
            AttributeError, "'CatalogProxy' object has no attribute 'delete'",
        ):
            hpecp = self.cli.CLI()
            hpecp.catalog.delete("/any/id")