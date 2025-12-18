import sys
from ..repo import repo_find
from ..config import read_config, write_config
 
def cmd_config(args):
    repo = repo_find()
    config = read_config(repo)
    
    if len(args) == 0:
        for section in config.sections():
            for key, val in config.items(section):
                print(f"{section}.{key}={val}")
        return
 
    key = args[0]
    if "." not in key:
        print("error: key does not contain a section: {}".format(key))
        sys.exit(1)
        
    section, option = key.split(".", 1)
    
    if len(args) == 2:
        # Set
        value = args[1]
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, option, value)
        write_config(repo, config)
    else:
        # Get
        if config.has_option(section, option):
            print(config.get(section, option))
        else:
            sys.exit(1)