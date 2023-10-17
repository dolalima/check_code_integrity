import hashlib
import os
import re
import getopt
import sys
import diff

ignore_file = ".ignore"
ignore_patterns = []
service = "nginx"
service_shutdown = False
integrity = True
target = None
default_hash_algorithm = "md5"


class TextColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def load_ignore():
    global ignore_file, ignore_patterns

    with open(ignore_file, "r") as f:
        ignore_patterns = [re.compile(p.replace('*', '.+')) for p in f.read().splitlines()]


def check_service_status(service_name):
    try:
        print(f"show {service_name} service status")

        # Check all the runnung service
        for line in os.popen(f"systemctl status {service_name}.service"):
            services = line.split()
            print(services)
            pass

    except OSError as ose:
        print("Error while running the command", ose)

    pass


def start_service(service_name):
    try:
        # start service
        os.popen(f"sudo systemctl start {service_name}.service")
        print(f"{service_name} service started successfully...")

    except OSError as ose:
        print("Error while running the command", ose)

    pass


def stop_service(service_name):
    try:
        # stop nginx service
        os.popen(f"sudo systemctl stop {service_name}.service")
        print(f"{service_name} service terminated successfully...")

    except OSError as ose:
        print("Error while running the command", ose)

    pass


def check_result(result: bool):
    if result:
        text = TextColors.OKGREEN + "PASSED" + TextColors.ENDC
    else:
        text = TextColors.FAIL + "FAIL" + TextColors.ENDC

    return text


def get_folders(folder):
    if not os.path.exists(folder):
        raise FileNotFoundError(f"the folder '{folder}' net exist.")

    folder_list = []
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if not os.path.isfile(file_path):
            folder_list.append(file_path)
    return folder_list


def get_hash_lib(hash_type="md5"):
    match hash_type:
        case "md5":
            return hashlib.md5()
        case "sha256":
            return hashlib.sha256()
        case "sha1":
            return hashlib.sha1()
        case _:
            raise Exception('hash algoritm not found')






def check_file_by_file(path):
    print('analyse side by site')
    for file in os.listdir(path):
        print(file)

def calc_hash_file(file):
    global ignore_patterns
    hash_md5 = get_hash_lib(default_hash_algorithm)
    if os.path.isfile(file):
        if not any(p.search(file) for p in ignore_patterns):
            with open(file, "rb") as f:
                hash_md5.update(f.read())
    return hash_md5.hexdigest()


def calc_hash_folder(folder):
    global ignore_patterns
    """
    Calcula o MD5 de uma pasta, considerando no cálculo todo o conteúdo, incluindo diretórios e subdiretórios.
  
    Args:
      pasta: O caminho da pasta.
  
    Returns:
      O MD5 da pasta.
    """

    if not os.path.exists(folder):
        raise FileNotFoundError("A pasta '{}' não existe.".format(folder))

    hash_md5 = get_hash_lib(default_hash_algorithm)

    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            if not any(p.search(file_path) for p in ignore_patterns):
                with open(file_path, "rb") as f:
                    hash_md5.update(f.read())

        elif os.path.isdir(file_path):
            if not any(p.search(file_path) for p in ignore_patterns):
                hash_md5_dir = calc_hash_folder(file_path)
                hash_md5.update(hash_md5_dir.encode('UTF-8'))

    return hash_md5.hexdigest()


def main():
    global target, ignore_file, integrity, service, service_shutdown, default_hash_algorithm

    # Remove 1st argument from the
    # list of command line arguments
    argument_list = sys.argv[1:]

    options = "a:cr:f:i:hmo:s:"

    # Long options
    long_options = ["help", "output=", "folder=", "ignore=", 'service=', "hash=", "shutdown"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argument_list, options, long_options)

        hash_check = None

        pasta = None

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--help"):
                print("""
                      Displaying Help\n
                      -a calc md5 from file or directory and use as reference
                      -r input hash code verification
                      -f analyse a group of folder with same code
                      -i input ignore pattern file
                      --hash= choose algorithm lib. DEFAULT=md5
                      """)
                exit(0)

            if currentArgument == "-a":
                target = currentValue

            if currentArgument in ("-r", "--reference"):
                print(f"Code hash reference: {currentValue}")
                hash_check = currentValue

            if currentArgument in ("-f", "--folder"):
                print(f"verify foldes in : {currentValue}")
                pasta = currentValue

            if currentArgument in ("-i", "--ignore"):
                ignore_file = currentValue

            if currentArgument == "--hash":
                default_hash_algorithm = currentValue
                print(f"Using {default_hash_algorithm} hash algorithm")

            if currentArgument in ("-o", "--output"):
                print(f"Enabling special output mode ({currentValue})")

            if currentArgument in ("-s", "--service"):
                service = currentValue

            if currentArgument == "--shutdown":
                service_shutdown = True

        load_ignore()

        if target:
            print(f"Code hash reference: {target}")
            hash_check = calc_hash_folder(target)
            print(f"result: {hash_check}")

        if not hash_check:
            print('hash verification is required, use command -r <HASH> to insert hash string.')
            print('consult command help -h or --help')
            exit(1)

        if pasta:
            pastas = get_folders(pasta)

            for directory in pastas:
                # Calcula o MD5 da pasta
                hash_md5 = calc_hash_folder(directory)

                # Registra integridade
                if hash_check != hash_md5:
                    integrity = False

                # Imprime o hash
                print(f"{directory}\t{hash_md5}\t{check_result(hash_check == hash_md5)}")
                if (hash_check != hash_md5) and target:
                    for file_name, linhas_diferentes in diff.compare_files(directory, target, ignore_patterns):
                        if any(l for l in linhas_diferentes):
                            print("File:", file_name)
                        for line in linhas_diferentes:
                            print("Line:", line)


            if not integrity:
                if service_shutdown:
                    print(f"Same code isn`t integrity the service {service} will shutdown ")
                    stop_service(service)
                print(TextColors.FAIL + "Integrity test fail." + TextColors.ENDC)
                exit(0)
            else:
                print(TextColors.OKGREEN+"Integrity test pass successfully."+TextColors.ENDC)
                if service_shutdown:
                    start_service(service)
                exit(0)

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))


if __name__ == "__main__":
    main()
