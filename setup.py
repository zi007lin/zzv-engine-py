from setuptools import setup, find_packages

setup(
    name='zzv',
    version='0.1.0',
    description='Zeta-Zen VM Project Module',
    packages=[
        'zzv',
        'zzv.common',
        'zzv.engine',
        'zzv.examples',
        'zzv.health',
        'zzv.models',
        'zzv.msgcore',
        'zzv.msgcore.transporters'
    ],
    include_package_data=True,  # Include non-Python files in the package
    install_requires=[
        'kafka-python',  # Example dependencies; add/remove as needed
        'numpy',
        'pandas',
        'protobuf',
        'requests',
        'pydantic',
        'PyYAML',
        'uvicorn',
        'pytest'
    ],
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': [
            'zzv=zzv.engine.zeta_zen_vm:main',  # Modify based on your entry point
        ],
    },
    package_data={
        '': ['*.json', '*.yaml'],  # Include configuration files
    },
)
