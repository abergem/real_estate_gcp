'''Exports all env vars in env_vars.yaml
Only for running the main script locally'''

import yaml
import os

def export_env_vars():
    file = 'env_vars.yaml'
    try:
        with open(file, 'r') as yamlfile:
            env_vars = yaml.safe_load(yamlfile)
    except:
        os.chdir(os.path.join(os.getcwd(), r'path/to/dir'))
        with open(file, 'r') as yamlfile:
            env_vars = yaml.safe_load(yamlfile)

    for name, value in env_vars.items():
        os.environ[name] = value

if __name__ == '__main__':
    export_env_vars()
    