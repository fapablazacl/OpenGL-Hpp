
import xml.dom.minidom
import cpp

class Parameter:
    def __init__(self, name, type, class_):
        self.name = name
        self.type = type
        self.class_ = class_

    def has_class(self):
        return self.class_ is not None


class Command:
    def __init__(self, name, return_type, params, namespace, group):
        self.name = name
        self.return_type = return_type
        self.params = params
        self.namespace = namespace
        self.group = group

    def get_class(self):
        if self.params is None or len(self.params) == 0:
            return None
        
        if self.params[0].has_class():
            return self.params[0].class_
            
    def __str__(self):
        return self.name

    
class GLXMLParser:
    def parse(self, tree):
        commands = []

        registry_el = tree.documentElement
        for commands_list in registry_el.getElementsByTagName("commands"):
            ns = commands_list.getAttribute("namespace")

            for command_el in commands_list.getElementsByTagName("command"):
                commands.append(self.create_command(ns, command_el))
                
        return commands
                
    
    def create_command(self, namespace, command_el):
        name = self.extract_command_name(command_el)
        
        params = []
        for param_el in command_el.getElementsByTagName("param"):
            parameter = self.create_parameter(param_el)
            params.append(parameter)
        
        return Command(name=name, return_type=None, params=params, namespace=namespace, group=None)
        

    def create_parameter(self, param_el):
        return Parameter(
            self.extract_param_name(param_el),
            self.extract_param_type(param_el),
            self.extract_param_class(param_el)
        )

    def extract_command_name(self, command):
        return command.getElementsByTagName("proto")[0].getElementsByTagName("name")[0].childNodes[0].data

    def extract_param_name(self, param):
        param.getElementsByTagName("name")[0].childNodes[0].data

    def extract_param_type(self, param):
        param_type = "const void *"
        types = param.getElementsByTagName("ptype")
        if len(types) > 0:
            param_type = param.getElementsByTagName("ptype")[0].childNodes[0].data

        return param_type

    def extract_param_class(self, param):
        param_class = None

        if param.hasAttribute("class"):
            param_class = param.getAttribute("class")

        return param_class

def camel_case(class_name):
    return ''.join([ item.title() for item in class_name.split(' ')])


def main():
    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse("OpenGL-Registry/xml/gl.xml")
    parser = GLXMLParser()
    commands_el = parser.parse(DOMTree)

    for command_el in commands_el:
        class_ = command_el.get_class()

        if class_ is not None:
            print(command_el, class_)

if __name__ == "__main__":
    print(camel_case('vertex array'))
