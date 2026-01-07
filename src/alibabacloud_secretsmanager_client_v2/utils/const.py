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
# 文件缓存文件名前缀
JSON_FILE_NAME_PREFIX = "stage_"
# 文件缓存文件名后缀
JSON_FILE_NAME_SUFFIX = ".json"
# 当前stage
STAGE_ACS_CURRENT = "ACSCurrent"
# cbc模块key
CBC_MODE_KEY = '001'
# iv长度
IV_LENGTH = 16
# 数据类型 text
TEXT_DATA_TYPE = "text"
# 数据类型 binary
BINARY_DATA_TYPE = "binary"
# 默认ttl时间 单位:ms
DEFAULT_TTL = 60 * 60 * 1000
# 默认最大重试次数
DEFAULT_RETRY_MAX_ATTEMPTS = 5
# 重试时间间隔，单位ms
DEFAULT_RETRY_INITIAL_INTERVAL_MILLS = 2000
# 最大等待时间，单位ms
DEFAULT_CAPACITY = 10000
# 默认日志名称
DEFAULT_LOGGER_NAME = "SecretsManagerClientV2"
# Secrets Manager Client V2 Python的User Agent
USER_AGENT_OF_SECRETS_MANAGER_V2_PYTHON = "alibabacloud-secretsmanager-client-python-v2"
# 版本号
PROJECT_VERSION = "2.0.0"
# 默认配置文件名称
DEFAULT_CONFIG_NAME = "secretsmanager.properties"
# 请求等待时间(毫秒)
REQUEST_WAITING_TIME = 2 * 60 * 1000
# 默认协议
DEFAULT_PROTOCOL = "https"
# 随机密钥字节长度
RANDOM_KEY_LENGTH = 32
# 实例网关域后缀
INSTANCE_GATEWAY_DOMAIN_SUFFIX = "cryptoservice.kms.aliyuncs.com"
