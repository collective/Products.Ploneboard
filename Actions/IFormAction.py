# ###########################################################################
from Interface import Base

class IFormAction(Base):
    def __call__(self, controller_state, REQUEST):
        """Executes the action.  Returns either a new
        controller_state or something that should be handed off to
        the publication machinery."""
# ###########################################################################