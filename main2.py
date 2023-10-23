import os.path
import xml.dom.minidom

from oglhppgen.model import RegistryFactory
from oglhppgen.c_generator import C_Generator

if __name__ == "__main__":
    parent_path = "tests/test-dynamicLoading"
    gl_xml_file_path = "OpenGL-Registry/xml/gl.xml"
    # Open XML document using minidom parser
    document = xml.dom.minidom.parse(gl_xml_file_path)

    root_node = document.childNodes[0]
    registry_factory = RegistryFactory()
    registry = registry_factory.create_registry(root_node)

    generator = C_Generator(registry=registry)
    lib_source_dict = generator.generate(api="gl", number="1.0")

    for filename_suffix in lib_source_dict:
        print(f"Generating {filename_suffix}")

        code = lib_source_dict[filename_suffix]
        filename = os.path.join("tests/test-dynamicLoading", filename_suffix)
        text_file = open(filename, "w")
        text_file.write(code)
        text_file.close()
