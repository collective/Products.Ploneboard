## Script (Python) "photo_display_sizes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=max_size=None
##title=returns a dictionary of display sizes
##

# aquire display array from skinpath so projects can easily override 
return {'thumbnail': (128,128),
        'xsmall': (200,200),
        'small': (320,320),
        'medium': (480,480),
        'large': (768,768),
        'xlarge': (1024,1024)
        }
