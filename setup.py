from setuptools import find_packages, setup


with open('requirements.txt') as fd:
    install_requirements = [i.strip() for i in fd.readlines()]

with open('requirements-dev.txt') as fd:
    tests_requirements = [i.strip() for i in fd.readlines()]

with open('README.md') as fd:
    long_description = fd.read()

def get_requirements():
    requirements = list()
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
    return requirements

setup(
    name='motex',
    #version=motex.__version__,
    description='A minimal binary analysis framework',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/finixbit/motex',
    packages=find_packages(),
    license='MIT License',
    tests_require=tests_requirements,
    setup_requires=get_requirements(),
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': ['motex.tools=motex.tools.motex_tools:main']
    },
)
