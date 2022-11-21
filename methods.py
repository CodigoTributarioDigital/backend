from nfelib.v4_00 import leiauteNFe_sub as parser
from data.ncm import ncm_db, fecoep
from data.cfop import output_nf, devolution_nf, input_nf
import os

def remove_items(test_list, item):
    # using list comprehension to perform the task
    res = [i for i in test_list if i != item]
 
    return res

# Retorna um xml
def read_xml(path):
  return parser.parse(path, silence=True)

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
  nfe_path = "./data/big_nfe"
  nfc_path = "./data/big_nfc"
  validated_nf = []
  nfes = read_xml_folder(nfe_path)
  nfcs = read_xml_folder(nfc_path)

  for xml in nfes:
    if xml.infNFe.emit.CNPJ == cnpj:
      validated_nf.append(xml)

  for xml in nfcs:
    if xml.infNFe.emit.CNPJ == cnpj:
      validated_nf.append(xml)

  return validated_nf

def list_filtered(cnpj, month, year):
  validated_nf = list_by_cnpj(cnpj)
  filtered_nfs=[]
  for xml in validated_nf:
    xml_date = xml.infNFe.ide.dhEmi
    
    if year == xml_date[:4] and month == xml_date[5:7]:
      aux = {"key":xml.infNFe.Id,
             "type":xml.infNFe.ide.mod,
             "date":xml_date, 
             "emit":xml.infNFe.emit.xNome, 
             "dest":xml.infNFe.dest.xNome, 
             "value":xml.infNFe.total.ICMSTot.vNF}
      filtered_nfs.append(aux)

  return filtered_nfs

def get_some_value(ncm):
  if ncm_db[ncm]:
    if ncm_db[ncm] in fecoep:
      return (ncm_db, 2)
    return (ncm_db[ncm], None)
  else:
    return (17, None)

def verify_efd(cnpj, efd):
  efd_array = read_efd(efd)

  access_codes = []
  for value in efd_array:
    actual_line = value.split('|')
    actual_line = remove_items(actual_line, '')
    actual_line = remove_items(actual_line, '\n')
    
    # print(actual_line)
    if actual_line[0] == "C100":
      access_codes.append(actual_line[8])
    if actual_line[0] == "0000":
      month = actual_line[3][2:4]
      year = actual_line[3][4:8]

  filtered = list_filtered(cnpj, month, year)
  
  miss = []

  for value in filtered:
    value["key"] = value["key"].replace("NFe","")
    if value["key"] not in access_codes:
      miss.append(value)
  
  return miss

def pgda_calculator(cnpj):
  xml = list_by_cnpj(cnpj)

  total_i1 = 0
  total_i2_i3 = 0

  i1 = []
  i2 = []
  i3 = []

  for nf in xml:
    products = nf.infNFe.det
    for value in products:
      
      if value.prod.CFOP in output_nf:
        total_i1+=float(value.prod.vProd)
        aux = {"key":nf.infNFe.Id,
                "type":nf.infNFe.ide.mod,
                "date":nf.infNFe.ide.dhEmi, 
                "emit":nf.infNFe.emit.xNome, 
                "dest":nf.infNFe.dest.xNome, 
                "value":nf.infNFe.total.ICMSTot.vNF}
        i1.append(aux)

      elif value.prod.CFOP in devolution_nf:
        total_i2_i3+=float(value.prod.vProd)
        aux = {"key":nf.infNFe.Id,
                "type":nf.infNFe.ide.mod,
                "date":nf.infNFe.ide.dhEmi, 
                "emit":nf.infNFe.emit.xNome, 
                "dest":nf.infNFe.dest.xNome, 
                "value":nf.infNFe.total.ICMSTot.vNF}
        i2.append(aux)

      elif value.prod.CFOP in input_nf:
        total_i2_i3+=float(value.prod.vProd)
        aux = {"key":nf.infNFe.Id,
                "type":nf.infNFe.ide.mod,
                "date":nf.infNFe.ide.dhEmi, 
                "emit":nf.infNFe.emit.xNome, 
                "dest":nf.infNFe.dest.xNome, 
                "value":nf.infNFe.total.ICMSTot.vNF}
        i3.append(aux)
  
  total = total_i1 - total_i2_i3

  return {"total": total, "i1": i1, "i2": i2, "i3": i3 }


print(pgda_calculator('42602001413603'))