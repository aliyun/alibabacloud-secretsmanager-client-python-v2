Alibaba Cloud Secrets Manager Client V2 implementation for Python
=================================================================

The Alibaba Cloud Secrets Manager Client V2 implementation for Python
developers to easily work with Alibaba Cloud KMS Secrets.

Read this in other languages: `简体中文 <README.zh-cn.rst>`__

-  `Alibaba Cloud Secrets Manager Client
   Homepage <https://help.aliyun.com/document_detail/190269.html?spm=a2c4g.11186623.6.621.201623668WpoMj>`__
-  `Issues <https://github.com/aliyun/alibabacloud-secretsmanager-client-python-v2/issues>`__
-  `Release <https://github.com/aliyun/alibabacloud-secretsmanager-client-python-v2/releases>`__

License
=======

`Apache License
2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`__

Features
========

-  Provide quick integration capability to gain secret information
-  Provide Alibaba secrets cache ( memory cache or encryption file cache
   )
-  Provide tolerated disaster by the secrets with the same secret name
   and secret data in different regions
-  Provide default backoff strategy and user-defined backoff strategy

Requirements
============

Python 3.7+

Install
=======

Install the official release version through PIP (taking Linux as an
example):

.. code:: bash

   $ pip install alibabacloud_secretsmanager_client_v2

You can also install the unzipped installer package directly:

.. code:: bash

   $ sudo python setup.py install

Sample Code
===========

Ordinary User Sample Code
-------------------------

-  Build Secrets Manager Client by system environment variables or
   configuration file (secretsmanager.properties) (`system environment
   variables setting for details <README_environment.md>`__,\ `configure
   configuration details <README_config.md>`__)

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_client()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  Build Secrets Manager Client by a custom configuration file (you can
   customize the file name or file path name) (`configure configuration
   details <README_config.md>`__)

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
               DefaultSecretManagerClientBuilder.standard().with_custom_config_file("#customConfigFileName#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  Build Secrets Manager Client by the given parameters(accessKey,
   accessSecret, regionId, etc)

.. code:: python

   import os

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder
   from alibabacloud_secretsmanager_client_v2.utils.credentials_provider_utils import CredentialsProviderUtils

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
               DefaultSecretManagerClientBuilder.standard().with_credentials_provider(CredentialsProviderUtils
                       .with_access_key(os.getenv("#accessKeyId#"), os.getenv("#accessKeySecret#"))).with_region("#regionId#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  Build Secrets Manager Client by Aliyun default credential chain. For
   more information, please refer to `Aliyun default credential
   chain <https://help.aliyun.com/zh/sdk/developer-reference/v2-manage-access-credentials#3cb4c2e29d9hk>`__.

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
               DefaultSecretManagerClientBuilder.standard().with_credentials_provider().with_region("#regionId#").build()).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

-  Build Secrets Manager Client by the given
   parameters(roleArn、oidcProviderArn、oidcTokenFilePath, etc)

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder
   from aliyun_credentials.provider import OIDCRoleArnCredentialProvider

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
                       DefaultSecretManagerClientBuilder.standard()
                               .with_credentials_provider(
                                       OIDCRoleArnCredentialProvider.builder()
                                               .role_arn("#roleArn#")
                                               .oidc_provider_arn("#oidcProviderArn#")
                                               .oidc_token_file_path("#oidcTokenFilePath#")
                                               .build())
                               .with_region("#regionId#")
                               .build())
               .build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

Customized User Code
--------------------

-  Use custom parameters or user's own implementation

