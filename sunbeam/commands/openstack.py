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

import asyncio
import logging
from pathlib import Path

from sunbmea.commands.juju import JujuHelper

LOG = logging.getLogger(__name__)


class DeployControlPlaneStep(BaseStep):
    """Deploy OpenStack Control Plane."""

    def __init__(self, model: str, bundle_dir: Path):
        super().__init__("Deploy Control Plane", "Deploy Controlplane using juju")

        self.model = model
        self.bundle_dir = bundle_dir

    def is_skip(self, status: Optional["Status"] = None):
        """Determines if the step should be skipped or not.

        :return: True if the Step should be skipped, False otherwise
        """

        return False

    def run(self, status: Optional["Status"] = None) -> Result:
        """Run the step to completion.

        Invoked when the step is run and returns a ResultType to indicate

        :return:
        """
        result = asyncio.get_event_loop().run_until_complete(
            JujuHelper.deploy_bundle(self.model, self.bundle)
        )

        if result:
            return Result(ResultType.COMPLETED)
        else:
            return Result(ResultType.FAILED, "Error in deploygin openstack apps")
