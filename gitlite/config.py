import configparser
 
def get_config_path(repo):
    return repo.gitdir / "config"
 
def read_config(repo):
    config = configparser.ConfigParser()
    path = get_config_path(repo)
    if path.exists():
        config.read(path)
    return config
 
def write_config(repo, config):
    path = get_config_path(repo)
    with open(path, "w") as f:
        config.write(f)