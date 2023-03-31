from os.path import exists, isfile
from os import remove as DelFile
from json import loads, dumps
from types import SimpleNamespace
from yaml import safe_load as yamLoad
from configparser import ConfigParser, MissingSectionHeaderError
from icecream import ic

def isfloat(val: str) -> bool:
    if val.isdigit():
        return False
    try:
        res = float(val)
    except:
        return False
    else:
        return True

DEBUG = True

class UniClass:
    def __init__(self, path = '', doPrint = True):
        """
        Tries to load a conf into universal class
            to use it flawlessy with dot and having
            possibility to tab on ipython.
        It will try to load theese type of configs:
            - json
        """
        self.print = doPrint
        if path:
            self.load_file(path)
    
    def load_file(self, path):
        if all([ exists(path),
                 isfile(path)
            ]):
            try:
                content = open(path).read()
            except:
                if self.print: print(f"Could not open {path}")
            
            if self.understand_content(content, path):
                if self.print: print(f"Loading successfull")
            else:
                if self.print: print(f"Impossible to load {path}")

    def understand_content(self, 
                           content: str,
                           path: str,
                           goto: str = ''):
        """
        Will try to understand if file is json, ini
            or something readable
        """
        #JSON
        if (not goto) or goto=='JSON':
            try:
                res = loads(content)
                if self.print: print(f"json spotted!")
                
            except Exception as e:
                pass
            else:
                return self.load_json(content)
        #YAML
        if (not goto) or goto=='YAML':
            try:
                res = yamLoad(content)
                if self.print: print(f"yaml spotted")
            except Exception as e:
                pass
            else:
                return self.load_yaml(res)
        #INI
        if (not goto) or goto=='INI':
            try:
                c = ConfigParser()
                c.read(path)
                if self.print: print(f"INI spotted")
            except MissingSectionHeaderError:
                #maybe just header is not present, try to overcome
                if self.print: print(f"Maybe just missing header for INI, trying...")
                open("tmp_ini.ini", 'w').write(
                    "[default]\n" + content
                )
                return self.understand_content(content, "tmp_ini.ini","INI")
            except Exception as e:
                if goto == 'INI':
                    if self.print: print(f"Nope, no ini file.")
                    #clean
                    DelFile(path)
                    if DEBUG: print(f"Error on understand_content: {e}")
            else:
                #INI file loaded in res, not convert to class obj
                if goto == 'INI':
                    if self.print: print(f"Claning temp file.")
                    #clean
                    DelFile(path)
                return self.load_ini(c)
        
        return False

    def load_ini(self, c):
        """
        configparser is monodimensiona, but ini can have nested
            section, like:
            [section1]
            [section1.subsection1]
            [section1.subsection2]
            Will try to replicate a nested dict starting with this
        configparser translate all in string, will try to convert
            values in int, float, octal, hex, bin, boolean.
        Will convert in dict, than SimpleNameSpace of dump of dict.
        """
    	# let's just start with haveing a dict instead of configparser
        aD = dict()
        for k,v in c.items():
            aD[k] = dict()
            for sk, sv in v.items():
                if sv.isdigit(): sv = int(sv)
                elif isfloat(sv): sv = float(sv)
                elif sv.lower() in ['true', 'false']: 
                    if sv.lower() == 'false':
                        sv = False
                    else:
                        sv = True
                elif isfloat(sv):
                    sv = float(sv)
                
                aD[k][sk] = sv
        
        # now first level key intelligence:
        # key.subkey under key:
        # [key][subkey]

        # list first level key, without "."
        newD = {k:v for k,v in aD.items () if '.' not in k}
        the_others = {k:v for k,v in aD.items() if '.' in k}

        for path, v in the_others.items():
            self.make_path(newD, path.split('.'), v)
        
        res = dict(aD)

        self.conf = loads(dumps(aD), object_hook=lambda d: SimpleNamespace(**d))
        return True

    def lookahead(self, iterable):
        """Pass through all values from the given iterable, augmented by the
        information if there are more values to come after the current one
        (True), or if it is the last value (False).
        """
        # Get an iterator and pull the first value.
        it = iter(iterable)
        last = next(it)
        # Run the iterator to exhaustion (starting from the second value).
        for val in it:
            # Report the *previous* value (more to come).
            yield last, True
            last = val
        # Report the last value.
        yield last, False


    def make_path(self, d: dict, paths: list, v: any) -> None:
        for key,middle in self.lookahead(paths):
            if middle: d = d.setdefault(key, {})
            else: d = d.setdefault(key, v)

    def load_yaml(self, d):
        """
        Abusing of SimpleNameSpace and json loads
        """
        self.conf = loads(dumps(d), object_hook=lambda d: SimpleNamespace(**d))
        return True
    
    def load_json(self, content):
        """
        res is a json to load inside the class.add()
            it will be loaded under self.conf as a 
            simpleNameSpace
        """
        self.conf = loads(content, object_hook=lambda d: SimpleNamespace(**d))
        return True