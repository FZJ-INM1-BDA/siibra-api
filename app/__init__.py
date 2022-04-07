# Copyright 2018-2020 Institute of Neuroscience and Medicine (INM-1),
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

import logging
from logging.handlers import TimedRotatingFileHandler
import os
from siibra import logger as siibra_logger

logger = logging.getLogger(__name__)
access_logger = logging.getLogger(__name__ + ".access_log")

ch = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s:%(levelname)s]  %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel('INFO')


if os.environ.get("SIIBRA_API_ACCESS_LOG_FILE"):
    access_log_handler = TimedRotatingFileHandler(os.environ.get("SIIBRA_API_ACCESS_LOG_FILE"), when="d", encoding="utf-8")
else:
    access_log_handler = logging.StreamHandler()

access_format = logging.Formatter('%(asctime)s - %(resp_status)s - %(process_time_ms)sms - %(hit_cache)s - %(message)s')
access_log_handler.setFormatter(access_format)
access_log_handler.setLevel(logging.INFO)
access_logger.addHandler(access_log_handler)


if os.environ.get("SIIBRA_API_GENERAL_LOG_FILE"):
    warn_fh = TimedRotatingFileHandler(os.environ.get("SIIBRA_API_GENERAL_LOG_FILE"), when="d", encoding="utf-8")
    warn_fh.setLevel(logging.INFO)
    warn_fh.setFormatter(formatter)
    logger.addHandler(warn_fh)
    siibra_logger.addHandler(warn_fh)

__version__='0.2.0'
