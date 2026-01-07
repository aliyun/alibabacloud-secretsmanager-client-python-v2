阿里云凭据管家Python客户端V2
============================

阿里云凭据管家Python客户端V2可以使Python开发者快速使用阿里云凭据。

其他语言版本: `English <README.rst>`__

-  `阿里云凭据管家客户端主页 <https://help.aliyun.com/document_detail/190269.html?spm=a2c4g.11186623.6.621.201623668WpoMj>`__
-  `Issues <https://github.com/aliyun/alibabacloud-secretsmanager-client-python-v2/issues>`__
-  `Release <https://github.com/aliyun/alibabacloud-secretsmanager-client-python-v2/releases>`__

许可证
------

`Apache License
2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`__

优势
----

-  支持用户快速集成获取凭据信息
-  支持阿里云凭据管家内存和文件两种缓存凭据机制
-  支持凭据名称相同场景下的跨地域容灾
-  支持默认规避策略和用户自定义规避策略

软件要求
--------

Python 3.7+

安装
----

通过pip安装官方发布的版本（以Linux系统为例）：

.. code:: bash

   pip install aliyun-secret-manager-client-v2

也可以直接安装解压后的安装包：

.. code:: bash

   sudo python setup.py install

示例代码
--------

一般用户代码
~~~~~~~~~~~~

-  通过系统环境变量或配置文件(secretsmanager.properties)构建客户端(`系统环境变量设置详情 <README_environment.zh-cn.md>`__\ 、\ `配置文件设置详情 <README_config.zh-cn.md>`__)

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_client()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  通过自定义配置文件(可自定义文件名称或文件路径名称)构建客户端(`配置文件设置详情 <README_config.zh-cn.md>`__)

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
           DefaultSecretManagerClientBuilder.standard().with_custom_config_file("#customConfigFileName#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  通过指定参数(accessKey、accessSecret、regionId等)构建客户端

.. code:: python

   import os

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
       DefaultSecretManagerClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
           DefaultSecretManagerClientBuilder.standard().with_access_key(
               os.getenv("#accessKeyId#"), os.getenv("#accessKeySecret#")).with_region(
               "#regionId#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  通过指定阿里云默认凭据链参数构建客户端。更多信息请参考
   `阿里云默认凭据链 <https://help.aliyun.com/zh/sdk/developer-reference/v2-manage-access-credentials#3cb4c2e29d9hk>`__\ 。

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
           DefaultSecretManagerClientBuilder.standard().with_region("#regionId#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  通过指定参数(roleArn、oidcProviderArn、oidcTokenFilePath等)构建客户端

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
       DefaultSecretManagerClientBuilder
   from alibabacloud_credentials import provider

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
           DefaultSecretManagerClientBuilder.standard()
           .with_credentials_provider(
               provider.OIDCRoleArnCredentialsProvider(role_arn="#roleArn#",
                                                       oidc_provider_arn="#oidcProviderArn#",
                                                       oidc_token_file_path="#oidcTokenFilePath#"))
           .with_region("#regionId#")
           .build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

定制化用户代码
~~~~~~~~~~~~~~

-  使用自定义参数或用户自己实现

.. code:: python

   import os

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.cache.file_cache_secret_store_strategy import FileCacheSecretStoreStrategy
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
       DefaultSecretManagerClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_refresh_secret_strategy import DefaultRefreshSecretStrategy
   from alibabacloud_secretsmanager_client_v2.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder \
           .new_cache_client_builder(DefaultSecretManagerClientBuilder.standard()
                                     .with_access_key(os.getenv("#accessKeyId#"), os.getenv("#accessKeySecret#"))
                                     .with_region("#regionId#")
                                     .with_back_off_strategy(FullJitterBackoffStrategy(3, 2000, 10000)).build()) \
           .with_cache_secret_strategy(FileCacheSecretStoreStrategy("#cacheSecretPath#", True, "#salt#")) \
           .with_refresh_secret_strategy(DefaultRefreshSecretStrategy("#ttlName#")) \
           .with_cache_stage("#stage#") \
           .with_secret_ttl("#secretName#", 1 * 60 * 1000) \
           .with_secret_ttl("#secretName1#", 2 * 60 * 1000).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

常见问题 FAQ
------------

1. 出现 “cannot find the built-in ca certificate for region[$regionId],
   please provide the caFilePath parameter.” 错误怎么办？

**问题原因：** SDK 中该地域内置的 CA 证书不存在。

**解决方案：** 1. 请更新 SDK 到最新版本。

2. 如果已更新到最新版本仍然报此错误，可以下载最新的CA证书（CA证书可在\ `密钥管理服务 <https://yundun.console.aliyun.com/?spm=5176.12818093.ProductAndResource--ali--widget-product-recent.dre3.3be916d0yK6Zzx&p=kms#/keyStore/list/base/>`__
   - 实例管理 - 实例详情
   页面下载），并传入CA证书路径参数。具体方式如下：

**方式一：编码方式传递 CA 证书路径**

.. code:: python

   import os

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import \
       DefaultSecretManagerClientBuilder
   from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo

   if __name__ == '__main__':
       # 创建包含 CA 证书路径的 RegionInfo
       region_info = RegionInfo(
           region_id="#regionId#",
           endpoint="#kmsInstanceEndpoint#",  # 指定 KMS 实例地址
           ca_file_path="#caFilePath#"  # 指定 CA 证书文件路径
       )
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
           DefaultSecretManagerClientBuilder.standard()
           .with_access_key(
               os.getenv("#accessKeyId#"),
               os.getenv("#accessKeySecret#"))
           .add_region_info(region_info)  # 使用带 CA 证书路径的 RegionInfo
           .build()).build()
       # ... 使用 client

**方式二：通过配置文件方式传递 CA 证书路径**

在 ``secretsmanager.properties`` 配置文件中添加 ``caFilePath`` 参数：

.. code:: properties

   # 关联的KMS服务地域，包含CA证书路径和实例地址
   cache_client_region_id=[{"regionId":"<regionId>","endpoint":"<kmsInstanceId>.cryptoservice.kms.aliyuncs.com","caFilePath":"<ca证书文件路径>"}]

**方式三：通过环境变量方式传递 CA 证书路径**

参考
`环境变量配置说明 <README_environment.zh-cn.md>`__\ ，在环境变量配置中添加
CA 证书路径参数：

.. code:: bash

   # 关联的KMS服务地域，包含CA证书路径和实例地址
   export cache_client_region_id=[{"regionId":"<regionId>","endpoint":"<kmsInstanceId>.cryptoservice.kms.aliyuncs.com","caFilePath":"<ca证书文件路径>"}]
