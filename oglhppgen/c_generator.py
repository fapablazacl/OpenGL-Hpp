class C_Generator:
    def __init__(self, registry):
        self.__registry = registry

        self.__available_api_numbers = {
            'gl': ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '2.0', '2.1', '3.0', '3.1', '3.2', '3.3', '4.0', '4.1',
                   '4.2', '4.3', '4.4', '4.5', '4.6'],
            'gles1': ['1.0'],
            'gles2': ['2.0', '3.0', '3.1', '3.2'],
            'glsc2': ['2.0'],
        }

        # index feature list by api, and then, by version number
        self.__feature_by_api_number = self.__create_feature_by_api_number_dict(self.__registry.feature_list)
        self.__type_by_name = {}
        for value in self.__registry.types_list:
            self.__type_by_name[value.name] = value

        self.__enum_by_name = {}
        for enums in self.__registry.enums_list:
            for key in enums.enum_dict:
                self.__enum_by_name[key] = enums.enum_dict[key]

        self.__command_by_name = {}
        for value in self.__registry.command_list:
            self.__command_by_name[value.name] = value

    def __generate_header(self, features, type_name_set):
        code = ''
        code += f'{self.__generate_header_prologue()}'

        code += '/* loader declarations */\n'
        code += f'typedef void (*OGLHPP_PROC)(void);\n'
        code += f'typedef OGLHPP_PROC (*OGLHPP_GETPROCADDRESS)(const char *name);\n'
        code += f'extern void oglhpp_load_functions(OGLHPP_GETPROCADDRESS getProcAddress);\n\n'

        code += '/* data type definitions */\n'
        code += f'{self.__generate_types(type_name_set)}'
        code += '\n\n'.join([self.__generate_header_from_feature(feature) for feature in features])
        code += f'{self.__generate_header_epilogue()}'

        return code

    def __generate_source(self, features, type_name_set):
        code = '#include <oglhpp/gl.h>\n\n'
        code += '\n\n'.join([self.__generate_source_from_feature(feature) for feature in features])

        return code

    def generate(self, api, number):
        self.__check_api_number(api, number)
        features = self.__collect_features(api, number)
        type_name_set = self.__collect_types(features)

        return {
            'include/oglhpp/gl.h': self.__generate_header(features, type_name_set),
            'src/gl.c': self.__generate_source(features, type_name_set)
        }

    def __generate_header_prologue(self):
        return """
#pragma once 

#ifndef __OGLHPP_GL_H__
#define __OGLHPP_GL_H__

#include <KHR/khrplatform.h>

#if defined(__gl_h_) || defined(__GL_H__)
  #error please include this header instead
#endif

#define __gl_h_
#define __GL_H__

#if _WIN32
  #define GLAPI 
  #define GLCALLCONV __stdcall
#else 
  #define GLAPI
  #define GLCALLCONV
#endif

#if defined(__cplusplus)
extern "C" {
#endif

"""

    def __generate_header_epilogue(self):
        return """  
#if defined(__cplusplus)
}
#endif

#endif
"""

    def __collect_types(self, features):
        # collect data type definitions from the commands
        type_name_set = set()

        for feature in features:
            for require in feature.require_list:
                for command_ref in require.command_list:
                    command = self.__command_by_name[command_ref.name]

                    for param in command.params:
                        if param.data_type is not None:
                            type_name_set.add(param.data_type)

        return type_name_set

    def __generate_types(self, type_name_set):
        code = ''

        for type_name in type_name_set:
            type_ = self.__type_by_name[type_name]
            code += f'{self.__generate_type(type_)}\n'

        return code

    def __generate_header_from_feature(self, feature):
        code = f'/* {feature.name} definitions */\n'

        for require in feature.require_list:
            for type_ref in require.type_list:
                type_ = self.__type_by_name[type_ref.name]
                code += f'{self.__generate_type(type_)}\n'

            for enum_ref in require.enum_list:
                enum = self.__enum_by_name[enum_ref.name]
                code += f'{self.__generate_enum(enum)}\n'

            for command_ref in require.command_list:
                command = self.__command_by_name[command_ref.name]
                code += f'{self.__generate_command_ptr_typedef(command)}\n'
                code += f'{self.__generate_command_ptr_variable(command, extern=True)}\n'
                code += '\n'

        return code

    def __generate_source_from_feature(self, feature):
        command_list = []

        code = f'/* {feature.name} function pointer variables */\n'

        for require in feature.require_list:
            for command_ref in require.command_list:
                command = self.__command_by_name[command_ref.name]
                code += f'{self.__generate_command_ptr_variable(command, extern=False)}\n'

                command_list.append(command)

        code += f'\n{self.__generate_loader_from_command_list(command_list)}'

        return code

    def __generate_loader_from_command_list(self, command_list):
        code = "void oglhpp_load_functions(OGLHPP_GETPROCADDRESS getProcAddress) {\n"

        for command in command_list:
            command_name = command.name
            command_ptr_variable_type = self.__generate_command_ptr_name(command.name)
            command_ptr_variable_name = self.__generate_command_ptr_variable_name(command.name)

            code += f'    {command_ptr_variable_name} = ({command_ptr_variable_type})getProcAddress("{command_name}");\n'

        code += '}'

        return code

    def __generate_type(self, type):
        return type.c_definition

    def __generate_enum(self, enum):
        return f'#define {enum.name} {enum.value}'

    def __generate_command_ptr_name(self, command_name):
        return f'PFN{command_name.upper()}PROC'

    def __generate_command_ptr_typedef(self, command):
        return_type_str = self.__generate_command_return_type(command.return_type)
        params_str = ', '.join([self.__generate_command_param(param) for param in command.params])
        name = self.__generate_command_ptr_name(command.name)

        return f'typedef GLAPI {return_type_str} (GLCALLCONV *{name})({params_str});'

    def __generate_command_ptr_variable_name(self, command_name):
        return f'{command_name}'

    def __generate_command_ptr_variable(self, command, extern = False):
        type_name = self.__generate_command_ptr_name(command.name)
        variable_name = self.__generate_command_ptr_variable_name(command.name)

        extern_str = 'extern ' if extern else ''

        return f'{extern_str}{type_name} {variable_name};'

    def __generate_command_prototype(self, command):
        return_type_str = self.__generate_command_return_type(command.return_type)
        params_str = ', '.join([self.__generate_command_param(param) for param in command.params])

        return f'GLAPI {return_type_str} GLCALLCONV {command.name}({params_str});'

    def __generate_command_return_type(self, return_type):
        return f'{"const " if return_type.is_const else ""}{return_type.name}{"*" if return_type.is_pointer else ""}'

    def __generate_command_param(self, param):
        if param.is_void:
            return f'{"const " if param.is_const else ""}void{"*"*param.pointer_indirection} {param.name}'
        else:
            return f'{"const " if param.is_const else ""}{param.data_type}{"*"*param.pointer_indirection} {param.name}'

    def __collect_features(self, api, number):
        features = []
        feature_by_number = self.__feature_by_api_number[api]
        numbers = self.__available_api_numbers[api]

        for i in range(len(numbers)):
            feature = feature_by_number[numbers[i]]
            features.append(feature)

            if numbers[i] == number:
                break

        return features

    def __create_feature_by_api_number_dict(self, feature_list):
        feature_by_api_number = {}
        for feature in feature_list:
            api = feature.api
            number = feature.number

            feature_by_number = None
            if api not in feature_by_api_number:
                feature_by_number = {}
                feature_by_api_number[api] = feature_by_number
            else:
                feature_by_number = feature_by_api_number[api]

            feature_by_number[number] = feature

        return feature_by_api_number

    def __check_api_number(self, api, number):
        if api not in self.__available_api_numbers:
            raise Exception(f"{api} not in {self.__available_api_numbers}")

        numbers = self.__available_api_numbers[api]
        if number not in numbers:
            raise Exception(f"version number {number} not available in {numbers} for api {api}")
