# Swift Bridging Header Generator

### Intro
This tool allows to generate bridging header by including all h-files of Objective C project. For some reasons it could be useful to make visible whole Objective C code base during migrating to Swift. It looks like a trivial issue when you working on small project with a few dozens of files. But everything changes when your projects consists of thousand of classes. In this case developer should manually provide required header file into bridging for every particular case.

### Usage
There are two ways to start script. The first one allows you to enter all required parameters in command prompt:
```
python sbh-generator.py <options>
```

Available options:
Option              | Description
------------------- | -------------
--root=\<path\>     | Optional, specifies path to project root folder. Default is current folder
--product=\<name\>  | Required, *name* will used to generate title of bridging header as *name*-Bridging-Header.h and for generating. Could be overridden with --filename option
--output=\<path\>   | Optional, specifies path to result bridging header. Default is current folder
--filename=\<name\> | Optional, use this option to force assign output file name
--author=\<name\>   | Optional. Use to provide *name* as author in comment into output file. Default is __Swift Bridging Header Generator__

The second way allows you provide parameters as file in JSON format. Usage:
```
python sbh-generator.py --config=<path_to_file>
```
JSON keys are the same such as a parameters for command prompt. The advantage of this way parameter *exclude* which doesn't provided for command prompt. The *exclude* allows you to set list of folders to avoid processing their content. For example, configuration file could be next:
```
{
    "product": "SuperProject",
    "root": "/Users/john.smith/SuperProject",
    "author": "John Smith",
    "output": "/Users/john.smith/SuperProject",
    "exclude": ["libs", "build"]
}
```

### Notes
Also please pay attention to next points:
* You should use this tool at your own risk. Make a copy of critical data before you start.
* Your project could be broken because of presence of header files which are not registered into project.pbxproj. This tool will include such headers and you will receive compiler error that included file not found. It could be a good start point to clear your project from unused files.
* Your project could be broken with compile errors like a `No 'assign', 'retain', or 'copy' attribute is specified - 'assign' is assumed`. In fact you should provide property attribute explicitly. For example, your old code
```
@interface Employee : NSObject
@property(nonatomic) int serverId;
@property(nonatomic) NSString *name;
@property(nonatomic) NSDecimalNumber *salary;
@end
```
should be transformed to
```
@interface Employee : NSObject
@property(nonatomic) int serverId;
@property(nonatomic, strong) NSString *name;
@property(nonatomic, storng) NSDecimalNumber *salary;
@end
```
* Existing bridging file will be overwritten