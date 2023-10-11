
class Generator:
    def __init__(self, registry):
        self.__registry = registry

        self.__available_api_numbers = {
            'gl' : ['1.0', '1.1', '1.2', '1.3', '1.4', '1.5', '2.0', '2.1', '3.0', '3.1', '3.2', '3.3', '4.0', '4.1', '4.2', '4.3', '4.4', '4.5', '4.6'],
            'gles1' : ['1.0'],
            'gles2' : ['2.0', '3.0', '3.1', '3.2'],
            'glsc2': ['2.0'],
        }

        # index feature list by api, and then, by version number
        self.__feature_by_api_number = self.__create_feature_by_api_number_dict(self.__registry.feature_list)

    def generate(self, api, number):
        self.__check_api_number(api, number)

        print(self.__feature_by_api_number)


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
