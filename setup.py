import setuptools

setuptools.setup(name="netfuses",
                 version="1.0",
                 author="baglab",
                 description="fuse similar yet distinct nodes in a network",
                 packages=setuptools.find_packages(),
                 install_requires=["networkx==1.11"]
                 )
