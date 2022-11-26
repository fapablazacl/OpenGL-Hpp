
import xml.dom.minidom

class Parameter:
    def __init__(self, name, type, class_, len):
        self.name = name
        self.type = type
        self.class_ = class_
        self.len = len

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

        return None
    
    def __str__(self):
        return self.name

class Require:
    def __init__(self) -> None:
        self.enums = []
        self.commands = []
        
class Remove:
    def __init__(self, profile) -> None:
        self.enums = []
        self.commands = []
        self.profile = profile

class Feature:
    def __init__(self, api, name, number, require_list, remove_list) -> None:
        self.api = api
        self.name = name
        self.number = number
        self.require_list = require_list
        self.remove_list = remove_list

    def __str__(self) -> str:
        template_str = "Feature(api={}, name={}, number={}, require_list={}, remove_list={})"
        return template_str.format(self.api, self.name, self.number, len(self.require_list), len(self.remove_list))

    
class GLXMLParser:
    def parse(self, tree):
        registry_el = tree.documentElement

        features = self.parse_features(registry_el)

        for feature in features:
            print(feature)

        commands = []
        for commands_list in registry_el.getElementsByTagName("commands"):
            ns = commands_list.getAttribute("namespace")

            for command_el in commands_list.getElementsByTagName("command"):
                commands.append(self.create_command(ns, command_el))
                
        return commands


    def parse_features(self, registry_el):
        features_el = registry_el.getElementsByTagName("feature")

        return [self.create_feature(feature_el) for feature_el in features_el]
        
    def create_remove(self, remove_el):
        remove = Remove(profile=remove_el.getAttribute("profile"))

        for enum_el in remove_el.getElementsByTagName("enum"):
            name = enum_el.getAttribute("name")
            remove.enums.append(name)

        for command_el in remove_el.getElementsByTagName("command"):
            name = command_el.getAttribute("name")
            remove.commands.append(name)

        return remove

    def create_require(self, require_el):
        require = Require()

        for enum_el in require_el.getElementsByTagName("enum"):
            name = enum_el.getAttribute("name")
            require.enums.append(name)

        for command_el in require_el.getElementsByTagName("command"):
            name = command_el.getAttribute("name")
            require.commands.append(name)

        return require

    def create_feature(self, feature_el):
        require_list = [self.create_require(require_el) for require_el in feature_el.getElementsByTagName("require")]        
        remove_list = [self.create_remove(remove_el) for remove_el in feature_el.getElementsByTagName("remove")]

        feature = Feature(
            api = feature_el.getAttribute("api"),
            name = feature_el.getAttribute("name"),
            number =  feature_el.getAttribute("number"),
            require_list=require_list,
            remove_list=remove_list
        )

        return feature

    def create_command(self, namespace, command_el):
        name = self.extract_command_name(command_el)
        return_type = self.extract_command_return_type(command_el)
        
        params = []
        for param_el in command_el.getElementsByTagName("param"):
            parameter = self.create_parameter(param_el)
            params.append(parameter)

        return Command(name=name, return_type=return_type, params=params, namespace=namespace, group=None)
        

    def create_parameter(self, param_el):
        return Parameter(
            self.extract_param_name(param_el),
            self.extract_param_type(param_el),
            self.extract_param_class(param_el),
            self.extract_param_len(param_el)
        )

    def extract_command_return_type(self, command):
        proto = command.getElementsByTagName("proto")[0]

        types = proto.getElementsByTagName("ptype")
        if len(types) > 0:
            return types[0].childNodes[0].data

        # void data type
        return proto.childNodes[0].data

        
    def extract_command_name(self, command):
        return command.getElementsByTagName("proto")[0].getElementsByTagName("name")[0].childNodes[0].data

    def extract_param_name(self, param):
        return param.getElementsByTagName("name")[0].childNodes[0].data

    def extract_param_type(self, param):
        param_type = "const void *"
        types = param.getElementsByTagName("ptype")
        if len(types) > 0:
            param_type = types[0].childNodes[0].data

        return param_type

    def extract_param_class(self, param):
        param_class = None

        if param.hasAttribute("class"):
            param_class = param.getAttribute("class")

        return param_class

    def extract_param_len(self, param):
        if param.hasAttribute("len"):
            return param.getAttribute("len")
        
        return None


def camel_case(class_name):
    return ''.join([ item.title() for item in class_name.split(' ')])


def consolidate_classes(commands):
    classdict = {}

    for command in commands:
        class_ = command.get_class()
        if class_ is None:
            continue

        class_commands = None
        if class_ in classdict:
            class_commands = classdict[class_]
        else:
            class_commands = []
            classdict[class_] = class_commands

        class_commands.append(command)
    
    return classdict

def generate_param(param):
    tmpl = "{} {}"
    return tmpl.format(param.type, param.name)
    
def generate_params(params):
    return ', '.join([generate_param(param) for param in params])

def generate_method_signature(command):
    tmpl = "{} {}({})"
    return tmpl.format(command.return_type, command.name, generate_params(command.params))


def generate_method_body(command):
    tmpl = """ {{

}}
"""
    return tmpl.format()

def generate_method(command):
    tmpl = """{}{}"""
    return tmpl.format(generate_method_signature(command), generate_method_body(command))

def generate_methods(commands):
    result = ""

    for command in commands:
        result += generate_method(command) + "\n"

    return result

def generate_class(commands, key):
    tmpl = """ 
class {} {{
public:
{}

private:


}};"""

    class_name = camel_case(key)
    return tmpl.format(class_name, generate_methods(commands))


def main():
    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse("OpenGL-Registry/xml/gl.xml")
    parser = GLXMLParser()

    commands = parser.parse(DOMTree)
    classdict = consolidate_classes(commands)

    key = "texture"
    generate_class(classdict[key], key)
    
    """
    for key in classdict:
        generate_class(classdict[key], key)
    """


if __name__ == "__main__":
    # print(camel_case('vertex array'))
    main()
