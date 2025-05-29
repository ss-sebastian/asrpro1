from setuptools import setup, find_packages

setup(
    name="asrpro",
    version="0.2.1",  # 更新版本号
    packages=find_packages(),
    install_requires=[
        "pydub>=0.25.1",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        "console_scripts": [
            "asrpro = asrpro.__main__:main"
        ]
    },
    author="Chuqiao 'Sebastian' Song",
    author_email="songchuqiao23@gmail.com",
    description="ASR Audio Preprocessor - Optimize audio files for child speech recognition",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ss-sebastian/asrpro",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    include_package_data=True,
)