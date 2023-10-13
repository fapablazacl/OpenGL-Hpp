
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
    code = generator.generate(api="gl", number="1.0")

    text_file = open("tests/test-dynamicLoading/include/oglhpp/GL.h", "w")
    text_file.write(code)
    text_file.close()
