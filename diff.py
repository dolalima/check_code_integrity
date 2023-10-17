import os
import sys
import difflib

def compare_files(pasta1, pasta2, ignore_patterns = []):
    """
    Compara os arquivos de duas pastas, incluindo os arquivos em subpastas.

    Args:
      pasta1: Pasta 1.
      pasta2: Pasta 2.

    Returns:
      Uma lista de tuplas, onde cada tupla contém o nome do arquivo, o número da linha e o texto da diferença.
    """

    arquivos_diferentes = []

    for pasta, subpastas, arquivos in os.walk(pasta1):

        for arquivo in arquivos:

            path_file_1 = os.path.join(pasta, arquivo)
            path_file_2 = os.path.join(pasta2 + (pasta[len(pasta1):]), arquivo)

            if not any(p.search(path_file_1) for p in ignore_patterns):

                if os.path.isfile(path_file_1) and os.path.isfile(path_file_2):
                    linhas_diferentes = difflib.unified_diff(
                        open(path_file_1).readlines(),
                        open(path_file_2).readlines(),
                        fromfile=path_file_1,
                        tofile=path_file_2,
                        n=0)

                    if linhas_diferentes:
                        arquivos_diferentes.append((arquivo, linhas_diferentes))

                if os.path.isfile(path_file_1) and not os.path.isfile(path_file_2):
                    arquivos_diferentes.append((arquivo, [f'not found {path_file_2}']))


    return arquivos_diferentes


def main():
    """
    Main program
    """

    argument_list = sys.argv[1:]

    if not argument_list[0]:
        pasta1 = input("Digite o caminho da pasta 1: ")
    else:
        pasta1= argument_list[0]

    if not argument_list[1]:
        pasta2 = input("Digite o caminho da pasta 2: ")
    else:
        pasta2 = argument_list[1]

    arquivos_diferentes = compare_files(pasta1, pasta2)

    for arquivo, linhas_diferentes in arquivos_diferentes:
        print("File:", arquivo)
        for linha in linhas_diferentes:
            print("Line:", linha)


if __name__ == "__main__":
    main()