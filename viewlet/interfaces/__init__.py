from Interface import Interface
from Interface.Attribute import Attribute

class IViewlet(Interface):
    """Interface of Viewlets that can be applied to an object.
    """

    def __call__():
        """Returns the template associated with the viewlet.
        """
