import configparser
from pathlib import Path


def create_base_config():
    conf_fie = Path(__file__).parents[1] / "resources" / "config" / "conf.ini"
    conf_fie.touch()
    in_path = Path(__file__).parents[1] / "resources"
    in_path.mkdir(exist_ok=True)
    out_path = Path(__file__).parents[1] / "resources"
    out_path.mkdir(exist_ok=True)
    changes_path = Path(__file__).parents[1] / "resources" / "changes"
    changes_path.mkdir(exist_ok=True)
    error_file = Path(__file__).parents[1] / "resources" / "errors.txt"

    config = configparser.ConfigParser()
    config['Paths'] = {'Input Folder': f'{in_path.absolute()}',
                       'Output Folder': f'{out_path.absolute()}',
                       'Changes folder': f'{changes_path.absolute()}',
                       'Error File': f'{error_file.absolute()}'}

    with open(conf_fie, 'w') as configfile:
        config.write(configfile)


def read_config(path: Path = Path(__file__).parents[1] / "resources" / "config" / "conf.ini"):
    """Reads configuration from file and returns configparser

    Arguments:
        path {Path} -- [path of config file]

    Returns:
        [configparser] -- [app configuration]
    """
    config = configparser.ConfigParser()

    config.read([path, Path("conf.ini"), Path("config.ini"), Path("config/conf.ini"), Path("config/config.ini")])
    return config


if __name__ == "__main__":
    create_base_config()
    # read_config()
