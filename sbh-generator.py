import sys
import os
import getopt
import datetime
import json

# -------------------------------------------------------------------------
# Utils
# -------------------------------------------------------------------------
def str_join(str_list: list, separator: str =" ") -> str:
    if str_list == None:
        return None
    count = len(str_list)    
    output = ""
    if count == 0:
        return output
    else:
        output = str_list[0]
    for i in range(1, count):
        output = "{0}{1}{2}".format(output, separator, str_list[i])
    return output


# -------------------------------------------------------------------------
# Shared Configuration
# -------------------------------------------------------------------------
class Configuration:
    ROOT_PATH = "root"
    PRODUCT = "product"
    EXCLUDE = "exclude"
    AUTHOR = "author"
    OUTPUT_PATH = "output"
    CUSTOM_FILENAME = "filename"

    def __init__(self):
        self.__product = None
        self.__custom_file_name = None
        self.__root_path = '.'
        self.__output_path = '.'
        self.__exclude = None
        self.__author = "Swift Bridging Header Generator"

    def apply_parameters(self, parameters: dict):
        if Configuration.PRODUCT in parameters:
            self.__product = parameters[Configuration.PRODUCT]
        if Configuration.ROOT_PATH in parameters:            
            self.__root_path = parameters[Configuration.ROOT_PATH]
        if Configuration.EXCLUDE in parameters:
            self.__exclude = parameters[Configuration.EXCLUDE]
        if Configuration.AUTHOR in parameters:
            self.__author = parameters[Configuration.AUTHOR]
        if Configuration.OUTPUT_PATH in parameters:
            self.__output_path = parameters[Configuration.OUTPUT_PATH]
        if Configuration.CUSTOM_FILENAME in parameters:
            self.__custom_file_name = parameters[Configuration.CUSTOM_FILENAME]

    def parameters_from_file(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
            self.apply_parameters(data)        

    @property
    def product(self) -> str:
        return self.__product

    @product.setter
    def product(self, newValue):
        self.__product = newValue

    @property
    def exclude_folders(self) -> list:
        return self.__exclude

    @property
    def root_path(self) -> str:
        return self.__root_path

    @root_path.setter
    def root_path(self, newValue):
        self.__root_path = newValue

    @property
    def author(self) -> str:
        return self.__author

    @author.setter
    def author(self, newValue):
        self.__author = newValue

    @property
    def output_path(self) -> str:
        return self.__output_path

    @output_path.setter
    def output_path(self, newValue):
        self.__output_path = newValue

    @property
    def custom_file_name(self) -> str:
        return self.__custom_file_name

    @custom_file_name.setter
    def custom_file_name(self, newValue):
        self.__custom_file_name = newValue

    @property
    def output_file_name(self) -> str:
        file_name = self.custom_file_name
        if file_name == None:
            file_name = "{0}-Bridging-Header.h".format(self.product)
        return file_name

    @property
    def fullpath_output_file(self) -> str:
        return os.path.join(self.output_path, self.output_file_name)

    @property
    def is_valid(self) -> bool:
        return self.product != None and self.root_path != None


class OptKey:
    def __init__(self, name: str, is_value: bool = True):
        self.__name = name
        self.__is_value = is_value
    
    def is_equal(self, key: str) -> bool:
        if self.__name == key:
            return True
        # try to skip "--"
        if len(key) > 2:
            return key[2:] == self.__name
        return False

    @property
    def opt_list_name(self) -> str:
        return self.__name if not self.__is_value else self.__name + "="

# -------------------------------------------------------------------------
# Processing
# -------------------------------------------------------------------------
def is_c_header_file(file_path:str) -> bool:
    if len(file_path) < 2:
        return False
    return file_path[-2:] == ".h"


def scan_files(configuration: Configuration) -> list:
    root = configuration.root_path
    exclude = set()
    if configuration.exclude_folders != None:
        for folder in configuration.exclude_folders:
            path = os.path.join(root, folder)
            exclude.add(path)
    headers = []
    repeating = {}
    folders = [root]        
    bridge_file = configuration.output_file_name
    while len(folders) > 0:
        folder = folders.pop(0)            
        for elem in os.listdir(folder):
            full_path = os.path.join(folder, elem)
            if os.path.isdir(full_path):
                if full_path not in exclude:
                    folders.append(full_path)
            elif is_c_header_file(full_path):
                if elem == bridge_file:
                    continue
                headers.append((elem, full_path))
                count = 0 if elem not in repeating else repeating[elem]
                repeating[elem] = count + 1
    root_len = len(root)        
    headers = list(map(lambda item: item[0] if repeating[item[0]] == 1 else ".." + item[1][root_len:], headers))
    return headers


def generate_bridge(configuration: Configuration, header_list: list) -> bool:
    if len(header_list) == 0:
        return False
    with open(configuration.fullpath_output_file, "w") as file:
        include_guard_name = "{0}_Bridging_Header".format(configuration.product)
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        file_header = str_join([
            "//",
            "// Created by {0} on {1}".format(configuration.author, current_date),
            "//",
            "",
            "#ifndef {0}".format(include_guard_name),
            "#define {0}".format(include_guard_name),
            "",
        ], "\n")
        file.write(file_header)            
        for elem in header_list:                
            file.write("#import \"{0}\"\n".format(elem))

        file_footer = str_join([                
            "",
            "#endif"
        ], "\n")
        file.write(file_footer)
        file.close()      
        return True
    return False      

# -------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------
def print_short_usage():
    print("You did something wrong.\nUse --help for details")

def option_description_str(option: str, description: str) -> str:
    return "\t{0:<20} {1}".format(option, description)

def print_help():
    arr = [        
        "Usage:",
        "python sbh-generator.py <options>",
        "",
        "Options:",
        option_description_str("--root=<path>", "Optional, specifies path to project root folder. Default is current folder"),
        option_description_str("--product=<name>", "Required, name will used to generate title of bridging header and for generating"),
        option_description_str("--output=<path>", "Optional, specifies path to result bridging heaer. Default is current folder"),
        option_description_str("--filename=<name>", "Optional, use this option to force assign output file name"),
        option_description_str("--author=<name>", "Optional. Use to provide name as author in comment into output file"),
        option_description_str("--config=filename", "Generate bridging header with parameters from file"),
        option_description_str("--help", "Show this help"),
        "",
        "See github page for more details:",
        "https://github.com/SergeyChelak/swift-bridging-header-generator"
    ]
    output = str_join(arr, "\n")
    print(output)


def launch(configuration: Configuration):
    if not configuration.is_valid:
        print("Invalid configuration")
        return
    headers = scan_files(configuration)
    print("{0} header(s) found".format(len(headers)))
    result = generate_bridge(configuration, headers)
    print("Bridging header created" if result else "Unable to create proper bridging header")


def main(args: list):
    if len(args) == 1:
        print_short_usage()
        return
    key_config = OptKey("config")
    key_help = OptKey("help", False)
    key_root = OptKey(Configuration.ROOT_PATH)
    key_output = OptKey(Configuration.OUTPUT_PATH)
    key_author = OptKey(Configuration.AUTHOR)
    key_custom_output_file = OptKey(Configuration.CUSTOM_FILENAME)
    keys = list(map(lambda key: key.opt_list_name, [
        key_config, 
        key_help, 
        key_root,
        key_author,
        key_output,
        key_custom_output_file
    ]))
    options, _ = getopt.getopt(args[1:], "", keys)
    is_distinct = len(options) == 1
    is_error = False
    configuration = Configuration()
    for option in options:
        key, value = option
        if key_help.is_equal(key):
            if is_distinct:
                print_help()
                return
            else:
                is_error = True
                break
        elif key_config.is_equal(key):
            if is_distinct:
                configuration.parameters_from_file(value)
            else:
                is_error = True
        elif key_root.is_equal(key):
            configuration.root_path = value
        elif key_output.is_equal(key):
            configuration.output_path = value
        elif key_author.is_equal(key):
            configuration.author = value
        elif key_custom_output_file.is_equal(key):
            configuration.custom_file_name = value
        else:
            is_error = True
    if is_error:
        print_short_usage()
        return
    launch(configuration)


if __name__ == "__main__":
    print("Swift Bridging Header Generator, version 0.1")
    #main(sys.argv)
    try:
        main(sys.argv)
    except Exception as err:
        print("Error:", err)
        print_short_usage()
        sys.exit(1)
