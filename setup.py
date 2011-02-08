from setuptools import setup, find_packages

version = '2.2'

setup(name='Products.Ploneboard',
      version=version,
      description="A discussion board for Plone.",
      long_description=open("README.txt").read() + \
                        open("docs/INSTALL.txt").read() + \
                        open("docs/HISTORY.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Zope CMF Plone board forum',
      author='Jarn, Wichert Akkerman, Martin Aspeli',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/Products.Ploneboard/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      download_url='http://plone.org/products/ploneboard',
      install_requires=[
        'setuptools',
        'Products.SimpleAttachment',
        'plone.app.controlpanel',
        'plone.app.portlets',
        'plone.portlets',
        'plone.memoize',
        'plone.i18n',
        'python-dateutil',
        'Plone >= 3.3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
