# coding=utf-8

"""Alibaba Cloud Secrets Manager Client V2 for Python."""
import os
import re
import sys

from setuptools import find_packages, setup

VERSION_RE = re.compile(r"""__version__\s*=\s*['"]([^'"]*)['"]""")
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*paths):
    """读取完整文件内容"""
    try:
        with open(os.path.join(HERE, *paths), 'r', encoding='utf-8') as fh:
            return fh.read()
    except Exception as e:
        print(f"警告: 无法读取文件 {os.path.join(HERE, *paths)}: {e}")
        return ""


def get_version():
    """读取版本号"""
    try:
        init = read("src", "alibabacloud_secretsmanager_client_v2", "__init__.py")
        version_match = VERSION_RE.search(init)
        if version_match:
            return version_match.group(1)
        else:
            raise RuntimeError("无法找到版本字符串")
    except Exception as e:
        print(f"获取版本时出错: {e}")
        sys.exit(1)


def get_ca_files():
    """获取CA目录下的所有PEM文件"""
    ca_files = []
    ca_dir = os.path.join(HERE, "src", "alibabacloud_secretsmanager_client_v2", "ca")
    try:
        if os.path.exists(ca_dir):
            for filename in os.listdir(ca_dir):
                if filename.endswith(".pem"):
                    ca_files.append(os.path.join("ca", filename))
        else:
            print(f"警告: 在 {ca_dir} 找不到CA目录")
    except Exception as e:
        print(f"警告: 无法访问CA目录 {ca_dir}: {e}")
    return ca_files


setup(
    name="alibabacloud_secretsmanager_client_v2",
    packages=find_packages("src", include=["alibabacloud_secretsmanager_client_v2",
                                           "alibabacloud_secretsmanager_client_v2.*"]),
    package_dir={"": "src"},
    version=get_version(),
    license="Apache License 2.0",
    author="Alibaba Cloud",
    maintainer="Alibaba Cloud",
    description="Alibaba Cloud Secrets Manager Client V2 implementation for Python",
    long_description=read("README.rst"),
    long_description_content_type="text/x-rst",
    keywords=["alibabacloud", "kms", "secretsmanager", "secrets", "v2"],
    url="https://www.alibabacloud.com/",
    install_requires=[
        "alibabacloud_kms20160120>=2.3.1",
        "cryptography>=3.2.1",
        "apscheduler>=3.5.2",
        "bytebuffer>=0.1.0",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    package_data={
        "alibabacloud_secretsmanager_client_v2": get_ca_files()
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Security",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
)
