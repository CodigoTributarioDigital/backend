from nfelib.v4_00 import leiauteNFe_sub as parser
import os

nfe_path = "./data/nfe"
nfc_path = "./data/nfc"

def read_xml(path):
  file = parser.parse(path)
  return file

def read_xml_folder(path):
  files = []
  paths = [os.path.join(path, nome) for nome in os.listdir(path)]
  for file_path in paths:
    files.append(read_xml(file_path))
  return files

def read_efd(path):
  with open(path) as f:
    lines = f.readlines()
    f.close()
  return lines
    