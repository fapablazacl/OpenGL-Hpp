
import xml.dom.minidom
from xml.dom.minidom import Node

import sys

class Type:
    def __init__(self, name, c_definition, requires=None, comment=None):
        self.name = name
        self.c_definition = c_definition
        self.requires = requires
        self.comment = comment

class Enum:
    def __init__(self, value, name, group=None, alias=None, comment=None):
        self.value = value
        self.name = name
        self.group = group
        self.alias = alias
        self.comment = comment

class EnumsGroup:
    def __init__(self, namespace, enums):
        self.namespace = namespace
        self.enums = enums

def genspaces(count):
    spaces = ""

    for i in range(count):
        spaces += " "

    return spaces

def display(node, level = 0):
    if node.nodeType == Node.ELEMENT_NODE:
        print(genspaces(level * 2), node.tagName)
    else:
        print(genspaces(level * 2), node)

    for child in node.childNodes:
        display(child, level + 1)

def extract_type_definitions(root):
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

    types = []

    for type_node in types_node.childNodes:
        if type_node.nodeType != Node.ELEMENT_NODE:
            continue

        name = type_node.getAttribute("name")

        if name != '':
            type = Type(name=name, c_definition=None, requires=None, comment=None)
        else:
            for child in type_node.childNodes:
                if child.nodeType == Node.ELEMENT_NODE and child.tagName == "name":
                    name = child.firstChild.data.strip()
                    
            type = Type(name=name, c_definition=None, requires=None, comment=None)

        types.append(type)

        print(type)

        if name == '':
            name = "<noname>"

        print(name)

        for child in type_node.childNodes:
            print("    ", child)

    return types


if __name__ == "__main__":
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"

    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)
    print(document)

    root_node = document.childNodes[0]
    types = extract_type_definitions(root_node)
    # print(types)
