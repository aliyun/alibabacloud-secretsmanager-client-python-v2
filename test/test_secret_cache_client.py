# coding=utf-8
import os
import time
import unittest

from alibabacloud_secretsmanager_client_v2.cache.file_cache_secret_store_strategy import FileCacheSecretStoreStrategy
from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo
from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
from alibabacloud_secretsmanager_client_v2.service.default_refresh_secret_strategy import DefaultRefreshSecretStrategy
from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
    DefaultSecretManagerClientBuilder
from alibabacloud_secretsmanager_client_v2.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy


class TestCacheClient(unittest.TestCase):
    ak = os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"]
    sk = os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"]

    def test_cache_client_info_with_env(self):
        secret_name = "cache_client_3"
        secret_cache_client = SecretManagerCacheClientBuilder.new_client()
        secret_info = secret_cache_client.get_secret_info(secret_name)
        print(secret_info)
        time.sleep(1000000)

    def test_cache_client(self):
        secret_name = "cache_client_3"
        secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
            DefaultSecretManagerClientBuilder.standard().with_access_key(TestCacheClient.ak,
                                                                         TestCacheClient.sk)
                .with_back_off_strategy(
                FullJitterBackoffStrategy(3, 2000, 10000))
                .with_region("cn-beijing").add_region(
                "cn-shanghai").add_region_info(RegionInfo("cn-shenzhen"))
                .build()).with_secret_ttl(secret_name, 2 * 60 * 1000) \
            .with_cache_secret_strategy(
            FileCacheSecretStoreStrategy("secrets", True, "1234abcd")).with_refresh_secret_strategy(
            DefaultRefreshSecretStrategy("ttl")).with_parse_json_ttl(
            "refreshInterval").build()
        # .with_secret_ttl(secret_name,2 * 60 * 1000)
        # .with_refresh_secret_strategy(DefaultRefreshSecretStrategy("ttl"))
        secret_value = secret_cache_client.get_secret_value(secret_name)
        print(secret_value)
        time.sleep(1000000)

    def test_cache_client_with_ak(self):
        secret_name = "cache_client"
        secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
            DefaultSecretManagerClientBuilder.standard().with_access_key(TestCacheClient.ak,
                                                                         TestCacheClient.sk).build()) \
            .with_parse_json_ttl("refreshInterval") \
            .build()
        secret_info = secret_cache_client.get_secret_info(secret_name)
        print(secret_info)
        time.sleep(1000000)

    def test_back_off(self):
        secret_name = "cache_client_3"
        secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
            DefaultSecretManagerClientBuilder.standard().with_access_key(TestCacheClient.ak,
                                                                         TestCacheClient.sk)
                .with_back_off_strategy(
                FullJitterBackoffStrategy(3, 2000, 10000))
                .with_region("cn-beijing").add_region(
                "cn-shanghai").add_region_info(RegionInfo("cn-shenzhen"))
                .build()) \
            .build()
        secret_info = secret_cache_client.get_secret_info(secret_name)
        print(secret_info)
        time.sleep(1000000)
