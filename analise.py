import hashlib
import os
import re
import getopt,sys

ignore_file = ".ignore"
ignore_patterns = []

class bcolors:
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
    global ignore_file,ignore_patterns
    
    with open(ignore_file, "r") as f:
        ignore_patterns = [re.compile(p) for p in f.read().splitlines()]

def checkServiceStatus(service):
    try:
        print(f"View {service} service status")

        #Check all the runnung service
        for line in os.popen(f"systemctl status {service}.service"):
            services = line.split()
            print(services)
            pass

    except OSError as ose:
        print("Error while running the command", ose)

    pass

def startService(service):
    try:
        #start service
        os.popen(f"sudo systemctl start {service}.service")
        print(f"{service} service started successfully...")

    except OSError as ose:
        print("Error while running the command", ose)

    pass

def stopService(service):
    try:
        #stop nginx service
        os.popen(f"sudo systemctl stop {service}.service")
        print(f"{service} service terminated successfully...")

    except OSError as ose:
        print("Error while running the command", ose)

    pass

def check_result(result):
    text = ""

    if result == True:
        text = bcolors.OKGREEN+"PASSED"+bcolors.ENDC
    else:
        text = bcolors.FAIL+"FAIL"+bcolors.ENDC

    return text


def get_pastas(pasta):
    if not os.path.exists(pasta):
        raise FileNotFoundError("A pasta '{}' não existe.".format(pasta))

    lista = []
    for arquivo in os.listdir(pasta):
        caminho_arquivo = os.path.join(pasta, arquivo)
        if not os.path.isfile(caminho_arquivo):
            lista.append(caminho_arquivo)
    return lista
    

def calcular_md5_pasta(pasta):

    global ignore_patterns
    """
    Calcula o MD5 de uma pasta, considerando no cálculo todo o conteúdo, incluindo diretórios e subdiretórios.
  
    Args:
      pasta: O caminho da pasta.
  
    Returns:
      O MD5 da pasta.
    """
  
    if not os.path.exists(pasta):
      raise FileNotFoundError("A pasta '{}' não existe.".format(pasta))
    
  
    hash_md5 = hashlib.md5()
  
    for arquivo in os.listdir(pasta):
      caminho_arquivo = os.path.join(pasta, arquivo)      
      if os.path.isfile(caminho_arquivo):
        if not any(p.search(caminho_arquivo) for p in ignore_patterns):
            with open(caminho_arquivo, "rb") as f:                
                hash_md5.update(f.read())
  
      elif os.path.isdir(caminho_arquivo):
        if not any(p.search(caminho_arquivo) for p in ignore_patterns):            
            hash_md5_dir = calcular_md5_pasta(caminho_arquivo)
            hash_md5.update(hash_md5_dir.encode('UTF-8'))

  
    return hash_md5.hexdigest()


def main():    
    global ignore_file

    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    options = "cr:f:i:hmo:"

    # Long options
    long_options = ["help", "output=","folder=","ignore="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)        

        hash_check=None

        pasta=None;       

        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--help"):
                print("""
                      Displaying Help\n
                      -r input hash code verification
                      -f analyse a gruop of folder with same code
                      -i input ignore pattern file
                      """)
                exit(0)

            if currentArgument in ("-r", "--reference"):
                print(("Code hash reference: %s") % (currentValue))
                hash_check = currentValue

            if currentArgument in ("-f", "--folder"):
                print(("verify foldes in : %s") % (currentValue))
                pasta = currentValue

            if currentArgument in ("-i", "--ignore"):                
                ignore_file = currentValue

            elif currentArgument in ("-m", "--My_file"):
                print("Displaying file_name:", sys.argv[0])

            elif currentArgument in ("-o", "--output"):
                print(("Enabling special output mode (%s)") % (currentValue))


        load_ignore()

        if not hash_check:
            print('hash verication is required, use command -r <HASH> to insert hash string.')
            print('consult command help -h or --help')
            exit(1)

        pastas = get_pastas(pasta)

        for directory in pastas:

            # Calcula o MD5 da pasta
            hash_md5 = calcular_md5_pasta(directory)

            # Imprime o MD5
            print(f"{directory}\t{hash_md5}\t{check_result(hash_check == hash_md5)}")

    except getopt.error as err:
        # output error, and return with an error code
        print(str(err))


if __name__ == "__main__":
  main()