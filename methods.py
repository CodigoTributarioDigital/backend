from nfelib.v4_00 import leiauteNFe_sub as parser
from data.ncm import ncm_db, fecoep
from data.cfop import nat_output_nf,ext_output_nf, nat_devolution_nf, ext_devolution_nf, nat_input_nf, ext_input_nf
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
  nfe_path = "./data/nfe"
  nfc_path = "./data/nfc"
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

def generate_some(year_income):
  if year_income <= 180000:
    return (4.0,0)

  elif year_income >= 180000.01 and year_income<=360000:
    return (7.30, 5940)

  elif year_income >= 360000.01 and year_income <= 720000:
    return (9.5,13860)

  elif year_income >= 720000.01 and year_income <= 1800000:
    return (10.7,22500)

  elif year_income >= 1800000.01 and year_income <= 3600000:
    return (14.3,87300)

  elif year_income >= 3600000.01 and year_income <= 4800000:
    return (19,378000)


def pgda_calculator(cnpj, year_income):
  xml = list_by_cnpj(cnpj)

  tribute_range = 0

  total_i1_nat = 0
  total_i1_ext = 0

  total_i2_i3_nat = 0
  total_i2_i3_ext = 0

  for nf in xml:
    products = nf.infNFe.det
    for value in products:
      
      if value.prod.CFOP in nat_output_nf:
        total_i1_nat+=float(value.prod.vProd)

      elif value.prod.CFOP in ext_output_nf:
        total_i1_ext+=float(value.prod.vProd)

      elif value.prod.CFOP in nat_devolution_nf or value.prod.CFOP in nat_input_nf:
        total_i2_i3_nat+=float(value.prod.vProd)

      elif value.prod.CFOP in ext_devolution_nf or value.prod.CFOP in ext_input_nf:
        total_i2_i3_ext+=float(value.prod.vProd)

  total_nat = total_i1_nat - total_i2_i3_nat
  total_ext = total_i1_ext - total_i2_i3_ext

    
  monthly_income = total_nat + total_ext

  nominal_some, pd = generate_some(year_income)

  effective_some = ((year_income * nominal_some) - pd)/year_income

  final_value = monthly_income * effective_some
  response = {}
  if tribute_range == 1:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":5.5,
              "IRPJ_value": final_value*0.055,
              "CSLL_percent":3.5,
              "CSLL_value": final_value*0.035,
              "Cofins_percent":12.74,
              "Cofins_value": final_value*0.1274,
              "PIS_Pasep_percent":2.76,
              "PIS_Pasep_value": final_value*0.0276,
              "CPP_percent":41.5,
              "CPP_value": final_value*0.415,
              "ICMS_percent":34.0,
              "ICMS_value": final_value*0.34,
              "tribute_range":tribute_range
              }
  elif tribute_range == 2:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":5.5,
              "IRPJ_value": final_value*0.055,
              "CSLL_percent":3.5,
              "CSLL_value": final_value*0.035,
              "Cofins_percent":12.74,
              "Cofins_value": final_value*0.1274,
              "PIS_Pasep_percent":2.76,
              "PIS_Pasep_value": final_value*0.0276,
              "CPP_percent":41.5,
              "CPP_value": final_value*0.415,
              "ICMS_percent":34.0,
              "ICMS_value": final_value*0.34,
              "tribute_range":tribute_range
              }
  elif tribute_range == 3:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":5.5,
              "IRPJ_value": final_value*0.055,
              "CSLL_percent":3.5,
              "CSLL_value": final_value*0.035,
              "Cofins_percent":12.74,
              "Cofins_value": final_value*0.1274,
              "PIS_Pasep_percent":2.76,
              "PIS_Pasep_value": final_value*0.0276,
              "CPP_percent":42.0,
              "CPP_value": final_value*0.42,
              "ICMS_percent":33.5,
              "ICMS_value": final_value*0.335,
              "tribute_range":tribute_range
              }

  elif tribute_range == 4:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":5.5,
              "IRPJ_value": final_value*0.055,
              "CSLL_percent":3.5,
              "CSLL_value": final_value*0.035,
              "Cofins_percent":12.74,
              "Cofins_value": final_value*0.1274,
              "PIS_Pasep_percent":2.76,
              "PIS_Pasep_value": final_value*0.0276,
              "CPP_percent":42.0,
              "CPP_value": final_value*0.42,
              "ICMS_percent":33.5,
              "ICMS_value": final_value*0.335,
              "tribute_range":tribute_range
              }

  elif tribute_range == 5:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":5.5,
              "IRPJ_value": final_value*0.055,
              "CSLL_percent":3.5,
              "CSLL_value": final_value*0.035,
              "Cofins_percent":12.74,
              "Cofins_value": final_value*0.1274,
              "PIS_Pasep_percent":2.76,
              "PIS_Pasep_value": final_value*0.0276,
              "CPP_percent":42.0,
              "CPP_value": final_value*0.42,
              "ICMS_percent":33.5,
              "ICMS_value": final_value*0.335,
              "tribute_range":tribute_range
              }

  elif tribute_range == 6:
    response = {"final_value": final_value, 
              "monthly_income": monthly_income, 
              "effective_some": effective_some,
              "IRPJ_percent":13.5,
              "IRPJ_value": final_value*0.135,
              "CSLL_percent":10,
              "CSLL_value": final_value*0.10,
              "Cofins_percent":28.27,
              "Cofins_value": final_value*0.2827,
              "PIS_Pasep_percent":6.13,
              "PIS_Pasep_value": final_value*0.0613,
              "CPP_percent":42.0,
              "CPP_value": final_value*0.42,
              "ICMS_percent":33.5,
              "ICMS_value": final_value*0.335,
              "tribute_range":tribute_range
              }    
  
  return response





  


