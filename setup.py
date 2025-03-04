from setuptools import setup, find_packages

setup(
    name="t3rm1n4l",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich>=13.5.2",
        "pygame>=2.5.2",
        "mutagen>=1.47.0",
        "tinytag>=1.9.0",
        "google-cloud-storage>=2.10.0",  # For GCS integration
    ],
    entry_points={
        "console_scripts": [
            "t3r=main:main",
        ],
    },
)
