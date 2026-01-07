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
import socket

from Tea.exceptions import TeaException, UnretryableException
from alibabacloud_tea_openapi.exceptions import ThrottlingException

from alibabacloud_secretsmanager_client_v2.utils import err_code_const


def judge_need_back_off(e):
    """
    判断是否需要回退策略
    
    :param e: 异常对象
    :return: 是否需要回退
    """
    if isinstance(e, TeaException):
        if isinstance(e, ThrottlingException) or (err_code_const.REJECTED_THROTTLING == e.code) or (
                err_code_const.SERVICE_UNAVAILABLE_TEMPORARY == e.code) or (
                err_code_const.INTERNAL_FAILURE == e.code):
            return True
    return False


def judge_need_recovery_exception(e):
    """
    判断是否需要恢复的异常
    
    :param e: 异常对象
    :return: 是否需要恢复
    """
    if isinstance(e, UnretryableException):
        return e.message is not None and e.message != "" and \
            (isinstance(e.__cause__, socket.timeout) or
             (isinstance(e.message, str) and err_code_const.SDK_READ_TIMEOUT in e.message))
    elif isinstance(e, TeaException):
        return (err_code_const.SDK_READ_TIMEOUT == e.code or
                judge_need_back_off(e))
    return False
