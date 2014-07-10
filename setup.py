from setuptools import setup, find_packages

name = 'Products.Ploneboard'
version = '3.6.dev0'

setup(
    name='Products.Ploneboard',
    version=version,
    description="A discussion board for Plone.",
    long_description=open("README.rst").read() + \
    open("CHANGES.rst").read(),
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Zope2",
        "Programming Language :: Python",
    ],
    keywords='Zope CMF Plone board forum',
    author='Jarn, Wichert Akkerman, Martin Aspeli',
    author_email='plone-product-developers@lists.plone.org',
    url='https://github.com/collective/Products.Ploneboard',
    license='GPL',
    namespace_packages=['Products'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.CMFPlone >= 4.1',
        'Products.SimpleAttachment',
        'plone.api',
        'plone.app.controlpanel',
        'plone.app.portlets',
        'plone.portlets',
        'plone.memoize',
        'plone.i18n',
        'Products.CMFPlacefulWorkflow',
        'python-dateutil<2.0dev',
        'AccessControl>=3.0',
    ],
    extras_require=dict(
        test=['plone.app.testing',
              'lxml',
              'Products.PloneTestCase', ],
    ),
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
