from setuptools import setup, find_packages

setup(
    name="shift_optimizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.71.0",
        "grpcio-tools>=1.71.0",
        "protobuf>=4.25.0",
    ],
    python_requires=">=3.8",
) 