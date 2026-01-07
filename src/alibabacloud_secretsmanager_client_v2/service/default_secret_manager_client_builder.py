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


import os
import sys
import time
from abc import ABC

from Tea.exceptions import TeaException
from alibabacloud_credentials import provider
from alibabacloud_kms20160120.client import Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_kms20160120.models import GetSecretValueRequest
from alibabacloud_tea_openapi import models as open_api_models

import alibabacloud_secretsmanager_client_v2.utils.const
from alibabacloud_secretsmanager_client_v2 import utils
from alibabacloud_secretsmanager_client_v2.cache_client_builder import CacheClientBuilder
from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo
from alibabacloud_secretsmanager_client_v2.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy
from alibabacloud_secretsmanager_client_v2.service.secret_manager_client import SecretManagerClient
from alibabacloud_secretsmanager_client_v2.service.user_agent_manager import register_user_agent, \
    get_user_agent
from alibabacloud_secretsmanager_client_v2.utils import const, \
    credentials_properties_utils, variable_const, credentials_provider_utils, err_code_const, private_ca_utils
from alibabacloud_secretsmanager_client_v2.utils.backoff_utils import judge_need_recovery_exception
from alibabacloud_secretsmanager_client_v2.utils.common_logger import get_logger
from alibabacloud_secretsmanager_client_v2.utils.kms_end_point_utils import get_vpc_endpoint, get_endpoint
from alibabacloud_secretsmanager_client_v2.utils.ping_utils import ping_host
from concurrent.futures import wait, ALL_COMPLETED, FIRST_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor

from alibabacloud_secretsmanager_client_v2.utils.private_ca_utils import REGION_ID_AND_CA_MAP


class BaseSecretManagerClientBuilder(CacheClientBuilder, ABC):

    @classmethod
    def standard(cls):
        """构建对象，同时对对象实例进行初始化"""
        return DefaultSecretManagerClientBuilder()


class RegionInfoExtend:

    def __init__(self, region_id, endpoint=None, vpc=False, reachable=None, elapsed=None, ca_file_path=None):
        self.elapsed = elapsed
        self.reachable = reachable
        self.region_id = region_id
        self.vpc = vpc
        self.endpoint = endpoint
        self.ca_file_path = ca_file_path


def sort_region_info_list(region_info_list):
    if len(region_info_list) == 0:
        return region_info_list
    with ThreadPoolExecutor(len(region_info_list)) as thread_pool_executor:
        region_info_extend_list = []
        futures = []
        for region_info in region_info_list:
            futures.append(thread_pool_executor.submit(ping_task, RegionInfoExtend(region_id=region_info.region_id,
                                                                                   endpoint=region_info.endpoint,
                                                                                   vpc=region_info.vpc,
                                                                                   ca_file_path=region_info.ca_file_path)))
        if wait(futures, return_when=ALL_COMPLETED):
            for future in futures:
                region_info_extend_list.append(future.result())
        region_info_extend_list.sort(
            key=lambda rie: (not rie.reachable, rie.elapsed))
        region_info_list = []
        for region_info_extend in region_info_extend_list:
            region_info_list.append(
                RegionInfo(region_info_extend.region_id, region_info_extend.vpc, region_info_extend.endpoint,
                           region_info_extend.ca_file_path))
        return region_info_list


def ping_task(region_info_extend):
    endpoint = region_info_extend.endpoint
    region_id = region_info_extend.region_id
    vpc = region_info_extend.vpc
    ca_file_path = region_info_extend.ca_file_path
    if endpoint is not None and endpoint.strip() != '':
        ping_delay = ping_host(endpoint)
    elif vpc:
        ping_delay = ping_host(get_vpc_endpoint(region_id))
    else:
        ping_delay = ping_host(get_endpoint(region_id))
    return RegionInfoExtend(region_id, endpoint, vpc, ping_delay >= 0,
                            ping_delay if ping_delay >= 0 else sys.float_info.max, ca_file_path)