.. code:: python

   import os

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.cache.file_cache_secret_store_strategy import FileCacheSecretStoreStrategy
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_refresh_secret_strategy import DefaultRefreshSecretStrategy
   from alibabacloud_secretsmanager_client_v2.service.full_jitter_back_off_strategy import FullJitterBackoffStrategy
   from alibabacloud_secretsmanager_client_v2.utils.credentials_provider_utils import CredentialsProviderUtils

   if __name__ == '__main__':
       secret_cache_client = SecretManagerCacheClientBuilder \
       .new_cache_client_builder(DefaultSecretManagerClientBuilder.standard()
               .with_credentials_provider(CredentialsProviderUtils.with_access_key(os.getenv("#accessKeyId#"), os.getenv("#accessKeySecret#")))
               .with_region("#regionId#")
               .with_back_off_strategy(FullJitterBackoffStrategy(3, 2000, 10000)).build()) \
        .with_cache_secret_strategy(FileCacheSecretStoreStrategy("#cacheSecretPath#", True, "#salt#")) \
        .with_refresh_secret_strategy(DefaultRefreshSecretStrategy("#ttlName#")) \
        .with_cache_stage("#stage#") \
        .with_secret_ttl("#secretName#", 1 * 60 * 1000) \
        .with_secret_ttl("#secretName1#", 2 * 60 * 1000).build()
       secret_info = secret_cache_client.get_secret_info("#secretName#")
       print(secret_info.__dict__)

FAQ
===

1. How to resolve "cannot find the built-in ca certificate for
   region[$regionId], please provide the caFilePath parameter." error?

**Error Cause:** The built-in CA certificate for this region does not
exist in the SDK.

**Solution:** 1. Please update the SDK to the latest version.

2. If you still encounter this error after updating to the latest
   version, you can download the latest CA certificate (CA certificates
   can be downloaded at `Key Management
   Service <https://yundun.console.aliyun.com/?spm=5176.12818093.ProductAndResource--ali--widget-product-recent.dre3.3be916d0yK6Zzx&p=kms#/keyStore/list/base/>`__
   - Instances - Instance Details page) and pass in the CA certificate
   path parameter. The specific methods are as follows:

**Method 1: Passing CA certificate path via coding**

.. code:: python

   from alibabacloud_secretsmanager_client_v2.secret_manager_cache_client_builder import SecretManagerCacheClientBuilder
   from alibabacloud_secretsmanager_client_v2.service.default_secret_manager_client_builder import DefaultSecretManagerClientBuilder
   from alibabacloud_secretsmanager_client_v2.model.region_info import RegionInfo
   from alibabacloud_secretsmanager_client_v2.utils.credentials_provider_utils import CredentialsProviderUtils

   if __name__ == '__main__':
       try:
           # Create RegionInfo with CA certificate path
           region_info = RegionInfo(
               region_id="#regionId#",
               endpoint="#kmsInstanceEndpoint#",  # Specify KMS instance endpoint
               ca_file_path="#caFilePath#"  # Specify CA certificate file path
           )

           secret_cache_client = SecretManagerCacheClientBuilder.new_cache_client_builder(
                   DefaultSecretManagerClientBuilder.standard()
                           .with_credentials_provider(CredentialsProviderUtils.with_access_key(
                                   os.getenv("#accessKeyId#"),
                                   os.getenv("#accessKeySecret#")))
                           .with_region(region_info)  # Using RegionInfo with CA certificate path
                           .build())
                   .build()
           # ... use client
       except Exception as e:
           print(e)

**Method 2: Passing CA certificate path via configuration file**

Add caFilePath parameter in the secretsmanager.properties configuration
file:

.. code:: properties

   # KMS service region with CA certificate path and endpoint
   cache_client_region_id=[{"regionId":"<regionId>","endpoint":"<kmsInstanceId>.cryptoservice.kms.aliyuncs.com","caFilePath":"<ca certificate file path>"}]

**Method 3: Passing CA certificate path via environment variables**

Refer to `Environment Variable Configuration
Instructions <README_environment.md>`__ and add the CA certificate path
parameter in the environment variable configuration:

.. code:: bash

   # KMS service region with CA certificate path and endpoint
   export cache_client_region_id=[{"regionId":"<regionId>","endpoint":"<kmsInstanceId>.cryptoservice.kms.aliyuncs.com","caFilePath":"<ca certificate file path>"}]
