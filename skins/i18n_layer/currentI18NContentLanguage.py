## Script (Python) "currentI18NContentLanguage"
##title=
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
REQUEST=context.REQUEST

try:
    here_url=REQUEST['URL']
    layer_url=context.retrieveI18NContentLayerURL()
    available_languages=context.retrieveFilteredLanguages()
except:
    return None, None

currentCookie=REQUEST.cookies.get('I18N_CONTENT_LANGUAGE', None)
currentServed=REQUEST.get('I18N_CONTENT_SERVED_LANGUAGE', None)
currentOnce=REQUEST.get('cl', None)
fallback=1

print "here_url", here_url
print "layer_url", layer_url
print "available", available_languages
print "currentCookie", currentCookie
print "currentServed", currentServed
print "currentOnce", currentOnce

if here_url[:len(layer_url)] == layer_url:
    try: rest=here_url[len(layer_url):]
    except: rest=None
    print "r1", rest
    if rest and rest not in ('/','/index_html','/view'):
        rest=rest.split('/')
        print "rest", rest
        print "langs", available_languages
        if rest[1] in available_languages.keys():
            if rest[1] != currentServed:
                print "rest is currentServed"
                currentServed=rest[1]
        else:
            print "none was served"
            fallback=0
            currentServed=None
        print "currentServed", currentServed
    elif currentOnce:
        currentServed=currentOnce
    else:
        currentServed=currentCookie

if not currentServed and fallback:
    for ac in context.retrieveAcceptLanguages():
        if ac in available_languages.keys():
            currentServed=ac
            break		

name=available_languages.get(currentServed, None)
lang=currentServed, name

if not name or not currentServed:
    return None, None

if currentServed and currentCookie and currentCookie != currentServed and not currentOnce:
    print "updating cookie"
    REQUEST.RESPONSE.setCookie('I18N_CONTENT_LANGUAGE',currentServed, path='/')

print lang
return lang