class DefaultSecretManagerClientBuilder(BaseSecretManagerClientBuilder):

    def __init__(self):
        self.region_info_list = []
        self.credentials_provider = None
        self.back_off_strategy = None
        self.config_dict = {}
        self.custom_config_file = None

    def build(self):
        """构建SecretManagerClient实例"""
        return self.DefaultSecretManagerClient(self.region_info_list, self.credentials_provider, self.back_off_strategy,
                                               self.config_dict, self.custom_config_file, self)

    def with_access_key(self, access_key_id, access_key_secret):
        """指定ak sk信息"""
        self.credentials_provider = provider.StaticAKCredentialsProvider(access_key_id=access_key_id,
                                                                         access_key_secret=access_key_secret)
        return self

    def with_credentials_provider(self, credentials_provider):
        """指定credentials provider"""
        self.credentials_provider = credentials_provider
        return self

    def add_region(self, region_id):
        """添加调用地域Id"""
        self.region_info_list.append(RegionInfo(region_id))
        return self

    def add_region_info(self, region_info):
        """添加调用地域信息"""
        self.region_info_list.append(region_info)
        return self

    def with_region(self, *region_ids):
        """指定调用地域Id列表"""
        for region_id in region_ids:
            self.region_info_list.append(RegionInfo(region_id))
        return self

    def with_back_off_strategy(self, back_off_strategy):
        """指定back off 策略"""
        self.back_off_strategy = back_off_strategy
        return self

    def add_config(self, config):
        """添加配置信息"""
        region_info = RegionInfo(region_id=config.region_id, endpoint=config.endpoint)
        self.config_dict[region_info] = config
        self.add_region_info(region_info)
        return self

    def with_custom_config_file(self, custom_config_file):
        """指定自定义配置文件路径"""
        self.custom_config_file = custom_config_file
        return self

    class DefaultSecretManagerClient(SecretManagerClient):

        def __init__(self, region_info_list, credential, back_off_strategy, config_dict, custom_config_file,
                     builder):
            self.client_dict = {}
            self.credential = credential
            self.back_off_strategy = back_off_strategy
            self.builder = builder
            self.pool = ThreadPoolExecutor(max_workers=5)
            self.region_info_list = region_info_list
            self.config_dict = config_dict
            self.custom_config_file = custom_config_file

        def init(self):
            """初始化方法"""
            self.__init_from_config_file()
            self.__init_from_env()
            if not self.region_info_list:
                raise ValueError("the param[regionInfo] is needed")
            register_user_agent(
                const.USER_AGENT_OF_SECRETS_MANAGER_V2_PYTHON + "/" + const.PROJECT_VERSION, 0)
            if self.back_off_strategy is None:
                self.back_off_strategy = FullJitterBackoffStrategy()
            self.back_off_strategy.init()
            if len(self.region_info_list) > 1:
                self.region_info_list = list(set(self.region_info_list))
            if len(self.region_info_list) > 1:
                self.region_info_list = sort_region_info_list(self.region_info_list)
            for region_info in self.region_info_list:
                self.__get_client(region_info)

        def get_secret_value(self, get_secret_value_req):
            futures = []
            finished = []
            for i in range(len(self.region_info_list)):
                if i == 0:
                    try:
                        return self.__get_secret_value(self.region_info_list[i], get_secret_value_req)
                    except TeaException as e:
                        get_logger().error("action:__get_secret_value", exc_info=True)
                        if not judge_need_recovery_exception(e):
                            raise e
                get_secret_request = GetSecretValueRequest()
                get_secret_request.secret_name = get_secret_value_req.secret_name
                get_secret_request.version_stage = get_secret_value_req.version_stage
                get_secret_request.fetch_extended_config = get_secret_value_req.fetch_extended_config
                future = self.pool.submit(self.__retry_get_secret_value,
                                          get_secret_request, self.region_info_list[i], finished)
                futures.append(future)
            try:
                if wait(futures, const.REQUEST_WAITING_TIME, return_when=FIRST_COMPLETED):
                    for future in futures:
                        if not future.done():
                            future.cancel()
                        else:
                            return future.result()
            except Exception as e:
                get_logger().error("action:__retry_get_secret_value_task", exc_info=True)
                raise e
            finally:
                finished.append(True)
            raise TeaException({"code": err_code_const.SDK_READ_TIMEOUT,
                                "message": "refreshSecretTask fail"})

        def __retry_get_secret_value(self, get_secret_value_req, region_info, finished):
            retry_times = 0
            last_exception = None
            while True:
                if len(finished) > 0 and finished[0]:
                    return None
                wait_time_exponential = self.back_off_strategy.get_wait_time_exponential(retry_times)
                if wait_time_exponential < 0:
                    raise TeaException({
                        "code": "TimesLimitExceeded",
                        "message": "Retry times exceeded the limit",
                        "data": last_exception
                    })
                time.sleep(wait_time_exponential / 1000)
                try:
                    return self.__get_secret_value(region_info, get_secret_value_req)
                except TeaException as e:
                    last_exception = e
                    get_logger().error(
                        "action:__retry_get_secret_value region_info:%s retry_times:%s"
                        % (region_info, retry_times),
                        exc_info=True)
                    if not judge_need_recovery_exception(e):
                        raise e
                retry_times += 1

        def __get_secret_value(self, region_info, get_secret_value_req):
            return self.__get_client(region_info).get_secret_value(get_secret_value_req)

        def __get_client(self, region_info):
            if self.client_dict.get(region_info) is not None:
                return self.client_dict.get(region_info)
            self.client_dict[region_info] = self.__build_kms_client(region_info)
            return self.client_dict.get(region_info)

        def __build_kms_client(self, region_info):
            config = self.config_dict.get(region_info)
            if config is None:
                config = open_api_models.Config()
                if region_info.endpoint is not None and region_info.endpoint.strip() != '':
                    config.endpoint = region_info.endpoint
                    if region_info.endpoint.endswith(
                            alibabacloud_secretsmanager_client_v2.utils.const.INSTANCE_GATEWAY_DOMAIN_SUFFIX):
                        if region_info.ca_file_path is not None and region_info.ca_file_path.strip() != '':
                            config.ca = region_info.ca_file_path
                        else:
                            if region_info.region_id in REGION_ID_AND_CA_MAP:
                                config.ca = REGION_ID_AND_CA_MAP.get(region_info.region_id)
                            else:
                                raise ValueError(
                                    f"cannot find the built-in ca certificate for region[{region_info.region_id}],"
                                    f" please provide the caFilePath parameter.")
                elif region_info.vpc:
                    config.endpoint = get_vpc_endpoint(region_info.region_id)
                else:
                    config.endpoint = get_endpoint(region_info.region_id)
                config.credential = CredentialClient(provider=self.credential)
                config.protocol = utils.const.DEFAULT_PROTOCOL
            if config.ca is None:
                config.user_agent = "%s/%s" % (get_user_agent(), const.PROJECT_VERSION)
            else:
                expiration_date = private_ca_utils.get_ca_expiration_utc_date(config.ca)
                config.user_agent = "%s/%s %s/%s" % (get_user_agent(), const.PROJECT_VERSION,
                                                     region_info.region_id + "_ca_expiration_utc_date", expiration_date)
            return Client(config)

        def __init_from_config_file(self):
            credential_properties = credentials_properties_utils.load_credentials_properties(self.custom_config_file)
            if credential_properties is not None:
                if credential_properties.credentials_provider is not None:
                    self.credential = credential_properties.credentials_provider
                if credential_properties.region_info_list is not None:
                    self.region_info_list.extend(credential_properties.region_info_list)

        def __init_from_env(self):
            env_dict = os.environ
            region_info_list = credentials_provider_utils.init_kms_regions(env_dict,
                                                                            variable_const.SOURCE_TYPE_ENV)
            if region_info_list:
                self.region_info_list.extend(region_info_list)
            credentials_provider = credentials_provider_utils.init_credentials_provider_from_env(env_dict)
            if credentials_provider:
                self.credential = credentials_provider

        def __del__(self):
            self.close()

        def close(self):
            if self.pool is not None:
                self.pool.shutdown()
