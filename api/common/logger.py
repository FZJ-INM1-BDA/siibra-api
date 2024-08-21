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

"""Logging module.

if `LOGGER_DIR` is defined in config, will also use `TimedRotatingFileHandler` to write
to `LOGGER_DIR`.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from api.siibra_api_config import LOGGER_DIR

main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__ + ".info")
access_logger = logging.getLogger(__name__ + ".access_log")
ch = logging.StreamHandler()

formatter = logging.Formatter("[%(name)s:%(levelname)s]  %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel("INFO")


log_dir = LOGGER_DIR

if log_dir:
    log_dir += "" if log_dir.endswith("/") else "/"

if log_dir:
    import socket
    filename = log_dir + f"{socket.gethostname()}.access.log"
    access_log_handler = TimedRotatingFileHandler(filename, when="d", encoding="utf-8")
else:
    access_log_handler = logging.StreamHandler()

access_format = logging.Formatter("%(asctime)s - %(resp_status)s - %(process_time_ms)sms - %(hit_cache)s - %(message)s")
access_log_handler.setFormatter(access_format)
access_log_handler.setLevel(logging.INFO)
access_logger.addHandler(access_log_handler)


if log_dir:
    import socket
    filename = log_dir + f"{socket.gethostname()}.general.log"
    warn_fh = TimedRotatingFileHandler(filename, when="d", encoding="utf-8")
    warn_fh.setLevel(logging.INFO)
    warn_fh.setFormatter(formatter)
    logger.addHandler(warn_fh)
