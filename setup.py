from setuptools import setup, find_packages

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

setup(
    name="followThePid",            
    version="0.1.0",               
    packages=find_packages(),       
    install_requires=read_requirements(),
    author="Pietro Lechthaler",
    author_email="pietrolechthaler@gmail.com",
    description="",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/se-fbk/followThePid/",
    python_requires=">=3.10",
)
