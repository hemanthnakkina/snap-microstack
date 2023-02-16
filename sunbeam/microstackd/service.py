# Copyright (c) 2022 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json
from abc import ABC
from urllib.parse import quote

from requests.exceptions import HTTPError
from requests.sessions import Session
from requests_unixsocket import DEFAULT_SCHEME
from snaphelpers import Snap

LOG = logging.getLogger(__name__)


class RemoteException(Exception):
    """An Exception raised when interacting with the remote microclusterd service"""

    pass


class NodeAlreadyExistsException(RemoteException):
    """Raised when the node already exists"""

    pass


class NodeJoinException(RemoteException):
    """Raised when the node not able to join cluster"""

    pass


class TokenAlreadyGeneratedException(RemoteException):
    """Raised when token is already generated for the node"""

    pass


class ClusterServiceUnavailableException(RemoteException):
    """Raised when cluster service is not yet bootstrapped"""

    pass


class BaseService(ABC):
    """BaseService is the base service class for microstackd services."""

    def __init__(self, session: Session):
        """Creates a new BaseService for the microstackd API

        The service class is used to provide convenient APIs for clients to
        use when interacting with the microstackd api.


        :param session: the session to use when interacting with the microstackd API
        :type: Session
        """
        self.__session = session
        self._socket_path = Snap().paths.common / "state" / "control.socket"

    def _request(self, method, path, **kwargs):
        if path.startswith("/"):
            path = path[1:]
        netloc = quote(str(self._socket_path), safe="")
        url = f"{DEFAULT_SCHEME}{netloc}/{path}"
        LOG.debug('[%s] %s, args=%s', method, url, kwargs)
        response = self.__session.request(method=method, url=url, **kwargs)
        LOG.debug('Response(%s) = %s', response, response.text)

        try:
            response.raise_for_status()
        except HTTPError as e:
            # Do some nice translating to microstackdexceptions
            error = json.loads(response.text).get("error")
            if "remote with name" in error:
                raise NodeAlreadyExistsException(
                    "Already node exists in the microstack cluster"
                )
            elif "Failed to join cluster with the given join token" in error:
                raise NodeJoinException(
                    "Join node to cluster failed with the given token"
                )
            elif "UNIQUE constraint failed: internal_token_records.name" in error:
                raise TokenAlreadyGeneratedException(
                    "Token already generated for the node"
                )
            elif "Daemon not yet initialized" in error:
                raise ClusterServiceUnavailableException(
                    "Microstack Cluster not initialized"
                )
            raise e

        return response.json()

    def _get(self, path, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        return self._request("get", path, **kwargs)

    def _head(self, path, **kwargs):
        kwargs.setdefault("allow_redirects", False)
        return self._request("head", path, **kwargs)

    def _post(self, path, data=None, json=None, **kwargs):
        return self._request("post", path, data=data, json=json, **kwargs)

    def _patch(self, path, data=None, **kwargs):
        return self._request("patch", path, data=data, **kwargs)

    def _put(self, path, data=None, **kwargs):
        return self._request("put", path, data=data, **kwargs)

    def _delete(self, path, **kwargs):
        return self._request("delete", path, **kwargs)

    def _options(self, path, **kwargs):
        kwargs.setdefault("allow_redirects", True)
        return self._request("options", path, **kwargs)
