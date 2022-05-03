# Copyright 2018-2022 Institute of Neuroscience and Medicine (INM-1),
# Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class SiibraCustomException(Exception):
    """Exception raised for errors in the siibra api service

    Attributes:
        message -- explanation of the error
        status_code -- HTTP error that should be presented to the user
    """
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
