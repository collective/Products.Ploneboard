### Register Transforms
### This is interesting because we don't expect all transforms to be
### available on all platforms. To do this we allow things to fail at
### two levels
### 1) Imports
###    If the import fails the module is removed from the list and
###    will not be processed/registered
### 2) Registration
###    A second phase happens when the loaded modules register method
###    is called and this produces an instance that will used to
###    implement the transform, if register needs to fail for now it
###    should raise an ImportError as well (dumb, I know)

from Products.PortalTransforms.libtransforms.utils import MissingBinary
modules = [
    'text_to_emoticons',
    'url_to_hyperlink',
    ]

g = globals()
transforms = []
for m in modules:
    try:
        ns = __import__(m, g, g, None)
        transforms.append(ns.register())
    except ImportError, e:
        print "Problem importing module %s : %s" % (m, e)
    except MissingBinary, e:
        print e
    except:
        import traceback
        traceback.print_exc()


def initialize(engine):
    for transform in transforms:
        engine.registerTransform(transform)
