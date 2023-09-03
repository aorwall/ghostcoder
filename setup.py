from setuptools import setup, find_packages

setup(
    name="ghostcoder",
    version="0.0.6",
    packages=find_packages(),
    #entry_points={
    #    'console_scripts': [
    #        'app=ghostcoder.main:run',
    #    ],
    #},
    install_requires=[
        'codeblocks-gpt>=0.1.2',
        'openai>=0.27.6,<0.28.0',
        'langchain>=0.0.251,<0.1.0',
        'pydantic>=1,<2',
        'tiktoken>=0.4.0,<0.5.0',
        'gitpython>=3.1.31,<3.2.0',
        'tree-sitter-languages>=1.7.0'
    ]
)