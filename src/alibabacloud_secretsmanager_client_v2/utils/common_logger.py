# coding=utf-8
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
import logging
import threading

from alibabacloud_secretsmanager_client_v2.utils import const


class CommonLogger:
    """
    通用日志记录器类
    提供全局日志记录器的管理功能
    """

    def __init__(self):
        pass

    common_logger = None
    lock = threading.RLock()


def set_logger(logger):
    """
    设置全局日志记录器
    
    :param logger: 日志记录器对象
    """
    with CommonLogger.lock:
        if CommonLogger.common_logger is None:
            CommonLogger.common_logger = logger


def get_logger():
    """
    获取全局日志记录器
    
    :return: 日志记录器对象
    """

    if CommonLogger.common_logger is None:
        set_logger(default_logger())
    return CommonLogger.common_logger


def default_logger():
    """
    获取默认日志记录器

    :return: 日志记录器对象
    """
    logger = logging.getLogger(const.DEFAULT_LOGGER_NAME)
    set_logger(logger)
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            console.setFormatter(formatter)
            logger.addHandler(console)
