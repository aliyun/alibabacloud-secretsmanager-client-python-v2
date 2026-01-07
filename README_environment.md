# System Environment Variables Setting For Alibaba Secrets Manager Client V2

Use Alibaba Secrets Manager client v2 by system environment variables with the below ways:

* Use access key to access aliyun kms, you must set the following system environment variables (for linux):

	- export credentials\_type=ak
	- export credentials\_access\_key\_id=\<your access key id>
	- export credentials\_access\_secret=\<your access key secret>
	- export cache\_client\_region\_id=[{"regionId":"\<your region id>"}]
```
tips:
 	When accessing KMS instance gateway, use the following configuration
	export cache_client_region_id=[{"regionId":"<your region id>","endpoint":"<your kms instanceId>.cryptoservice.kms.aliyuncs.com"}]
```

* Use ECS RAM role to access aliyun kms, you must set the following system environment variables (for linux):

	- export credentials\_type=ecs\_ram\_role
	- export credentials\_role\_name=\<role name>
	- export cache\_client\_region\_id=[{"regionId":"\<your region id>"}]
```
tips:
 	When accessing KMS instance gateway, use the following configuration
	export cache_client_region_id=[{"regionId":"<your region id>","endpoint":"<your kms instanceId>.cryptoservice.kms.aliyuncs.com"}]
```

* Use OIDC Role ARN to access aliyun kms, you must set the following system environment variables (for linux):

	- export credentials\_type=oidc\_role\_arn
	- export credentials\_role\_arn=\<role arn> (optional, if not set, the default Aliyun configuration reading rules will be used)
	- export credentials\_oidc\_provider\_arn=\<oidc provider arn> (optional, if not set, the default Aliyun configuration reading rules will be used)
	- export credentials\_oidc\_token\_file\_path=\<oidc token file path> (optional, if not set, the default Aliyun configuration reading rules will be used)
	- export cache\_client\_region\_id=[{"regionId":"\<your region id>"}]
```
tips:
 	When accessing KMS instance gateway, use the following configuration
	export cache_client_region_id=[{"regionId":"<your region id>","endpoint":"<your kms instanceId>.cryptoservice.kms.aliyuncs.com"}]
```