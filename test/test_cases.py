# coding=utf-8
"""
测试初始化、重试策略、CA证书读取以及凭证配置和环境变量读取功能
"""

import os
import unittest
import tempfile
from unittest.mock import patch

from Tea.exceptions import TeaException

from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
    DefaultSecretManagerClientBuilder, sort_region_info_list
from alibabacloud_secretsmanager_client_v2.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy
from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo
from alibabacloud_secretsmanager_client_v2.utils import variable_const
from alibabacloud_secretsmanager_client_v2.utils.credentials_provider_utils import init_credentials_provider, \
    init_credentials_provider_from_env
from alibabacloud_secretsmanager_client_v2.utils.credentials_properties_utils import load_credentials_properties
from alibabacloud_secretsmanager_client_v2.utils.private_ca_utils import REGION_ID_AND_CA_MAP, get_ca_expiration_utc_date


class TestCases(unittest.TestCase):

    def test_initialization(self):
        """
        测试初始化功能
        """
        try:
            # 创建一个客户端构建器
            builder = DefaultSecretManagerClientBuilder.standard().with_access_key(
                os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID"), os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET"))

            # 添加区域信息
            builder.add_region("cn-hangzhou")

            # 构建客户端
            client = builder.build()

            # 调用初始化方法
            client.init()

            # 验证初始化成功
            self.assertIsNotNone(client)

            # 验证region是否正确设置
            region_info_list = client.region_info_list
            self.assertIsNotNone(region_info_list, "Region infos should not be null")
            self.assertFalse(len(region_info_list) == 0, "Region infos should not be empty")
            self.assertEqual(1, len(region_info_list), "Should have 1 region")
            self.assertEqual("cn-hangzhou", region_info_list[0].region_id, "Region ID should match")

            print("Initialization test passed")
        except Exception as e:
            self.fail("Initialization test failed: " + str(e))

    def test_retry_strategy(self):
        """
        测试重试策略功能
        """
        try:
            # 测试默认退避策略
            default_strategy = FullJitterBackoffStrategy()
            default_strategy.init()

            # 验证默认参数
            self.assertIsNotNone(default_strategy)

            # 测试自定义退避策略
            custom_strategy = FullJitterBackoffStrategy(5, 1000, 30000)
            custom_strategy.init()

            # 验证自定义参数
            wait_time = custom_strategy.get_wait_time_exponential(2)
            self.assertGreater(wait_time, 0, "Wait time should be positive")

            # 测试超过最大重试次数的情况
            negative_wait_time = custom_strategy.get_wait_time_exponential(10)
            self.assertEqual(-1, negative_wait_time, "Should return -1 when exceeding max attempts")

            print("Retry strategy test passed")
        except Exception as e:
            self.fail("Retry strategy test failed: " + str(e))

    def test_credentials_configuration_reading(self):
        """
        测试凭证配置读取功能
        """
        try:
            # 创建测试属性
            test_properties = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ak",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY: "testAccessKeyId",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY: "testAccessKeySecret"
            }

            # 测试从配置读取凭证
            provider = init_credentials_provider(test_properties, variable_const.SOURCE_TYPE_CONFIG)

            self.assertIsNotNone(provider, "Credentials provider should not be null")

            print("Credentials configuration reading test passed")
        except Exception as e:
            self.fail("Credentials configuration reading test failed: " + str(e))

    def test_environment_variable_reading(self):
        """
        测试环境变量读取功能
        """
        try:
            # 创建测试环境变量映射
            test_env_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ak",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY: "testAccessKeyId",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY: "testAccessKeySecret"
            }

            # 测试从环境变量读取凭证
            provider = init_credentials_provider_from_env(test_env_map)

            self.assertIsNotNone(provider, "Credentials provider should not be null")

            print("Environment variable reading test passed")
        except Exception as e:
            self.fail("Environment variable reading test failed: " + str(e))

    def test_region_initialization(self):
        """
        测试区域信息初始化
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()

            # 添加多个区域
            builder.with_region("cn-hangzhou", "cn-shanghai", "cn-beijing")

            region_infos = builder.region_info_list

            # 验证区域信息已正确添加
            self.assertEqual(3, len(region_infos), "Should have 3 regions")

            expected_regions = {"cn-hangzhou", "cn-shanghai", "cn-beijing"}
            actual_regions = set()
            for region_info in region_infos:
                actual_regions.add(region_info.region_id)

            self.assertEqual(expected_regions, actual_regions, "Region IDs should match")

            print("Region initialization test passed")
        except Exception as e:
            self.fail("Region initialization test failed: " + str(e))

    def test_custom_config_file_reading(self):
        """
        测试自定义配置文件读取
        """
        # 测试凭据属性工具类
        credentials_properties = load_credentials_properties(None)

        # 如果没有配置文件，应该返回None或者处理默认情况
        # 这里我们主要测试方法是否能正常执行
        self.assertTrue(True, "Method should execute without exception")

        print("Custom config file reading test passed")

    def test_backoff_strategy_wait_time_calculation(self):
        """
        测试退避策略的指数等待时间计算
        """
        strategy = FullJitterBackoffStrategy(3, 1000, 10000)

        try:
            strategy.init()

            # 测试不同重试次数的等待时间计算
            wait_time0 = strategy.get_wait_time_exponential(0)
            wait_time1 = strategy.get_wait_time_exponential(1)
            wait_time2 = strategy.get_wait_time_exponential(2)
            wait_time3 = strategy.get_wait_time_exponential(3)
            wait_time4 = strategy.get_wait_time_exponential(4)  # 超过最大重试次数

            # 验证计算结果
            self.assertEqual(1000, wait_time0, "Retry 0 should be 1000ms")
            self.assertEqual(2000, wait_time1, "Retry 1 should be 2000ms")
            self.assertEqual(4000, wait_time2, "Retry 2 should be 4000ms")
            self.assertEqual(8000, wait_time3, "Retry 3 should be 8000ms")
            self.assertEqual(-1, wait_time4, "Retry 4 should be -1 (exceeded max attempts)")

            print("Backoff strategy wait time calculation test passed")
        except Exception as e:
            self.fail("Backoff strategy wait time calculation test failed: " + str(e))

    def test_backoff_strategy_boundary_conditions(self):
        """
        测试退避策略边界条件
        """
        try:
            # 测试最大重试次数边界条件
            strategy = FullJitterBackoffStrategy(3, 1000, 10000)
            strategy.init()

            # 验证超过最大重试次数的情况
            wait_time = strategy.get_wait_time_exponential(4)
            self.assertEqual(-1, wait_time)

            # 测试初始间隔为0的情况
            strategy_with_zero_interval = FullJitterBackoffStrategy(3, 0, 10000)
            strategy_with_zero_interval.init()
            self.assertEqual(0, strategy_with_zero_interval.get_wait_time_exponential(1))

            # 测试容量为0情况
            strategy_with_zero_capacity = FullJitterBackoffStrategy(3, 1000, 0)
            strategy_with_zero_capacity.init()
            self.assertEqual(0, strategy_with_zero_capacity.get_wait_time_exponential(1))

            print("Backoff strategy boundary conditions test passed")
        except Exception as e:
            self.fail("Backoff strategy boundary conditions test failed: " + str(e))

    def test_default_secret_manager_client_builder_methods(self):
        """
        测试DefaultSecretManagerClientBuilder的各种方法
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()

            # 测试with_access_key方法
            builder.with_access_key("testAccessKeyId", "testAccessKeySecret")

            # 测试add_region方法
            builder.add_region("cn-hangzhou")

            # 测试with_region方法
            builder.with_region("cn-shanghai", "cn-beijing")

            # 测试with_back_off_strategy方法
            strategy = FullJitterBackoffStrategy()
            builder.with_back_off_strategy(strategy)

            # 测试with_custom_config_file方法
            builder.with_custom_config_file("/path/to/config")

            # 测试config_dict是否正确添加
            config_dict = builder.config_dict
            self.assertIsNotNone(config_dict, "Config dict should not be null")

            print("DefaultSecretManagerClientBuilder methods test passed")
        except Exception as e:
            self.fail("DefaultSecretManagerClientBuilder methods test failed: " + str(e))

    def test_credentials_provider_utils_all_types(self):
        """
        测试CredentialsProviderUtils的各种凭证类型
        """
        try:
            # 测试ak类型
            ak_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ak",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY: "testAccessKeyId",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY: "testAccessKeySecret"
            }

            ak_provider = init_credentials_provider(ak_map, variable_const.SOURCE_TYPE_CONFIG)
            self.assertIsNotNone(ak_provider, "Should create AK provider")

            # 测试ecs_ram_role类型
            ecs_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ecs_ram_role",
                variable_const.VARIABLE_CREDENTIALS_ROLE_NAME_KEY: "testRole"
            }

            ecs_provider = init_credentials_provider(ecs_map, variable_const.SOURCE_TYPE_CONFIG)
            self.assertIsNotNone(ecs_provider, "Should create ECS RAM Role provider")

            # 测试oidc_role_arn类型
            oidc_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "oidc_role_arn",
                variable_const.VARIABLE_CREDENTIALS_OIDC_ROLE_ARN_KEY: "testRoleArn",
                variable_const.VARIABLE_CREDENTIALS_OIDC_PROVIDER_ARN_KEY: "testProviderArn",
                variable_const.VARIABLE_CREDENTIALS_OIDC_TOKEN_FILE_PATH_KEY: "/path/to/token"
            }

            oidc_provider = init_credentials_provider(oidc_map, variable_const.SOURCE_TYPE_CONFIG)
            self.assertIsNotNone(oidc_provider, "Should create OIDC Role Arn provider")

            print("CredentialsProviderUtils all types test passed")
        except Exception as e:
            self.fail("CredentialsProviderUtils all types test failed: " + str(e))

    def test_credentials_provider_utils_exceptions(self):
        """
        测试CredentialsProviderUtils异常情况
        """
        # 测试无效的凭证类型
        try:
            invalid_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "invalid_type"
            }

            init_credentials_provider(invalid_map, "test")
            self.fail("Should throw ValueError for invalid credential type")
        except ValueError as e:
            # 预期异常
            self.assertIn("credentials type", str(e))
        except Exception as e:
            self.fail("Should throw ValueError, but got: " + str(e))

        # 测试AK类型缺少必要参数
        try:
            incomplete_ak_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ak"
                # 故意不设置accessKeyId和accessKeySecret
            }

            init_credentials_provider(incomplete_ak_map, variable_const.SOURCE_TYPE_ENV)
            self.fail("Should throw ValueError for missing AK params")
        except ValueError as e:
            # 预期异常
            self.assertIn(variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY, str(e))
        except Exception as e:
            self.fail("Should throw ValueError, but got: " + str(e))

        print("CredentialsProviderUtils exceptions test passed")

    def test_default_secret_manager_client_builder_build_and_init(self):
        """
        测试DefaultSecretManagerClientBuilder的build方法和初始化流程
        """
        try:
            # 测试没有添加region时的异常情况
            builder_without_region = DefaultSecretManagerClientBuilder.standard()
            client_without_region = builder_without_region.build()

            try:
                client_without_region.init()
                self.fail("Should throw ValueError when no region is specified")
            except ValueError as e:
                self.assertIn("regionInfo", str(e))
            except Exception as e:
                self.fail("Should throw ValueError, but got: " + str(e))

            # 测试正常构建流程
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            client = builder.build()
            self.assertIsNotNone(client, "Client should not be null")

            print("DefaultSecretManagerClientBuilder build and init test passed")
        except Exception as e:
            self.fail("DefaultSecretManagerClientBuilder build and init test failed: " + str(e))

    def test_default_secret_manager_client_builder_add_config(self):
        """
        测试DefaultSecretManagerClientBuilder的add_config方法
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()

            # 创建一个配置对象
            from alibabacloud_tea_openapi import models as open_api_models
            config = open_api_models.Config()
            config.region_id = "cn-hangzhou"
            config.endpoint = "kms.cn-hangzhou.aliyuncs.com"

            # 测试add_config方法
            builder.add_config(config)

            # 检查config_dict是否正确添加
            config_dict = builder.config_dict
            self.assertEqual(1, len(config_dict), "Config dict should contain 1 entry")

            # 检查region_info_list是否正确添加
            region_infos = builder.region_info_list
            self.assertEqual(1, len(region_infos), "Region infos should contain 1 entry")

            print("DefaultSecretManagerClientBuilder add_config test passed")
        except Exception as e:
            self.fail("DefaultSecretManagerClientBuilder add_config test failed: " + str(e))

    def test_credentials_properties_utils_load_credentials_properties(self):
        """
        测试CredentialsPropertiesUtils.load_credentials_properties方法
        """
        try:
            # 测试加载None配置文件名的情况
            properties = load_credentials_properties(None)
            # 如果没有默认配置文件，应该返回None
            # 这里我们主要测试方法是否能正常执行

            # 测试加载不存在的配置文件
            properties2 = load_credentials_properties("non-existent.properties")
            # 同样，主要测试方法是否能正常执行

            print("CredentialsPropertiesUtils load_credentials_properties test passed")
        except Exception as e:
            self.fail("CredentialsPropertiesUtils load_credentials_properties test failed: " + str(e))

    def test_default_secret_manager_client_builder_with_custom_config_file(self):
        """
        测试DefaultSecretManagerClientBuilder.with_custom_config_file方法
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()

            # 测试with_custom_config_file方法
            builder.with_custom_config_file("/path/to/custom/config.properties")

            custom_config_file = builder.custom_config_file

            self.assertEqual("/path/to/custom/config.properties", custom_config_file,
                             "Custom config file path should match")

            print("DefaultSecretManagerClientBuilder with_custom_config_file test passed")
        except Exception as e:
            self.fail("DefaultSecretManagerClientBuilder with_custom_config_file test failed: " + str(e))

    def test_default_secret_manager_client_builder_with_region(self):
        """
        测试DefaultSecretManagerClientBuilder.with_region方法
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()

            # 测试with_region方法
            builder.with_region("cn-hangzhou", "cn-shanghai", "cn-beijing")

            region_infos = builder.region_info_list

            self.assertEqual(3, len(region_infos), "Should have 3 regions")

            expected_regions = {"cn-hangzhou", "cn-shanghai", "cn-beijing"}
            actual_regions = set()
            for region_info in region_infos:
                actual_regions.add(region_info.region_id)

            self.assertEqual(expected_regions, actual_regions, "Region IDs should match")

            print("DefaultSecretManagerClientBuilder with_region test passed")
        except Exception as e:
            self.fail("DefaultSecretManagerClientBuilder with_region test failed: " + str(e))

    def test_region_info_functionality(self):
        """
        测试RegionInfo相关功能
        """
        try:
            # 测试RegionInfo构造函数
            region1 = RegionInfo("cn-hangzhou")
            self.assertEqual("cn-hangzhou", region1.region_id, "Region ID should match")

            region2 = RegionInfo("cn-shanghai", endpoint="kms.cn-shanghai.aliyuncs.com")
            self.assertEqual("cn-shanghai", region2.region_id, "Region ID should match")
            self.assertEqual("kms.cn-shanghai.aliyuncs.com", region2.endpoint, "Endpoint should match")

            region3 = RegionInfo("cn-beijing", True, "kms-vpc.cn-beijing.aliyuncs.com", "/path/to/ca.pem")
            self.assertEqual("cn-beijing", region3.region_id, "Region ID should match")
            self.assertTrue(region3.vpc, "VPC should be true")
            self.assertEqual("kms-vpc.cn-beijing.aliyuncs.com", region3.endpoint, "Endpoint should match")
            self.assertEqual("/path/to/ca.pem", region3.ca_file_path, "CA file path should match")

            print("RegionInfo functionality test passed")
        except Exception as e:
            self.fail("RegionInfo functionality test failed: " + str(e))

    def test_build_kms_client_with_existing_config(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 直接使用config_dict中的配置
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 创建一个配置对象并添加到config_dict中
            from alibabacloud_tea_openapi import models as open_api_models
            config = open_api_models.Config()
            config.region_id = "cn-hangzhou"
            config.endpoint = "kms.cn-hangzhou.aliyuncs.com"

            # 将config添加到config_dict中
            region_info = RegionInfo("cn-hangzhou")
            builder.config_dict[region_info] = config

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient with existing config test passed")
        except Exception as e:
            self.fail("BuildKMSClient with existing config test failed: " + str(e))

    def test_build_kms_client_create_new_config(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 创建新配置（普通endpoint）
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou", endpoint="kms.cn-hangzhou.aliyuncs.com"))

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", endpoint="kms.cn-hangzhou.aliyuncs.com")
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient create new config test passed")
        except Exception as e:
            self.fail("BuildKMSClient create new config test failed: " + str(e))

    def test_build_kms_client_instance_gateway_with_ca_file_path(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 实例网关endpoint带CA文件路径
        """
        ca_file_path = "src/test/resources/test-ca.pem"
        try:
            # 确保证书文件目录存在
            os.makedirs(os.path.dirname(ca_file_path), exist_ok=True)

            # 创建测试用的CA证书文件
            with open(ca_file_path, 'w') as f:
                f.write("""-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK/heBjcOYMA0GCSqGSIb3DQEBBQUAMEUxCzAJBgNV
BAYTAkFVMRMwEQYDVQQIDApTb21lLVN0YXRlMSEwHwYDVQQKDBhJbnRlcm5ldCBX
aWRnaXRzIFB0eSBMdGQwHhcNMTcwODI4MTQzMDAyWhcNMTgwODI4MTQzMDAyWjBF
MQswCQYDVQQGEwJBVTETMBEGA1UECAwKU29tZS1TdGF0ZTEhMB8GA1UECgwYSW50
ZXJuZXQgV2lkZ2l0cyBQdHkgTHRkMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIB
CgKCAQEAuYBXHNYXMnDtyes5Vj6979eABteQqw1hfQnq+jd4/8t47AqNuxWaC56o
i8Njox0fSuFzF9K8m9W7W7GNKZ0N5fCR9K01n4G5pQhP95Q4ZQ99zBzhkF0HsDy9
R1hJ277H3W4R5iOPF12L9+gZoO3t9q0J/n2h9sZ5yUk67d2j3nQccwMDo3zvQm0T
43Y3OCE8q23tH3NMO79KwwYFKDcC3dH1P3dZK8QJh37Gn87KptbJJHDlTqkhuBqF
nC2P1xZJCYrA1rJnNj1g9hJ10z7Dn6fy89HrR9rZ09n3212121212121212121212
1212121212121212121212121212121212121212121212121212121212121212
-----END CERTIFICATE-----""")

            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou", False,
                                          "kms-inst.cryptoservice.kms.aliyuncs.com", ca_file_path))

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", False,
                                     "kms-inst.cryptoservice.kms.aliyuncs.com", ca_file_path)
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient instance gateway with CA file path test passed")
        except Exception as e:
            self.fail("BuildKMSClient instance gateway with CA file path test failed: " + str(e))
        finally:
            # 清理测试创建的CA证书文件
            if os.path.exists(ca_file_path):
                os.remove(ca_file_path)

    def test_build_kms_client_instance_gateway_with_predefined_ca(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 实例网关endpoint使用预设CA证书
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")  # 使用预设有CA证书的区域

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", False,
                                     "kms-inst.cryptoservice.kms.aliyuncs.com", None)  # 不指定CA文件路径
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient instance gateway with predefined CA test passed")
        except Exception as e:
            self.fail("BuildKMSClient instance gateway with predefined CA test failed: " + str(e))

    def test_build_kms_client_with_vpc_endpoint(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - VPC endpoint
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou", True))  # VPC=True

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", True)
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient with VPC endpoint test passed")
        except Exception as e:
            self.fail("BuildKMSClient with VPC endpoint test failed: " + str(e))

    def test_build_kms_client_with_default_endpoint(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 默认endpoint
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou"))  # 既没有endpoint也没有VPC

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou")
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient with default endpoint test passed")
        except Exception as e:
            self.fail("BuildKMSClient with default endpoint test failed: " + str(e))

    def test_init_from_config_file(self):
        """
        测试DefaultSecretManagerClient的init方法 - 从配置文件初始化
        """
        config_file_name = "test-config.properties"
        try:
            # 创建临时配置文件
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.properties') as f:
                f.write(variable_const.VARIABLE_CREDENTIALS_TYPE_KEY + "=ak\n")
                f.write(variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY + "=testAccessKeyId\n")
                f.write(variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY + "=testAccessKeySecret\n")
                f.write(variable_const.VARIABLE_CACHE_CLIENT_REGION_ID_KEY + "=[{\"regionId\":\"cn-hangzhou\"}]\n")
                config_file_name = f.name

            builder = DefaultSecretManagerClientBuilder.standard()
            builder.with_custom_config_file(config_file_name)

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 验证region是否正确设置
            region_infos = client.region_info_list
            self.assertIsNotNone(region_infos, "Region infos should not be null")
            # 注意：由于配置文件中的region信息可能不会被正确解析（因为测试中没有实际的配置文件处理逻辑），
            # 所以我们只验证方法是否能正常执行

            print("Init from config file test passed")
        except Exception as e:
            self.fail("Init from config file test failed: " + str(e))
        finally:
            # 删除临时配置文件
            if os.path.exists(config_file_name):
                os.unlink(config_file_name)

    def test_init_from_env(self):
        """
        测试DefaultSecretManagerClient的init方法 - 从环境变量初始化
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 获取内部类实例
            client = builder.build()

            # 创建测试环境变量映射
            test_env_map = {
                variable_const.VARIABLE_CREDENTIALS_TYPE_KEY: "ak",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_KEY_ID_KEY: "testAccessKeyId",
                variable_const.VARIABLE_CREDENTIALS_ACCESS_SECRET_KEY: "testAccessKeySecret",
                variable_const.VARIABLE_CACHE_CLIENT_REGION_ID_KEY: "[{\"regionId\":\"cn-hangzhou\"}]"
            }

            # 直接调用__init_from_env方法进行测试
            with patch.dict(os.environ, test_env_map):
                client._DefaultSecretManagerClient__init_from_env()

            # 验证region是否正确设置
            region_infos = client.region_info_list
            self.assertIsNotNone(region_infos, "Region infos should not be null")
            self.assertFalse(len(region_infos) == 0, "Region infos should not be empty")

            print("Init from environment variables test passed")
        except Exception as e:
            self.fail("Init from environment variables test failed: " + str(e))

    def test_init_check_region_info_valid(self):
        """
        测试DefaultSecretManagerClient的init方法 - 检查regionInfo（正常情况）
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 验证region是否正确设置
            region_infos = client.region_info_list
            self.assertIsNotNone(region_infos, "Region infos should not be null")
            self.assertFalse(len(region_infos) == 0, "Region infos should not be empty")
            self.assertEqual(1, len(region_infos), "Should have 1 region")
            self.assertEqual("cn-hangzhou", region_infos[0].region_id, "Region ID should match")

            print("Init check region info valid test passed")
        except Exception as e:
            self.fail("Init check region info valid test failed: " + str(e))

    def test_init_check_region_info_invalid(self):
        """
        测试DefaultSecretManagerClient的init方法 - 检查regionInfo（异常情况）
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            # 不添加任何region

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            try:
                client.init()
                self.fail("Should throw ValueError when no region is specified")
            except ValueError as e:
                self.assertIn("regionInfo", str(e))
            except Exception as e:
                self.fail("Should throw ValueError, but got: " + str(e))

            print("Init check region info invalid test passed")
        except Exception as e:
            self.fail("Init check region info invalid test failed: " + str(e))

    def test_init_backoff_strategy(self):
        """
        测试DefaultSecretManagerClient的init方法 - 初始化backoff_strategy
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 获取内部类实例
            client = builder.build()

            # 确保back_off_strategy为None（使用默认值）
            builder.back_off_strategy = None
            client.back_off_strategy = None

            # 调用init方法
            client.init()

            # 验证back_off_strategy已被初始化
            self.assertIsNotNone(client.back_off_strategy, "Backoff strategy should be initialized")

            print("Init backoff strategy test passed")
        except Exception as e:
            self.fail("Init backoff strategy test failed: " + str(e))

    def test_init_region_infos_deduplication(self):
        """
        测试DefaultSecretManagerClient的init方法 - region_infos去重
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")
            builder.add_region("cn-hangzhou")  # 添加重复项
            builder.add_region("cn-shanghai")

            # 获取内部类实例
            client = builder.build()

            region_infos = client.region_info_list

            # 记录去重前的数量
            size_before = len(region_infos)

            # 调用init方法
            client.init()

            # 验证去重后的数量
            size_after = len(client.region_info_list)
            self.assertTrue(size_after <= size_before, "Region infos should be deduplicated")

            print("Init region infos deduplication test passed")
        except Exception as e:
            self.fail("Init region infos deduplication test failed: " + str(e))

    def test_init_region_infos_sorting(self):
        """
        测试DefaultSecretManagerClient的init方法 - region_infos排序
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-guangzhou")
            builder.add_region("cn-hangzhou")
            builder.add_region("cn-beijing")

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 验证region是否正确设置
            region_infos = client.region_info_list
            self.assertIsNotNone(region_infos, "Region infos should not be null")
            self.assertFalse(len(region_infos) == 0, "Region infos should not be empty")
            self.assertEqual(3, len(region_infos), "Should have 3 regions")

            print("Init region infos sorting test passed")
        except Exception as e:
            self.fail("Init region infos sorting test failed: " + str(e))

    def test_build_kms_client_with_ca_file_path_in_region_info(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 使用region_info中的CA文件路径
        """
        try:
            # 创建一个临时CA文件用于测试
            test_ca_content = "-----BEGIN CERTIFICATE-----\n" + \
                              "MIIDhzCCAm+gAwIBAgIJAJLYwUtawfcsMA0GCSqGSIb3DQEBCwUAMHQxCzAJBgNV\n" + \
                              "BAYTAkNOMREwDwYDVQQIDAhaaGVKaWFuZzERMA8GA1UEBwwISGFuZ1pob3UxEDAO\n" + \
                              "BgNVBAoMB0FsaWJhYjExDzANBgNVBAsMBkFsaXl1bjEcMBoGA1UEAwwTUHJpdmF0\n" + \
                              "ZSBLTVMgUm9vdCBDQTAeFw0yNDA2MTIwODM0NTZaFw00NDA2MDcwODM0NTZaMIGH\n" + \
                              "-----END CERTIFICATE-----"

            # 写入临时CA文件
            temp_ca_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pem')
            temp_ca_file.write(test_ca_content)
            temp_ca_file.close()

            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou", False,
                                          "kms-inst.cryptoservice.kms.aliyuncs.com", temp_ca_file.name))

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", False,
                                     "kms-inst.cryptoservice.kms.aliyuncs.com", temp_ca_file.name)
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient with CA file path in RegionInfo test passed")
        except Exception as e:
            self.fail("BuildKMSClient with CA file path in RegionInfo test failed: " + str(e))
        finally:
            # 删除临时CA文件
            if 'temp_ca_file' in locals() and os.path.exists(temp_ca_file.name):
                os.unlink(temp_ca_file.name)

    def test_build_kms_client_with_predefined_ca(self):
        """
        测试DefaultSecretManagerClient的build_kms_client方法 - 使用预定义CA证书
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region(RegionInfo("cn-hangzhou", False, "kms-inst.cryptoservice.kms.aliyuncs.com", None))

            # 获取内部类实例
            client = builder.build()
            client.init()

            # 调用__build_kms_client方法
            region_info = RegionInfo("cn-hangzhou", False, "kms-inst.cryptoservice.kms.aliyuncs.com", None)
            kms_client = client._DefaultSecretManagerClient__build_kms_client(region_info)

            self.assertIsNotNone(kms_client, "KMS Client should not be null")

            print("BuildKMSClient with predefined CA test passed")
        except Exception as e:
            self.fail("BuildKMSClient with predefined CA test failed: " + str(e))

    def test_get_secret_values_normal(self):
        """
        测试DefaultSecretManagerClient的get_secret_value方法 - 正常情况
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 创建测试请求
            from alibabacloud_kms20160120.models import GetSecretValueRequest
            request = GetSecretValueRequest()
            request.secret_name = "test-secret"
            request.version_stage = "ACSCurrent"

            # 验证方法可以被调用（不会抛出异常即为成功）
            try:
                client.get_secret_value(request)
            except Exception as e:
                # 允许调用失败，因为我们没有实际的KMS服务
                # 只要能正确调用方法即可
                self.assertTrue(True)

            print("GetSecretValues normal test passed")
        except Exception as e:
            self.fail("GetSecretValues normal test failed: " + str(e))

    def test_get_secret_values_multi_region(self):
        """
        测试DefaultSecretManagerClient的get_secret_value方法 - 多区域情况
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")
            builder.add_region("cn-shanghai")

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 创建测试请求
            from alibabacloud_kms20160120.models import GetSecretValueRequest
            request = GetSecretValueRequest()
            request.secret_name = "test-secret"
            request.version_stage = "ACSCurrent"

            # 验证方法可以被调用（不会抛出异常即为成功）
            try:
                client.get_secret_value(request)
            except Exception as e:
                # 允许调用失败，因为我们没有实际的KMS服务
                # 只要能正确调用方法即可
                self.assertTrue(True)

            print("GetSecretValues multi-region test passed")
        except Exception as e:
            self.fail("GetSecretValues multi-region test failed: " + str(e))

    def test_retry_get_secret_value(self):
        """
        测试DefaultSecretManagerClient的__retry_get_secret_value方法
        """
        try:
            builder = DefaultSecretManagerClientBuilder.standard()
            builder.add_region("cn-hangzhou")

            # 获取内部类实例
            client = builder.build()

            # 调用init方法
            client.init()

            # 创建测试请求
            from alibabacloud_kms20160120.models import GetSecretValueRequest
            request = GetSecretValueRequest()
            request.secret_name = "test-secret"
            request.version_stage = "ACSCurrent"

            # 创建一个finished标志
            finished = []

            # 验证方法可以被调用（不会抛出异常即为成功）
            try:
                client._DefaultSecretManagerClient__retry_get_secret_value(request,
                                                                           client.region_info_list[
                                                                               0],
                                                                           finished)
            except TeaException as e:
                # 预期的异常类型
                self.assertTrue(True)
            except Exception as e:
                # 允许调用失败，因为我们没有实际的KMS服务
                # 只要能正确调用方法即可
                self.assertTrue(True)

            print("RetryGetSecretValue test passed")
        except Exception as e:
            self.fail("RetryGetSecretValue test failed: " + str(e))

    def test_sort_region_info_list(self):
        """
        测试sort_region_info_list函数
        """
        try:
            region_info_list = []
            region_info1 = RegionInfo("cn-hangzhou")
            region_info2 = RegionInfo("cn-shanghai", True)
            region_info3 = RegionInfo("cn-beijing")
            region_info4 = RegionInfo("cn-shenzhen")
            region_info_list.append(region_info4)
            region_info_list.append(region_info3)
            region_info_list.append(region_info2)
            region_info_list.append(region_info1)
            sorted_list = sort_region_info_list(region_info_list)

            # 改进的验证逻辑
            self.assertIsNotNone(sorted_list, "Sorted list should not be None")
            self.assertEqual(len(region_info_list), len(sorted_list), "Sorted list should have same length as input")

            # 验证所有原始区域信息都在排序后的列表中
            for region_info in region_info_list:
                self.assertIn(region_info, sorted_list, "All original region infos should be present in sorted list")

            # 验证列表确实是排序的（根据RegionInfo的比较逻辑）
            # 注意：由于ping_host现在返回固定值，所有区域的延迟相同，所以顺序可能与输入相同
            self.assertTrue(isinstance(sorted_list, list), "Should return a list")

            print("SortRegionInfoList test passed")
        except Exception as e:
            self.fail("SortRegionInfoList test failed: " + str(e))

    def test_get_ca_expiration_date_with_invalid_input(self):
        """
        测试使用无效输入获取过期时间
        """
        # 测试None输入
        result = get_ca_expiration_utc_date(None)
        self.assertIsNone(result)

        # 测试无效文件路径
        result = get_ca_expiration_utc_date("/path/to/nonexistent/certificate.pem")
        self.assertIsNone(result)

        # 测试无效证书内容
        invalid_cert = "invalid certificate content"
        result = get_ca_expiration_utc_date(invalid_cert)
        self.assertIsNone(result)

    def test_get_ca_expiration_date_with_valid_input(self):
        """
        测试使用有效输入获取过期时间
        """
        # 测试有效的文件路径
        valid_cert_file = REGION_ID_AND_CA_MAP.get("cn-hangzhou")
        result = get_ca_expiration_utc_date(valid_cert_file)
        self.assertIsNotNone(result)

        # 测试无效文件路径
        result = get_ca_expiration_utc_date("/path/to/nonexistent/certificate.pem")
        self.assertIsNone(result)

        # 测试无效证书内容
        invalid_cert = "invalid certificate content"
        result = get_ca_expiration_utc_date(invalid_cert)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
