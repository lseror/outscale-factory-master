from setuptools import setup

setup(
    name='outscale_factory_master',
    version='0.1',
    description='Buildmaster support package',
    url='http://github.com/nodalink/outscale-factory-master',
    author='Vincent Crevot',
    author_email=None,
    license='BSD',
    packages=['outscale_factory_master'],
    zip_safe=False,
    install_requires=['boto'],
)
