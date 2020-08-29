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

"""Python library code for working with install API."""

from __future__ import absolute_import


class InstallController:
    """Controller for working with the install API."""

    def __init__(self, client):
        self.client = client

    def get(self):
        """Get Install information.

        Returns
        -------
        [type]
            [description]
        """
        response = self.client._request(
            url="/api/v1/install",
            http_method="get",
            description="install/get",
        )
        return response.json()

    # def set_gateway_ssl(self, ):
    #     """Set Gateway SSL."""
    #     _data = {
    #         "gateway_ssl_cert_info": {
    #             "cert_file": {
    #                 "content": "-----BEGIN CERTIFICATE-----XXXX-----END CERTIFICATE-----\n",
    #                 "file_name": "cert.pem",
    #             },
    #             "key_file": {
    #                 "content": "-----BEGIN RSA PRIVATE KEY-----XXXX-----END RSA PRIVATE KEY-----\n",
    #                 "file_name": "key.pem",
    #             },
    #         }
    #     }

    #     response = self.client._request(
    #         url="/api/v1/install?install_reconfig",
    #         http_method="put",
    #         data=_data,
    #         description="install/set_gateway_ssl",
    #     )
    #     return response.json()
