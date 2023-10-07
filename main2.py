
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
        return f'Type( name="{self.name}", c_definition="{self.c_definition}", requires="{self.requires}", comment="{self.comment})"'

class EnumsGroup:
    def __init__(self, namespace, enums):
        self.namespace = namespace
        self.enums = enums

class Registry:
    def __init__(self, types_dict):
        self.types_dict = types_dict


class RegistryFactory:
    def create_registry(self, root_node):
        return Registry(types_dict=self.__extract_type_definitions(root_node))

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


if __name__ == "__main__":
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"

    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)
    print(document)

    root_node = document.childNodes[0]
    registry_factory = RegistryFactory()
    registry = registry_factory.create_registry(root_node)

    for key in registry.types_dict:
        print(registry.types_dict[key])

    # print(registry.types_dict['khrplatform'])
