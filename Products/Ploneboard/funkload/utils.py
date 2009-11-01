from BeautifulSoup import BeautifulSoup

def getPostUrlFromForum(res, position=0):
    soup = BeautifulSoup(res.body)
    posts = soup.findAll('a', attrs={'class':'state-active'})
    return posts[position].attrMap['href']

def getReplyUrlFromConversation(res, position=0):
    soup = BeautifulSoup(res.body)
    return soup.findAll('input', value='Reply to this')[position].parent.attrs[0][1].split('#')[0]

def getForumUrlsFromBoard(res):
    soup = BeautifulSoup(res.body)
    return [f.attrMap['href'] for f in soup.findAll('a', attrs={'class':'state-memberposting'})]
