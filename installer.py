from parser import ActionParser,PropertyParser
from Products.CMFCore.utils import getToolByName
from string import join

class Installer:    

    def install_actions(self,product_name,pobj):
        """Install actions to the specified tool"""
        res=''
        aparser=ActionParser()
        aparser.parse(product_name)
        actions=aparser.get_data()
        if actions:
            for action in actions:
                action_data=[]
                tname=action.keys()[0]
                tool=self.get_tool(pobj,tname)
                if tool:
                    existing_actions=[a.id for a in tool._cloneActions()]
                    for key in action[tname].keys():
                        action_data.append("%s='%s'" %(key,action[tname][key]))
                    if action[tname]['id'] not in existing_actions:
                        eval("tool.addAction(%s)" %join(action_data,','))
                        res += action[tname]['name']+'was successfully created\n\n'
                    else:
                        res += action[tname]['name']+'already exists\n\n'
                else:
                    res += tname + ' does not exist\n\n'
        else:
            res += 'There are no actions to create\n\n'

        return res                

    def uninstall_actions(self,product_name,pobj):
        """Install actions to the specified tool"""
        res=''
        aparser=ActionParser()
        aparser.parse(product_name)
        actions=aparser.get_data()
        if actions:
            for action in actions:
                action_data=[]
                tname=action.keys()[0]
                tool=self.get_tool(pobj,tname)
                if tool:
                    existing_actions=[a.id for a in tool._cloneActions()]
                    if action[tname]['id'] in existing_actions:
                        tool.deleteActions([existing_actions.index(action[tname]['id'])])
                        res += action[tname]['name']+'was successfully removed\n\n'
                    else:
                        res += action[tname]['name']+' does not exists\n\n'
                else:
                    res += tname+' does not longer exist removing of '+action[tname]['name']+' is not possible\n\n'
        else:
            res += 'There are no actions to create\n\n'

        return res                
            
    def install_properties(self,product_name,pobj):
        """Install properties to the specified tool"""
        res=''
        pparser=PropertyParser()
        pparser.parse(product_name)
        properties=pparser.get_data()
        if properties:
            for property in properties:
                tname=property.keys()[0]
                tool=self.get_tool(pobj,tname)
                if tool:
                    if not tool.hasProperty(property[tname]['id']):
                        tool.manage_addProperty(property[tname]['id'],property[tname]['value'],property[tname]['type'])
                        res += property[tname]['id']+'was successfully created\n\n'
                    else:
                        res += property[tname]['id']+'already exists\n\n'
                else:
                    res += tname +' does not exist\n\n'
                    
        else:
            res += 'There are no properties to create\n\n'
            
        return res

    def uninstall_properties(self,product_name,pobj):
        """Install properties to the specified tool"""
        res=''
        pparser=PropertyParser()
        pparser.parse(product_name)
        properties=pparser.get_data()
        if properties:
            for property in properties:
                tname=property.keys()[0]
                tool=self.get_tool(pobj,tname)
                if tool:
                    if tool.hasProperty(property[tname]['id']):
                        tool.manage_delProperties([property[tname]['id']])
                        res += property[tname]['id']+'was successfully removed\n\n'
                    else:
                        res += property[tname]['id']+'does not exist \n\n'
                else:
                    res += tname+' does not longer exist removing of '+action[tname]['name']+' is not possible\n\n'                    
        else:
            res += 'There are no properties to create\n\n'
            
        return res

    def get_tool(self,pobj,tname):
        if tname=='portal_url':
            return getToolByName(pobj,tname).getPortalObject()
        else:
            try:
                return getToolByName(pobj,tname)
            except:
                return None

def install_from_xml(self,product_name):
    """It would be nice if in future only this method is called from quickinstaller
       and all configuration script will be done in xml and the Quickinstaller install
       the tools"""
    res=''
    install=Installer()
    res +=install.install_actions(product_name,self)
    res +=install.install_properties(product_name,self)
    return res

def uninstall_from_xml(self,product_name):
    res=''
    install=Installer()
    res +=install.uninstall_actions(product_name,self)
    res +=install.uninstall_properties(product_name,self)
    return res
