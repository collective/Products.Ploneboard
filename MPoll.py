"""
$Id: MPoll.py,v 1.2 2003/04/04 11:46:52 magnusheino Exp $
"""
from Products.Archetypes.public import *
from BTrees.IOBTree import IOBTree
from BTrees.Length import Length
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
import types
import operator

schema = ExtensibleMetadata.schema + Schema((
    StringField('id',
                required=1,
                mode="rw",
                accessor="getId",
                mutator="setId",
                default=None,
                widget=IdWidget(label_msgid="label_name",
                                description_msgid="help_name",
                                i18n_domain="plone"),
                ),
    StringField('question',
                required=1,
                searchable=1,
                widget=StringWidget(description="The question for this poll.",
                                    label_msgid="label_question",
                                    description_msgid="help_question",
                                    i18n_domain="mpoll"),
                ),
    LinesField('answers',
               required=1,
               searchable=1,
               widget=LinesWidget(description="A list of alternatives. One alternative per row.",
                                  label_msgid="label_answers",
                                  description_msgid="help_answers",
                                  i18n_domain="mpoll"),
               ),
    BooleanField('open',
                 required=1,
                 accessor='isOpen',
                 default=None,
                 widget=BooleanWidget(description="Check this option to make the poll open, accepting votes from users.",
                                      label_msgid="label_open",
                                      description_msgid="help_open",
                                      i18n_domain="mpoll"),
                 ),
    ))

class MPoll(BaseContent):
    """Simple cookie-based poll."""
    schema = schema

    security = ClassSecurityInfo()

    actions = ({
        'id':'view',
        'name':'View',
        'action':'mpoll_view',
        'permissions':(CMFCorePermissions.View,)
        }, )

    def __init__(self, id, **kwargs):
        BaseContent.__init__(self, id, **kwargs)
        self._votes = IOBTree()

    security.declareProtected(CMFCorePermissions.View, 'vote')
    def vote(self, answer):
        """Register a vote"""

        if not self.isOpen():
            return

        if not isinstance(answer, types.IntType):
            answer = int(answer)

        if not self._votes.has_key(answer):
            self._votes[answer] = Length()

        self._votes[answer].change(1)

    security.declareProtected(CMFCorePermissions.View, 'Title')
    def Title(self):
        """Return question as title, for plone ui"""
        return self.getQuestion()
    
    security.declareProtected(CMFCorePermissions.View, 'getVotes')
    def getVotes(self):
        """Result of this poll"""

        result = {'total': reduce(operator.add, [votes() for votes in self._votes.values()] + [0,0])}

        scores = []

        i = 1
        for answer in self.getAnswers():
            votes = 0
            percent = 0

            if self._votes.has_key(i):
                votes = self._votes[i]()
                percent = int(votes*100.0/result['total'])
            
            scores.append({'answer': answer,
                           'votes': votes,
                           'percent': percent})
            i = i+1
            
        result['scores'] = scores

        return result
                
registerType(MPoll)
