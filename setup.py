
from setuptools import setup, find_packages
version = '0.1.1'
dependencies = ['requests==2.18.4']
test_dependencies = ['nose==1.3.7', 'mock==2.0.0']

setup_config = {'name': 'stackstats',
                'version': version,
                'description': 'A StackExchange API simple stats calculator',
                'packages': find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
                'install_requires': dependencies,
                'tests_require': test_dependencies,
                'test_suite': 'nose.collector',
                'include_package_data': True,
                'entry_points': {
                    'console_scripts': ['stats=stackstats.stats_calc:main']
                }
            }

if __name__ == '__main__':
    setup(**setup_config)

