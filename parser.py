import os
from string import strip,split

class ActionParser:
    """With this object you can parse action informations from xml files
    The structure for actions has be the follwing:

        filename:actions
        put the file in your Extension Directory from your Product

        the name has be the name of the installed tool not the name from the module
        eg. portal_actions not ActionTool
        
        <action_provider_name>
          name=Actionname
          id=Actionid
          action=string:yourform
          condition=member
          permission=View
          category=folder
          visible=1
        </action_provider_name>

    Installing actions over xml is the same as installing over python.
    The only diffrent is that you only have to write where and what do
    you want to install.The names in front of = are the same as the parameters in addAction
    so be carefull in writing them.
    """
    
    def __init__(self):
        self.data=[]
        self.lines=[]
        self.lineno=0
        self.start=0
        self.end=0
        
    def parse(self,product_name):
        """parse the actions to a list consisting dictionaries with the action data"""
        os.chdir(os.path.join(INSTANCE_HOME, 'Products',product_name,'Extensions'))
        try:
            self.lines=open('actions').readlines()
        except:
            return None
        for line in self.lines:
            new_line=strip(line)
            if new_line.startswith('<') and not new_line.startswith('</'):
                self.start=self.lineno
            if new_line.startswith('</'):
                self.end=self.lineno
                action={}
                for data in self.lines[self.start+1:self.end]:
                    item=split(strip(data),'=')
                    if len(item)>2:
                        action[item[0]]='='.join(item[1:])
                    else:
                        action[item[0]]=item[1]
                self.data.append({strip(self.lines[self.start])[1:-1]:action})
            self.lineno=self.lineno+1                

    def get_data(self):
        return self.data

class PropertyParser:
    """With this object you can parse property informations from xml files
    The structure for properties has be the follwing:

        filename:actions
        put the file in your Extension Directory from your Product

        the name has be the name of the installed tool not the name from the module
        eg. portal_actions not ActionTool

        <tool_name>
          propertyname=propertyvalue=type
          propertyname=propertyvalue1,propertyvalue2,propertyvalue3=list
          propertyname=1=boolean
        </tool_name>
        
    Installing Properties over xml is the same as Creating them over
    ZMI choose a id choose a value and choose a type. The type name has be the same
    as the type name zmi.
    """

    def __init__(self):
        self.data=[]
        self.lines=[]
        self.lineno=0
        self.start=0
        self.end=0
        
    def parse(self,product_name):
        """parse the properties to a list consisting dictionaries with the property data"""
        os.chdir(os.path.join(INSTANCE_HOME, 'Products',product_name,'Extensions'))
        try:
            self.lines=open('properties').readlines()
        except:
            return None
        
        for line in self.lines:
            new_line=strip(line)
            if new_line.startswith('<') and not new_line.startswith('</'):
                self.start=self.lineno
            if new_line.startswith('</'):
                self.end=self.lineno
                for data in self.lines[self.start+1:self.end]:
                    property={}
                    item=split(strip(data),'=')
                    property['id']=item[0]
                    if item[2]=='lines':
                        property['value']=split(item[1],',')
                    else:
                        if len(item)>3:
                            property['value']='='.join(item[1:len(item)-1])
                        else:    
                            property['value']=item[1]
                    property['type']=item[-1]
                    self.data.append({strip(self.lines[self.start])[1:-1]:property})
            self.lineno=self.lineno+1                

    def get_data(self):
        return self.data
