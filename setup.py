from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name="webtzite",
        version="0.1.0",
        description="A prototypal structure for serving materials data",
        install_requires=[
            "fastapi[all]",
            "mongogrant",
        ],
        packages=find_packages(),
        python_requires='>=3.6',
    )
