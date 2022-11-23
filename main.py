
import xml.dom.minidom

# Open XML document using minidom parser
DOMTree = xml.dom.minidom.parse("OpenGL-Registry/xml/gl.xml")
registry = DOMTree.documentElement

for commands in registry.getElementsByTagName("commands"):
    ns = commands.getAttribute("namespace")

    for command in commands.getElementsByTagName("command"):
        name = command.getElementsByTagName("proto")[0].getElementsByTagName("name")[0].childNodes[0].data
        
        params = []

        for param in command.getElementsByTagName("param"):
            # extract raw name
            param_name = param.getElementsByTagName("name")[0].childNodes[0].data

            # extract raw data type
            param_type = "const void *"
            types = param.getElementsByTagName("ptype")
            if len(types) > 0:
                param_type = param.getElementsByTagName("ptype")[0].childNodes[0].data

            # extract class -> this is a hint for a potential C++ RAAI class
            param_class = None

            if param.hasAttribute("class"):
                param_class = param.getAttribute("class")
            
            # construct parameter dictionary data
            param = {
                "name" : param_name,
                "type" : param_type 
            }

            if param_class is not None:
                param["class"] = param_class

            # append parameter to the parameter dictionary
            params.append(param)

        print(name, params)
