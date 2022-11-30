import base64, subprocess, argparse, os
from jinja2 import Template

# STATIC VARS
META = '''galaxy_info:
  role_name: {{ role_name }}
  author: author
  description: blank
  platforms:
    - name: Windows
      versions:
        - all
  license: "GPT-2.0"
  min_ansible_version: "2.1"
'''

CI = '''image: public.ecr.aws/ubuntu/ubuntu:20.04_stable

variables:
  GIT_SUBMODULE_STRATEGY: recursive

stages:
  - validate

ansible validate:
  stage: validate
  script:
    - apt-get update
    - apt-get -y install gnupg2
    - DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
    - apt-get -y install software-properties-common
    - DEBIAN_FRONTEND=noninteractive apt install -y sudo git python3-pip
    - pip3 install "ansible-lint"
    - ansible-galaxy collection install community.windows
    - ansible-lint --force-color -p roles/{{ role_name }}
'''

# ACTUAL CLASS
class ansibleRole():

    # INIT
    def __init__(self, roleName=None, command=None, script_dir=None):
        self.roleName = roleName
        self.command = command

    # META FILE TEMPLATING FUNCTION
    def jtemp(self, roleName):
        
        path_meta = f"{ roleName }/roles/{roleName}/meta/main.yml"
        path_ci = f"{ roleName }/.gitlab-ci.yml"

        tem_meta = Template(META).render(role_name=roleName)
        tem_ci = Template(CI).render(role_name=roleName)

        with open(path_meta, "w") as f:
            f.write(tem_meta)
        
        with open(path_ci, "w") as f:
            f.write(tem_ci)


    # CMD ENCODER FUNCTION
    def encodeCommand(self, command):
        if not isinstance(command, str):
            exit()

        else:
            _common_args = ['PowerShell', '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Unrestricted']
            command = command + "| Out-Null"
            command = command.encode('utf-16-le')
            command = bytes.decode(base64.b64encode(command))
            
            toExecute = _common_args + ['-EncodedCommand', command]

            return toExecute


    # ROLE STRUCTURE CREATION
    def createRoleStructure(self, roleName):
        commands = [f"New-Item -ItemType Directory -Name { roleName }/collections",
                    f"New-Item -Name { roleName }/collections/requirements.yml -Value '---' ",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/defaults",
                    f"New-Item -name { roleName }/roles/{ roleName }/defaults/main.yml -Value '---' ",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/files",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/handlers",
                    f"New-Item -Name { roleName }/roles/{ roleName }/handlers/main.yml -Value '---' ",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/meta",
                    f"New-Item -Name { roleName }/roles/{ roleName }/meta/main.yml -Value '---' ",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/tasks",
                    f"New-Item -Name { roleName }/roles/{ roleName }/tasks/main.yml -Value '---' ",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/templates",
                    f"New-Item -ItemType Directory -Name { roleName }/roles/{ roleName }/vars",
                    f"New-Item -Name { roleName }/roles/{ roleName }/vars/main.yml -Value '---' ",
                    f"New-Item -Name { roleName }/playbook.yml -Value '---' ",
                    f"New-Item -Name { roleName }/inventory.ini -Value '---' ",
                    f"new-item -Name { roleName }/README.md -Value '# { roleName }'"]
        


        for command in commands:
            psCommand = self.encodeCommand(command)
            subprocess.run(psCommand)

        # with open(f"{ roleName }/roles/{ roleName }/meta/main.yml", "w") as meta:    
        #     meta.write(META)
            
        self.jtemp(roleName)

# PARSING ARGS
parser = argparse.ArgumentParser()
parser.add_argument('--roleName', dest='roleName', type=str, help='Role name', required=True)
_args = parser.parse_args()
roleName = _args.roleName

# RUNNING PROGRAM WITH PASSED ROLENAME
if __name__ == "__main__":

    # CHECK IF PATH ALREADY EXISTS
    if os.path.exists(roleName):
        print(f"A role named { roleName } already exists!")
        exit(1)

    creator = ansibleRole()
    creator.createRoleStructure(roleName)
