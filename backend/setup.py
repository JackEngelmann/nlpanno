from setuptools import find_packages, setup


setup(
    name="nlpanno",
    version='0.0.1',
    install_requires=[],
    package_dir={"": "nlpanno"},
    packages=find_packages(where="nlpanno"),
    extras_require={
        "tests": ["pytest"]
    }
)
