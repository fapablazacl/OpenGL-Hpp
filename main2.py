
import xml.dom.minidom

from oglhppgen.model import RegistryFactory
from oglhppgen.c_generator import C_Generator

if __name__ == "__main__":
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"

    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)

    root_node = document.childNodes[0]
    registry_factory = RegistryFactory()
    registry = registry_factory.create_registry(root_node)

    generator = C_Generator(registry=registry)
    code = generator.generate(api="gl", number="1.1")

    print(code)

    """
    for value in registry.feature_list[0].require_list[0].type_list:
        print(value)

    for value in registry.feature_list[0].require_list[0].enum_list:
        print(value)

    for value in registry.feature_list[0].require_list[0].command_list:
        print(value)
    """

    """"
    print(registry.feature_list[0].require_list[0].type_list)
    print(registry.feature_list[0].require_list[0].enum_list)
    print(registry.feature_list[0].require_list[0].command_list)
    """

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
