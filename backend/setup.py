from setuptools import setup, find_packages

setup(
    name="mhms-backend-v2",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "flask",
        "psycopg2-binary",
        "python-dotenv",
        "flask-cors"
    ],
) 