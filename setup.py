from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='iiif-pipeline',
    version='0.1',
    description="Pipeline to create image derivatives and IIIF manifests.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://github.com/RockefellerArchiveCenter/iiif-pipeline',
    author='Rockefeller Archive Center',
    author_email='archive@rockarch.org',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'ArchivesSnake'
        'boto3',
        'iiif-prezi',
        'img2pdf',
        'Pillow',
        'python-magic',
        'shortuuid'
    ],
    tests_require=['pytest', 'vcrpy'],
    zip_safe=False)
