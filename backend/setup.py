from setuptools import find_packages, setup


setup(
    name="nlpanno",
    version='0.0.1',
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    extras_require={
        "tests": ["pytest", "requests"]
    }
)
