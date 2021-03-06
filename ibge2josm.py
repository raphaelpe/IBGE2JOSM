#!/usr/bin/env python

"""ibge2josm.py: a small python app that converts IBGE data for JOSM"""

__author__ = 'Igor Eliezer'
__copyright__ = "Copyright 2018-2019"
__date__ = '2019/03/14'
__status__ = "Production"

# This software is provided "AS-IS" without any express or implied warranty, in the hope that it will be useful.
# Contact the author for any question!

# Imports
import re
import os
from tkinter import Tk
from tkinter import filedialog

# Messages
print("\n=========== IBGE2JOSM ===========")
print("Programa que converte dados do IBGE/CNEFE para usar no JOSM.")
print("Criado por: " + __author__ + " Arquiteto e Urbanista (igoreliezer.com)")
print("Data: " + __date__)
print("\nInstruções")
print("  1. Após teclar ENTER, selecione um arquivo TXT com dados do IBGE/CNEFE.")
print("  * Codificações suportadas: UTF-8 ou ANSI/Windows 1250.")
print("  2. Informe o tipo de lista de endereços do arquivo txt selecionado.")
print("  3. O programa irá tentar convertê-lo em arquivo CVS formatado para o JOSM.")
print("  * JOSM requer o plug-in OpenData.")
print("  4. O arquivo CVS será salvo com o mesmo nome na mesma pasta do arquivo TXT.")
input("\nTecle ENTER para prosseguir: ")


# FUNCTIONS
def select_file():
    """
Select file
    :return: string
    """
    print("Selecionando arquivo...")
    Tk().withdraw()
    cwd = "/"
    filename = filedialog.askopenfilename(initialdir=cwd, title="Selecione um arquivo para converter",
                                          filetypes=(("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")))
    return filename


def dms(coord):
    """
Format DMS list (00 00 00 O) into DMS string with symbols ("00° 00' 00" W).
    :param coord: list
    :return: string
    """
    d = coord[0]
    m = coord[1]
    s = coord[2]
    c = coord[3]
    if c == 'O':
        c = 'W'
    return d + '° ' + m + '\' ' + s + '" ' + c


def dms2dd(coord):
    """
Convert DMS list (00 00 00 O) to decimal coord string ("-00.000000...").
    :param coord: list
    :return: string
    """
    d = coord[0]
    m = coord[1]
    s = coord[2]
    return '-' + str(float(d) + float(m) / 60 + float(s) / 3600)


def fixedwidth2list(line):
    """
Convert fixed width line string from a file into list.
    :param line: string
    :return: list
    """
    # cod,log,titulo,nome,num,c1,c2,c2_num,c3,c3_num,c4,c4_num,DMS_lat,DMS_lon,lat,lon,localidade,desc1,desc2,cep
    data = [line[0:15], line[16:36], line[36:66], line[66:129], line[129:134], line[134:141], line[141:161],
            line[161:171], line[171:191], line[191:201], line[201:221], line[221:321], line[321:336],
            line[336:351], line[351:471], line[473:513], line[513:544], line[544:]]
    data = [item.strip() for item in data]
    data = [item.title() for item in data]
    name = ' '.join(data[1:4])  # merge [log+titulo+nome]->name
    data = [data[0]] + [' '.join(name.split())] + data[4:]  # ...+[remove double white spaces]+...
    return data


# EXECUTION
file = select_file()

if file:
    option = input("\nInforme o tipo de lista de endereços para conversão:\n"                   
                   "  1 = Por distrito/subsdistrito\n"
                   "  2 = Por setor censitário\n"
                   "  ENTER ou qualquer tecla = sair\n\n"
                   "Entre a opção: ")

# Por distrito/subsdistrito
if option == '1' and file:
    # select and generate the header
    f = open(file, 'r', encoding='windows-1250')
    file_out = os.path.splitext(file)[0] + '.csv'
    f_out = open(file_out, 'w', encoding="utf-8")
    f_out.write('cod,log,num,c1,c2,c2_num,c3,c3_num,c4,c4_num,DMS_lat,DMS_lon,lat,lon,localidade,desc1,desc2,cep,place')

    # File 1 to file 2
    ct = 0
    for line in f:
        data = fixedwidth2list(line)
        lat = data[10].split(' ')
        lon = data[11].split(' ')
        if len(lat) == len(lon) == 4:
            line_out = ','.join(data[0:10] + [dms(lat)] + [dms(lon)] + [dms2dd(lat)] + [dms2dd(lon)] + data[12:])
            f_out.write('\n' + line_out + ',isolated_dwelling')
            ct += 1

# Por setor censitário
elif option == '2' and file:
    # select and try to read the header
    try:
        f = open(file, 'r', encoding='utf-8')
        header = f.readline().split(';')
    except UnicodeDecodeError:
        f = open(file, 'r', encoding='windows-1250')
        header = f.readline().split(';')

    # File 2 - create and write the header
    file_out = os.path.splitext(file)[0] + '.csv'
    f_out = open(file_out, 'w', encoding="utf-8")
    f_out.write(','.join(header[0:5] + ['DMS_lat', 'DMS_lon', 'lat', 'lon'] + header[7:16] + ['place\n']))

    # File 1 to file 2
    ct = 0
    for line in f:
        if not re.match('\'C', line):  # must not start with '
            data = line.split(';')
            lat = data[5].split(' ')
            lon = data[6].split(' ')
            if len(lat) == len(lon) == 4:
                line_out = ','.join(data[0:5] + [dms(lat)] + [dms(lon)] + [dms2dd(lat)] + [dms2dd(lon)] + data[7:16] + [
                    'isolated_dwelling\n'])
                f_out.write(line_out)
                ct += 1

else:
    print('Nada foi feito.')

if option in ['1', '2'] and file:
    # Close files
    print("\nGerou " + str(ct) + " linhas.")
    f.close()
    f_out.close()
    # Finish
    print("Salvo em: " + file_out)

input("\nTecle ENTER para sair: ")
