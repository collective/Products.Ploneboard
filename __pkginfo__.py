
modname = 'CMFQuickInstallerTool'
version = open('version.txt').read().strip()
numversion = version.split('.') 

license = 'GPL'
copyright = '''(c) 2003 BlueDynamics'''

author = "Philipp Auersperg"
author_email = "phil@bluedynamics.com"

short_desc = "A tool to manage installation of CMF products inside CMF sites"
long_desc = """This tool is independent from the former CMFQuickInstaller.
The main difference to CMFQuickInstaller the tracking of
what a product creates during install. 
"""

web = "http://www.sourceforge.net/projects/collective"
ftp = ""
mailing_list = "collective@lists.sourceforge.net"
