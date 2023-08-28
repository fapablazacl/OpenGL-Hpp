
import xml.dom.minidom
import sys
import glregistry
import hppgenerator
import os

def generate_hpp_header_filename(api, version):
    return api + version.replace(".", "") + ".hpp"

def generate_hpp_header(gl_xml_file_path, api, version, output_folder):
    print("generating header file, with api '" + api + "' and version '" + version + "'")

    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse(gl_xml_file_path)
    parser = glregistry.GLXMLParser()
    repository = parser.create_repository(DOMTree)
    generator = hppgenerator.CodeGenerator(repository)
    consolidated_require = repository.consolidate(api, version)
    generated_code = generator.generate_consolidated_require(consolidated_require)

    output_filename = os.path.join(output_folder, generate_hpp_header_filename(api, version))

    file = open(output_filename, "w")
    file.write(generated_code)
    file.close()


def main():
    generate_hpp_header("OpenGL-Registry/xml/gl.xml", "gl", "3.3", "tests/test-gl10")
    
if __name__ == "__main__":
    main()
