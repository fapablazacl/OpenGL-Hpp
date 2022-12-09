

def camel_case(class_name):
    return ''.join([ item.title() for item in class_name.split(' ')])

class CodeGenerator:
    def __init__(self, repository):
        self.__repository = repository

    def generate_consolidated_require(self, require):
        repository = self.__repository

        # collect groups, from commands, for enumeration generation
        group_set = set()
        for command_name in require.commands:
            command = repository.commanddict[command_name]

            for param in command.params:
                if param.group is None or param.group == "" or param.group not in repository.group_to_enums_dict:
                    continue

                group_set.add(param.group)

        # generate enumeration types
        generated_enums = []
        for group_name in group_set:
            generated_enums.append(self.generate_cpp_enum(group_name, repository.group_to_enums_dict[group_name]))
        
        # generate command code 
        generated_commands = []
        for command_name in require.commands:
            generated_commands.append(self.generate_cpp_command(repository.commanddict[command_name]))

        return """#ifndef __gl_hpp__
#define __gl_hpp__
#ifndef __glad_h_
#error This header requires glad.h to be included previously
#endif

namespace gl {{
{}
{}
}}
#endif 
""".format("\n".join(generated_enums), "\n".join(generated_commands))

    def generate_cpp_boolean_enum(self):
        pass

    def generate_cpp_enum(self, cpp_enum_name, enums):
        base_type = ""

        if cpp_enum_name == "Boolean":
            base_type = "GLboolean"
        else:
            base_type = "GLenum"

        tmpl = """enum class {} : {} {{
    {}
}};"""

        entries = [self.generate_cpp_enum_entry(enum) for enum in enums]
        return tmpl.format(cpp_enum_name, base_type, ",\n    ".join(entries))
    
    def convert_constant(self, constant):
        return constant.replace("GL_", "e")

    def generate_cpp_enum_entry(self, enum):
        tmpl = "{} = {}"
        return tmpl.format(self.convert_constant(enum.name), enum.value)

    def generate_cpp_command(self, command):
        return self.generate_method(command)

    def generate_param(self, param):
        tmpl = "{} {}"
        return tmpl.format(self.map_param_type(param), param.name)

    def map_param_type(self, param, ignore_group = False):
        param_type = param.type

        if ignore_group == False and param.has_group() and param.group in self.__repository.group_to_enums_dict:
            param_type = param.group
        
        parts = []
        if param.is_const:
            parts.append("const")

        parts.append(param_type)

        if param.is_pointer:
            parts.append("*")

        return " ".join(parts)
    
    def param_type_must_change(self, param, ignore_group = False):
        if ignore_group == False and param.has_group() and param.group in self.__repository.group_to_enums_dict:
            return True
        
        return False

    def generate_params(self, params):
        return ', '.join([self.generate_param(param) for param in params])

    def generate_method_signature(self, command):
        tmpl = "inline {} {}({})"
        return tmpl.format(command.return_type, self.convert_function_name(command.name), self.generate_params(command.params))

    def convert_function_name(self, name):
        return name[2:3].lower() + name[3:len(name)]

    def generate_method_body(self, command):
        tmpl = """ {{
    return {}({});
}}"""
        param_invoke_list = [self.generate_method_body_param(param) for param in command.params]

        return tmpl.format(command.name, ", ".join(param_invoke_list))

    def generate_method_body_param(self, param):
        if param.has_group() and param.group == "Boolean" and param.is_pointer:
            return f'reinterpret_cast<{self.map_param_type(param, True)}>({param.name})'

        if param.has_group() and not param.is_pointer:
            return f'static_cast<{param.type}>({param.name})'

        if self.param_type_must_change(param) and param.is_pointer:
            const = ""
            if param.is_const:
                const = "const"

            return f'reinterpret_cast<{const} {param.type}*>({param.name})'

        return param.name

    def generate_method(self, command):
        tmpl = """{}{}"""
        return tmpl.format(self.generate_method_signature(command), self.generate_method_body(command))

    def generate_methods(self, commands):
        result = ""

        for command in commands:
            result += self.generate_method(command) + "\n"

        return result

    def generate_class(self, commands, key):
        tmpl = """ 
class {} {{
public:
{}

private:

}};"""
        class_name = camel_case(key)
        return tmpl.format(class_name, self.generate_methods(commands))
