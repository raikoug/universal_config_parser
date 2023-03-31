# Universal config Parser
## Actually accepted formats
### Json
Json is almost compatible by default.
### YAML
Perfectly compatible
### INI
configparser structure is compatible, and nested sections are available:
```ini
[section]
someValue=1
[section.subsection]
someValue=2
```
Will become:
```python
section.subsection.someValue
>> 2
```

## ToDO
All the parser to understand dates, octal, hex, bin where this types are not fully comprehended.  
In INI files there is already a boolean, integer and float parser, more to come.

# Examples
YAML and JSON can lead to the same configuration.  
INI, given the lack oif structure, can't.  

Using the examples files (sample_data.{format}):

```python
from universal_class import UniClass as U

json_conf = U('sample_data.json')
yaml_conf = U('sample_data.yaml')
ini_conf = U('sample_data.ini')

json_conf.conf.key1.key1_2[1].id
>> 2
yaml_conf.conf.key1.key1_2[1].id
>> 2
ini_conf.conf.section.nested.value
>> 'nested'

```

