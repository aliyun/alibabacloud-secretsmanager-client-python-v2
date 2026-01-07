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


import base64
import json
import os
from copy import deepcopy

from alibabacloud_secretsmanager_client_v2.cache.cache_secret_store_strategy import CacheSecretStoreStrategy
from alibabacloud_secretsmanager_client_v2.model.secret_info import convert_dict_to_cache_secret_info
from alibabacloud_secretsmanager_client_v2.utils import const
from alibabacloud_secretsmanager_client_v2.utils.aes_utils import AESEncoder, AESDecoder
from alibabacloud_secretsmanager_client_v2.utils.json_utils import load, dump


def filter_none_values(obj):
    if isinstance(obj, dict):
        return {k: filter_none_values(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [filter_none_values(item) for item in obj]
    else:
        return obj


class FileCacheSecretStoreStrategy(CacheSecretStoreStrategy):
    """
    文件缓存密钥存储策略实现类
    将密钥信息缓存到文件中，支持加密存储和读取
    """

    def __init__(self, cache_secret_path, reload_on_start, salt):
        """
        初始化文件缓存密钥存储策略
        
        :param cache_secret_path: 缓存文件路径
        :param reload_on_start: 是否在启动时重新加载
        :param salt: 加密盐值
        """
        self.__cache_secret_path = cache_secret_path
        self.__reload_on_start = reload_on_start
        self.__salt = salt
        self.__cache_map = {}
        self.__reloaded_set = []

    def init(self):
        """
        初始化方法
        检查缓存路径和盐值是否有效
        """
        if self.__cache_secret_path is None:
            self.__cache_secret_path = "."
        if self.__salt is None:
            raise ValueError("the argument[salt] must not be null")

    def store_secret(self, cache_secret_info):
        """
        缓存secret信息到文件
        
        :param cache_secret_info: 要缓存的密钥信息
        """
        file_cache_secret_info = deepcopy(cache_secret_info)
        secret_name = file_cache_secret_info.secret_info.secret_name
        secret_value = file_cache_secret_info.secret_info.secret_value
        file_cache_secret_info.secret_info.secret_value = self.__encrypt_secret_value(secret_value)
        file_name = (const.JSON_FILE_NAME_PREFIX + cache_secret_info.stage + const.JSON_FILE_NAME_SUFFIX).lower()
        cache_secret_path = self.__cache_secret_path + os.sep + secret_name
        cache_dict = json.loads(json.dumps(file_cache_secret_info, default=lambda o: o.__dict__))
        filtered_dict = filter_none_values(cache_dict)
        dump(cache_secret_path, file_name, filtered_dict)
        self.__cache_map[secret_name] = cache_secret_info
        self.__reloaded_set.append(secret_name)

    def get_cache_secret_info(self, secret_name):
        """
        从文件中获取secret缓存信息
        
        :param secret_name: 密钥名称
        :return: 缓存的密钥信息
        """
        if not self.__reload_on_start and (not self.__reloaded_set.__contains__(secret_name)):
            return None
        memory_cache_secret_info = self.__cache_map.get(secret_name)
        if memory_cache_secret_info is not None:
            return memory_cache_secret_info
        file_name = (const.JSON_FILE_NAME_PREFIX + const.STAGE_ACS_CURRENT + const.JSON_FILE_NAME_SUFFIX).lower()
        cache_secret_path = self.__cache_secret_path + os.sep + secret_name + os.sep + file_name
        if not os.path.isfile(cache_secret_path):
            return None
        cache_secret_info_dict = load(cache_secret_path)
        if cache_secret_info_dict is not None:
            if cache_secret_info_dict["secret_info"] is not None:
                cache_secret_info_dict["secret_info"]["secret_value"] = self.__decrypt_secret_value(
                    cache_secret_info_dict["secret_info"]["secret_value"])
            cache_secret_info = convert_dict_to_cache_secret_info(cache_secret_info_dict)
            self.__cache_map[secret_name] = cache_secret_info
            return cache_secret_info

    def __encrypt_secret_value(self, secret_value):
        """
        加密凭据内容
        
        :param secret_value: 明文凭据内容
        :return: 加密后的凭据内容
        """
        key = os.urandom(const.RANDOM_KEY_LENGTH)
        iv = os.urandom(const.IV_LENGTH)
        return base64.b64encode(
            const.CBC_MODE_KEY.encode("utf-8") + key + iv + AESEncoder(key, iv, self.__salt.encode(),
                                                                       secret_value).encode()).decode()

    def __decrypt_secret_value(self, secret_value):
        """
        解密凭据内容
        
        :param secret_value: 加密的凭据内容
        :return: 解密后的明文凭据内容
        """
        secret_value_bytes = base64.b64decode(secret_value.encode())
        key_bytes = secret_value_bytes[
                    len(const.CBC_MODE_KEY.encode()):len(const.CBC_MODE_KEY.encode()) + const.RANDOM_KEY_LENGTH]
        iv_bytes = secret_value_bytes[len(const.CBC_MODE_KEY.encode()) + const.RANDOM_KEY_LENGTH: len(
            const.CBC_MODE_KEY.encode()) + const.RANDOM_KEY_LENGTH + const.IV_LENGTH]
        secret_bytes = secret_value_bytes[len(
            const.CBC_MODE_KEY.encode()) + const.RANDOM_KEY_LENGTH + const.IV_LENGTH: len(secret_value_bytes)]
        return AESDecoder(key_bytes, iv_bytes, self.__salt.encode(), secret_bytes).decode().decode()

    def close(self):
        """
        关闭资源
        """
        pass
