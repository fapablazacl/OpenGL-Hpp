import xml.dom.minidom
from xml.dom.minidom import Node

import sys


# Type is used here to denote:
# 1. Header requirements (khrplatform.h)
# 2. Typedefs from basic types (like GLenum). The name is denoted by the "name" inner tag
# 3. Typedefs

# Types have too dependencies, specified by the "requires" attributes
#

class Type:
    def __init__(self, name, c_definition, requires=None, comment=None):
        self.name = name
        self.c_definition = c_definition
        self.requires = requires
        self.comment = comment

    def __str__(self):
        return f'Type( name="{self.name}", c_definition="{self.c_definition}", requires="{self.requires}", comment="{self.comment}")'


class Enum:
    def __init__(self, value, name, group=None, alias=None, comment=None):
        self.value = value
        self.name = name
        self.group = group
        self.alias = alias
        self.comment = comment

    def __str__(self):
        return f'Enum( value="{self.value}", name="{self.name}", group="{self.group}", alias="{self.alias}", comment="{self.comment})"'


class Enums:
    def __init__(self, namespace, group, enums_type, enum_dict, start=None, end=None, vendor=None, comment=None):
        self.namespace = namespace
        self.group = None if group == '' else group
        self.enum_group_type = None if enums_type == '' else enums_type
        self.enum_dict = enum_dict
        self.start = None if start == '' else start
        self.end = None if end == '' else end
        self.vendor = None if vendor == '' else vendor
        self.comment = None if comment == '' else comment

    def __str__(self):
        return f'Enums( namespace="{self.namespace}", group="{self.group}", enum_group_type="{self.enum_group_type}", enum_dict="{self.enum_dict}", start="{self.start}", end="{self.end}", vendor="{self.vendor}", comment="{self.comment}"'

class TypeDecl:
    def __init__(self, name, is_pointer = False):
        self.name = name
        self.is_pointer = is_pointer

    def __str__(self):
        return f'TypeDecl(name="{self.name}", is_pointer="{self.is_pointer}")'

class Command:
    def __init__(self):
        self.name = None
        self.return_type = None
        self.params = []

    def __str__(self):
        return f'Command(name="{self.name}", return_type="{self.return_type}", params="{self.params}")'

    def __repr__(self):
        return f'{self}'

class CommandParam:
    def __init__(self, group, data_type, pointer_indirection, name, len):
        self.group = group if group != "" else None
        self.data_type = data_type
        self.pointer_indirection = pointer_indirection
        self.name = name
        self.len = len if len != "" else None

    def __str__(self):
        return f'CommandParam(group="{self.group}", name="{self.name}", pointer_indirection="{self.pointer_indirection}", data_type="{self.data_type}", len="{self.len}")'

    def __repr__(self):
        return f'{str(self)}'

class TypeRef:
    def __init__(self, name, comment):
        self.name = name
        self.comment = None if comment == "" else comment

    def __str__(self):
        return f'TypeRef(name="{self.name}", comment="{self.comment}")'


class EnumRef:
    def __init__(self, name, comment):
        self.name = name
        self.comment = None if comment == "" else comment

    def __str__(self):
        return f'EnumRef(name="{self.name}", comment="{self.comment}")'

class CommandRef:
    def __init__(self, name, comment):
        self.name = name
        self.comment = None if comment == "" else comment

    def __str__(self):
        return f'CommandRef(name="{self.name}", comment="{self.comment}")'


class Require:
    def __init__(self, type_list, enum_list, command_list):
        self.type_list = type_list
        self.enum_list = enum_list
        self.command_list = command_list

class Feature:
    def __init__(self, api, name, number, require_list = None):
        self.api = api
        self.name = name
        self.number = number
        self.require_list = [] if (require_list is None) else require_list

    def __str__(self):
        return f'Feature(api="{self.api}", name="{self.name}", number="{self.number}", len(require_list)={len(self.require_list)}'

    def __repr__(self):
        return f'{str(self)}'

class Extension:
    def __init__(self, name, supported, require_list):
        self.name = name
        self.supported = supported
        self.require_list = require_list

    def __str__(self):
        return f'Extension(name="{self.name}", supported="{self.supported}", len(require_list)="{len(self.require_list)}")'

    def __repr__(self):
        return f'{str(self)}'

class Extensions:
    def __init__(self, extension_list):
        self.extension_list = extension_list

    def __str__(self):
        return f'Extensions(extension_list="{self.extension_list}")'


class Registry:
    def __init__(self, types_list, enums_list, command_list, feature_list, extensions):
        self.types_dict = types_list
        self.enums_list = enums_list
        self.command_list = command_list
        self.feature_list = feature_list
        self.extensions = extensions

    def __str__(self):
        return f'Registry(types_list="{self.types_dict}", enums_list="{self.enums_list}", command_list="{self.command_list}", feature_list="{self.feature_list}", extensions="{self.extensions}")'


