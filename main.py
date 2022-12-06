
import xml.dom.minidom

import glregistry
import hppgenerator

def main():
    # Open XML document using minidom parser
    DOMTree = xml.dom.minidom.parse("OpenGL-Registry/xml/gl.xml")
    parser = glregistry.GLXMLParser()
    repository = parser.create_repository(DOMTree)
    generator = hppgenerator.CodeGenerator(repository)
    consolidated_require = repository.consolidate("gl", "3.3")
    generated_code = generator.generate_consolidated_require(consolidated_require)
    print(generated_code)

    """
    classdict = consolidate_classes(commands)

    key = "texture"
    generate_class(classdict[key], key)
    
    for key in classdict:
        generate_class(classdict[key], key)
    """

if __name__ == "__main__":
    main()
