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


from alibabacloud_secretsmanager_client_v2.cache.cache_secret_store_strategy import CacheSecretStoreStrategy


class MemoryCacheSecretStoreStrategy(CacheSecretStoreStrategy):
    """
    内存缓存密钥存储策略实现类
    将密钥信息缓存在内存中，提供快速访问
    """

    def __init__(self):
        """
        初始化内存缓存密钥存储策略
        """
        self.__cache_map = {}

    def init(self):
        """
        初始化方法
        """
        pass

    def store_secret(self, cache_secret_info):
        """
        在内存中缓存secret信息
        
        :param cache_secret_info: 要缓存的密钥信息
        """
        self.__cache_map[cache_secret_info.secret_info.secret_name] = cache_secret_info

    def get_cache_secret_info(self, secret_name):
        """
        从内存中获取secret缓存信息
        
        :param secret_name: 密钥名称
        :return: 缓存的密钥信息
        """
        return self.__cache_map.get(secret_name)

    def close(self):
        """
        关闭资源
        """
        pass
