
import xml.dom.minidom
from xml.dom.minidom import Node

class Parameter:
    def __init__(self, name, type, class_, len, group, is_const, is_pointer):
        self.name = name
        self.type = type
        self.class_ = class_
        self.len = len
        self.group = group
        self.is_const = is_const
        self.is_pointer = is_pointer
        
    def has_class(self):
        return self.class_ is not None

    def has_group(self):
        if self.group is None:
            return False
        
        if self.group == "":
            return False
        
        return True

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        tmpl = "Parameter(name={}, type={}, class={}, len={}, group={}, is_const={}, is_pointer={})"
        return tmpl.format(self.name, self.type, self.class_, self.len, self.group, self.is_const, self.is_pointer)


class EnumCollection:
    def __init__(self, namespace, enums, group, type, vendor) -> None:
        self.namespace = namespace
        self.enums = enums
        self.group = group
        self.type = type
        self.vendor = vendor

class Enum:
    def __init__(self, name, value, groups) -> None:
        self.name = name
        self.value = value
        self.groups = groups

    def __repr__(self) -> str:
        return "Enum(name={}, value={})".format(self.name, self.value)

    def __str__(self) -> str:
        return "Enum(name={}, value={}, groups={})".format(self.name, self.value, self.groups)

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
        tmpl = "Command(name={}, return_type={}, params={}, namespace={}, group={})"
        return tmpl.format(self.name, self.return_type, self.params, self.namespace, self.group)

class Require:
    def __init__(self, enums, commands) -> None:
        self.enums = enums
        self.commands = commands

    def __str__(self) -> str:
        return "Require(enums={}, commands={})".format(self.enums, self.commands)
        
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

class Repository:
    def __init__(self, features, commands, enumscollections) -> None:
        self.features = features
        self.commands = commands

        self.commanddict = {}
        for command in commands:
            self.commanddict[command.name] = command

        self.enumscollections = enumscollections
        self.group_to_enums_dict = self.__create_group_to_enums_dict(self.enumscollections)
        self.objectdict = self.__consolidate_classes(self.commands)

        self.features_per_api = {}
        for feature in self.features:
            api = feature.api

            if api not in self.features_per_api:
                self.features_per_api[api] = []
            
            self.features_per_api[api].append(feature)

    def __create_group_to_enums_dict(self, enumscollections):
        group_to_enums_dict = {}

        for enum_collection in enumscollections:
            for enum in enum_collection.enums:
                for group in enum.groups:
                    enums = None

                    if group in group_to_enums_dict:
                        enums = group_to_enums_dict[group]
                    else:
                        enums = []
                        group_to_enums_dict[group] = enums

                    enums.append(enum)

        return group_to_enums_dict

    def __consolidate_classes(self, commands):
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

    def consolidate(self, api, number):
        features = self.features_per_api[api]

        consolidated_require = Require(set(), set())

        # append first all feature contents
        for feature in features:
            if feature.number > number:
                continue
            
            for require in feature.require_list:
                for command in require.commands:
                    consolidated_require.commands.add(command)

                for enum in require.enums:
                    consolidated_require.enums.add(enum)
        
        
        # remove all deprecated commands and enumerations
        for feature in features:
            if feature.number > number:
                continue
            
            for remove in feature.remove_list:
                for command in remove.commands:
                    consolidated_require.commands.remove(command)

                for enum in remove.enums:
                    consolidated_require.enums.remove(enum)
        
        return consolidated_require
                
class GLXMLParser:
    def create_repository(self, tree):
        registry_el = tree.documentElement
        features = self.parse_features(registry_el)

        commands = []
        for commands_list in registry_el.getElementsByTagName("commands"):
            ns = commands_list.getAttribute("namespace")

            for command_el in commands_list.getElementsByTagName("command"):
                commands.append(self.create_command(ns, command_el))

        enumscollections = [self.create_enumcollection(enums_el) for enums_el in registry_el.getElementsByTagName("enums")]
        
        return Repository(features=features, commands=commands, enumscollections=enumscollections)
    
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
        enums = [enum_el.getAttribute("name") for enum_el in require_el.getElementsByTagName("enum")]
        commands = [command_el.getAttribute("name") for command_el in require_el.getElementsByTagName("command")]

        return Require(enums=enums, commands=commands)

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

    def create_enumcollection(self, enums_el):
        ns = enums_el.getAttribute("namespace")
        group = enums_el.getAttribute("group")
        type = enums_el.getAttribute("type")
        vendor = enums_el.getAttribute("vendor")
        enums = [self.create_enum(enum_el) for enum_el in enums_el.getElementsByTagName("enum")]
        enum_collection = EnumCollection(namespace=ns, enums=enums, group=group, type=type, vendor=vendor)

        return enum_collection

    def create_enum(self, enum_el):
        return Enum(
            name = enum_el.getAttribute("name"), 
            value = enum_el.getAttribute("value"), 
            groups = enum_el.getAttribute("group").split(","))

    def create_command(self, namespace, command_el):
        name = self.extract_command_name(command_el)
        return_type = self.extract_command_return_type(command_el)
        params = [self.create_parameter(param_el) for param_el in command_el.getElementsByTagName("param")]

        command = Command(name=name, return_type=return_type, params=params, namespace=namespace, group=None)
        
        return command
        
    def create_parameter(self, param_el):
        param = Parameter(
            self.extract_param_name(param_el),
            self.extract_param_type(param_el),
            self.extract_param_class(param_el),
            self.extract_param_len(param_el),
            self.extract_param_group(param_el),
            self.extract_param_is_const(param_el), 
            self.extract_param_is_pointer(param_el)
        )

        return param

    def extract_param_is_const(self, param_el):
        for node in param_el.childNodes:
            if node.nodeType != Node.TEXT_NODE:
                continue

            if node.data.strip() == "const":
                return True
        
        return False

    def extract_param_is_pointer(self, param_el):
        for node in param_el.childNodes:
            if node.nodeType != Node.TEXT_NODE:
                continue

            if node.data.strip() == "*":
                return True
        
        return False

    def extract_param_group(self, param_el):
        return param_el.getAttribute("group")

    def extract_param_name(self, param):
        return param.getElementsByTagName("name")[0].childNodes[0].data

    def extract_param_type(self, param):
        param_type = None
        types = param.getElementsByTagName("ptype")
        if len(types) > 0:
            param_type = types[0].childNodes[0].data
        else:
            for node in param.childNodes:
                if node.nodeType == Node.TEXT_NODE:
                    param_type = node.data.strip()
                    break
        
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

    def extract_command_return_type(self, command):
        # <proto group="String">const <ptype>GLubyte</ptype> *<name>glGetString</name></proto>
        proto = command.getElementsByTagName("proto")[0]
        parts = []

        for node in proto.childNodes:
            if node.nodeType == Node.TEXT_NODE:
                parts.append(node.data.strip())

            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "ptype":
                parts.append(node.childNodes[0].data.strip())

        return " ".join(parts)

    def extract_command_name(self, command):
        return command.getElementsByTagName("proto")[0].getElementsByTagName("name")[0].childNodes[0].data
