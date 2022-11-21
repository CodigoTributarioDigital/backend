from nfelib.v4_00 import leiauteNFe_sub as parser
from data.ncm import ncm_db
import os

# Retorna um xml
def read_xml(path):
  return parser.parse(path)

# Retorna um array onde cada elemento é um xml
# Usar paths diferentes para pegar os dois datasets
def read_xml_folder(path):
  files = []
  paths = [os.path.join(path, nome) for nome in os.listdir(path)]
  for file_path in paths:
    files.append(read_xml(file_path))
  return files

# Retorna um array onde cada elemento é uma linha da EFD
def read_efd(path):
  with open(path) as f:
    lines = f.readlines()
    f.close()
  return lines

# Retorna um array com xmls relacionados ao cnpj informado
def list_by_cnpj(cnpj):
  nfe_path = "./data/nfe"
  nfc_path = "./data/nfc"
  validated_nf = []
  nfes = read_xml_folder(nfe_path)
  nfcs = read_xml_folder(nfc_path)

  for xml in nfes:
    if xml.infNFe.emit.CNPJ == cnpj:
      validated_nf.append(nfes)

  for xml in nfcs:
    if xml.infNFe.emit.CNPJ == cnpj:
      validated_nf.append(nfcs)

  return validated_nf

def list_filtered(cnpj, month, year):
  validated_nf = list_by_cnpj(cnpj)
  filtered_nfs=[]
  for xml in validated_nf[0]:
    xml_date = xml.infNFe.ide.dhEmi
    
    if year == xml_date[:4] and month == xml_date[5:7]:
      aux = {"key":xml.infNFe.Id,
             "date": xml_date, 
             "emit":xml.infNFe.emit.xNome, 
             "dest":xml.infNFe.dest.xNome, 
             "value":xml.infNFe.total.ICMSTot.vNF}
      filtered_nfs.append(aux)

  return filtered_nfs

def get_aliquotas_values(ncm):
  if ncm_db[f"{ncm}"]:
    return ncm_db[f"{ncm}"]
  else:
    return 17