from setuptools import setup, find_packages

setup(
    name="snowflake-security",
    version="0.1",
    packages=find_packages(),
    install_requires=["dotenv","convex","cryptography","pyotp","prompt_toolkit"],
)