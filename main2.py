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


class Registry:
    def __init__(self, types_dict, enums_list, command_dict):
        self.types_dict = types_dict
        self.enums_list = enums_list
        self.command_dict = command_dict


class RegistryFactory:
    def create_registry(self, root_node):
        return Registry(
            types_dict=self.__extract_type_definitions(root_node),
            enums_list=self.__extract_enums_definitions(root_node),
            command_dict=self.__extract_commands_definitions(root_node))

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

        types_dict = {}

        for type_node in types_node.childNodes:
            if type_node.nodeType != Node.ELEMENT_NODE:
                continue

            type_ = self.__create_type(type_node)
            if type_ is not None:
                types_dict[type_.name] = type_
            else:
                print("Couldn't extract current type. Dumping child nodes:")
                for child in type_node.childNodes:
                    print("    ", child)

        return types_dict

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

        command_dict = {}

        for commands_node in root.childNodes:
            if commands_node.nodeType == Node.ELEMENT_NODE and commands_node.tagName == "commands":
                for command_node in commands_node.childNodes:
                    if command_node.nodeType == Node.ELEMENT_NODE and command_node.tagName == "command":
                        command = self.__create_command(command_node)
                        command_dict[command.name] = command

        return command_dict

    def __create_command(self, command_node):
        command = Command()

        for child in command_node.childNodes:
            if child.nodeType == Node.ELEMENT_NODE:
                if child.tagName == "proto":
                    self.__fill_command_from_proto_node(command, child)

        return command

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

if __name__ == "__main__":
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"

    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)

    root_node = document.childNodes[0]
    registry_factory = RegistryFactory()
    registry = registry_factory.create_registry(root_node)
    # print(registry.command_dict)

    for key in registry.command_dict:
        print(registry.command_dict[key])

    """
    for key in registry.types_dict:
        print(registry.types_dict[key])
    """

    """"
    for enums in registry.enums_list:
        print(enums)
    """

    # print(registry.types_dict['khrplatform'])
