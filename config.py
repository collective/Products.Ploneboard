import utils

######################################################################
# CONFIGURATION
# EMAIL_IDS_VALID = False
# Setting this to true will allow for characters valid in emails to
# appear througout the site as valid ids. Given the limited nature of
# this patch this impacts tradational content as well as
# user_ids. This shouldn't be a problem for most people, but it is
# disabled byt default
EMAIL_IDS_VALID = False
#
if EMAIL_IDS_VALID:
    utils.patch_ids()
######################################################################



