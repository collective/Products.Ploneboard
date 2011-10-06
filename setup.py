from setuptools import setup, find_packages

from os.path import join

name='Products.Ploneboard'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

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
      url='http://pypi.python.org/pypi/Products.Ploneboard',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'Products.SimpleAttachment',
        'plone.app.controlpanel',
        'plone.app.portlets',
        'plone.portlets',
        'plone.memoize',
        'plone.i18n',
        'python-dateutil<2.0dev',
        'Plone >= 3.3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