class RegistryFactory:
    def create_registry(self, root_node):
        return Registry(
            types_list=self.__extract_type_definitions(root_node),
            enums_list=self.__extract_enums_definitions(root_node),
            command_list=self.__extract_commands_definitions(root_node),
            feature_list=self.__extract_feature_definitions(root_node),
            extensions=self.__extract_extensions_definition(root_node))

    def __genspaces(self, count):
        spaces = ""

        for i in range(count):
            spaces += " "

        return spaces

    def __display(self, node, level=0):
        if node.nodeType == Node.ELEMENT_NODE:
            print(self.__genspaces(level * 2), node.tagName)
        else:
            print(self.__genspaces(level * 2), node)

        for child in node.childNodes:
            self.__display(child, level + 1)

    def __try_create_type_with_name_attrib(self, type_node):
        name = type_node.getAttribute("name")

        if name == '':
            return None

        requires = type_node.getAttribute("requires")
        if requires == '':
            requires = None

        c_definition = self.__create_c_definition(type_node)

        comment = type_node.getAttribute("comment")
        if comment == '':
            comment = None

        return Type(name=name, c_definition=c_definition, requires=requires, comment=comment)

    def __try_create_type_with_name_node(self, type_node):
        name = None

        for child in type_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE and child.tagName == "name":
                name = child.firstChild.data.strip()

        if name is None:
            return None

        requires = type_node.getAttribute("requires")
        if requires == '':
            requires = None

        c_definition = self.__create_c_definition(type_node)

        comment = type_node.getAttribute("comment")
        if comment == '':
            comment = None

        return Type(name=name, c_definition=c_definition, requires=requires, comment=comment)

    def __create_c_definition(self, type_node):
        definition = ''

        for child in type_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                child_definition = self.__create_c_definition(child)
                definition += child_definition
            elif child.nodeType == Node.TEXT_NODE:
                # Handle text content nodes
                definition += child.nodeValue

        return definition

    def __linearize_node_branch(self, node):
        return node.data.strip()

    def __create_type(self, type_node):
        type_ = self.__try_create_type_with_name_node(type_node)

        if type_ is not None:
            return type_

        return self.__try_create_type_with_name_attrib(type_node)

    def __extract_type_definitions(self, root):
        if root.nodeType != Node.ELEMENT_NODE:
            raise Exception("excepted element node as root")

        if root.tagName != "registry":
            raise Exception("expected registry node tag as root")

        types_node = None

        for node in root.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "types":
                types_node = node
                break

        if types_node is None:
            raise Exception('types node not found in registry root node.')

        types_list = []

        for type_node in types_node.childNodes:
            if type_node.nodeType != Node.ELEMENT_NODE:
                continue

            type_ = self.__create_type(type_node)

            if type_ is not None:
                types_list.append(type_)
            else:
                print("Warning: couldn't extract current type. Dumping child nodes:")
                for child in type_node.childNodes:
                    print("    ", child)

        return types_list

    def __extract_enums_definitions(self, root):
        if root.nodeType != Node.ELEMENT_NODE:
            raise Exception("excepted element node as root")

        if root.tagName != "registry":
            raise Exception("expected registry node tag as root")

        enums_list = []

        for node in root.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "enums":
                enums = self.__create_enums(node)
                enums_list.append(enums)

        return enums_list

    def __create_enums(self, enums_node):
        enums_dict = {}

        for node in enums_node.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "enum":
                enum = self.__create_enum(node)
                enums_dict[enum.name] = enum

        return Enums(
            namespace=enums_node.getAttribute("namespace"),
            group=enums_node.getAttribute("group"),
            enums_type=enums_node.getAttribute("type"),
            enum_dict=enums_dict,
            start=enums_node.getAttribute("start"),
            end=enums_node.getAttribute("end"),
            vendor=enums_node.getAttribute("vendor"),
            comment=enums_node.getAttribute("comment"))

    def __create_enum(self, enum_node):
        return Enum(
            value=enum_node.getAttribute("value"),
            name=enum_node.getAttribute("name"),
            group=enum_node.getAttribute("group"))

    def __extract_commands_definitions(self, root):
        if root.nodeType != Node.ELEMENT_NODE:
            raise Exception("excepted element node as root")

        if root.tagName != "registry":
            raise Exception("expected registry node tag as root")

        command_list = []

        for commands_node in root.childNodes:
            if commands_node.nodeType == Node.ELEMENT_NODE and commands_node.tagName == "commands":
                for command_node in commands_node.childNodes:
                    if command_node.nodeType == Node.ELEMENT_NODE and command_node.tagName == "command":
                        command = self.__create_command(command_node)
                        command_list.append(command)

        return command_list

    def __create_command(self, command_node):
        command = Command()

        params = []

        for child in command_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.tagName == "proto":
                    self.__fill_command_from_proto_node(command, child)
                elif child.tagName == "param":
                    param = self.__create_command_param(command_param_node=child)
                    params.append(param)


        command.params = params

        return command

    def __create_command_param(self, command_param_node):
        group = command_param_node.getAttribute("group")
        ptype = None
        name = None
        pointer_indirection = 0
        len = command_param_node.getAttribute("len")

        for child in command_param_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.tagName == "ptype":
                    ptype = child.firstChild.data.strip()
                elif child.tagName == "name":
                    name = child.firstChild.data.strip()

            if child.nodeType == Node.TEXT_NODE:
                if child.nodeValue.strip() == "*":
                    pointer_indirection += 1

        return CommandParam(group=group, data_type=ptype, name=name, pointer_indirection=pointer_indirection, len=len)

    def __fill_command_from_proto_node(self, command, command_proto_node):
        for child in command_proto_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.tagName == "name":
                    command.name = child.firstChild.data.strip()
                elif child.tagName == "ptype":
                    type_name = child.firstChild.data.strip()
                    command.return_type = TypeDecl(name=type_name, is_pointer=True)

            elif child.nodeType == Node.TEXT_NODE:
                type_name = child.nodeValue.strip()
                if type_name == "":
                    continue

                command.return_type = TypeDecl(name=type_name)

    def __extract_feature_definitions(self, root):
        feature_list = []

        for feature_node in root.childNodes:
            if feature_node.nodeType != Node.ELEMENT_NODE:
                continue

            if feature_node.tagName != "feature":
                continue

            feature = self.__create_feature(feature_node)
            feature_list.append(feature)

        return feature_list


    def __create_feature(self, feature_node):
        api = feature_node.getAttribute("api")
        name = feature_node.getAttribute("name")
        number = feature_node.getAttribute("number")
        require_list = []

        for require_node in feature_node.childNodes:
            if require_node.nodeType != Node.ELEMENT_NODE:
                continue

            if require_node.tagName != "require":
                continue

            require = self.__create_require(require_node)
            require_list.append(require)

        return Feature(api=api, name=name, number=number, require_list=require_list)

    def __create_require(self, require_node):
        type_list = []
        enum_list = []
        command_list = []

        for child in require_node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue

            if child.tagName == "type":
                type_ref = TypeRef(name=child.getAttribute("name"), comment=child.getAttribute("comment"))
                type_list.append(type_ref)
                continue

            elif child.tagName == "enum":
                enum_ref = EnumRef(name=child.getAttribute("name"), comment=child.getAttribute("comment"))
                enum_list.append(enum_ref)
                continue

            elif child.tagName == "command":
                command_ref = CommandRef(name=child.getAttribute("name"), comment=child.getAttribute("comment"))
                command_list.append(command_ref)
                continue

        return Require(type_list=type_list, enum_list=enum_list, command_list=command_list)

    def __extract_extensions_definition(self, root):
        for extensions_node in root.childNodes:
            if extensions_node.nodeType != Node.ELEMENT_NODE:
                continue

            if extensions_node.tagName != "extensions":
                continue

            extension_list = self.__extract_extensions_definitions(extensions_node=extensions_node)
            return Extensions(extension_list=extension_list)

        return None


    def __extract_extensions_definitions(self, extensions_node):
        extension_list = []

        for extension_node in extensions_node.childNodes:
            if extension_node.nodeType != Node.ELEMENT_NODE:
                continue

            if extension_node.tagName != "extension":
                continue

            extension = self.__create_extension(extension_node)
            extension_list.append(extension)

        return extension_list

    def __create_extension(self, extension_node):
        name = extension_node.getAttribute("name")
        supported = extension_node.getAttribute("supported").split('|')
        require_list = []

        for child in extension_node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue

            if child.tagName != "require":
                continue

            require = self.__create_require(require_node=child)
            require_list.append(require)

        return Extension(name=name, supported=supported, require_list=require_list)


if __name__ == "__main__":
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"

    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)

    root_node = document.childNodes[0]
    registry_factory = RegistryFactory()
    registry = registry_factory.create_registry(root_node)
    print(registry)

    """
    for value in registry.feature_list[0].require_list[0].type_list:
        print(value)

    for value in registry.feature_list[0].require_list[0].enum_list:
        print(value)

    for value in registry.feature_list[0].require_list[0].command_list:
        print(value)
    """

    #print(registry.feature_list[0].require_list[0].type_list)
    #print(registry.feature_list[0].require_list[0].enum_list)
    #print(registry.feature_list[0].require_list[0].command_list)

    """
    for key in registry.command_dict:
        print(registry.command_dict[key])
    """

    """
    # print(registry.command_dict["glGetSubroutineIndex"])
    for key in registry.types_dict:
        print(registry.types_dict[key])
    """

    """"
    for enums in registry.enums_list:
        print(enums)
    """
