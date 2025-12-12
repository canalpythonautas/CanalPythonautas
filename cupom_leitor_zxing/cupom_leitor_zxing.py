import cv2
import sys
from zxingcpp import read_barcodes, BarcodeFormat
import requests
from pprint import pprint
from bs4 import BeautifulSoup


if len(sys.argv) < 2:
    print("ERRO: Informe o arquivo de cupom fiscal. Ex:")
    print("\t$ cupom_leitor.py cupom_fiscal.jpeg")
    exit()

filename = sys.argv[1]
print(f"Processando arquivo: {filename}")

img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

results = read_barcodes(img)

data = None
for r in results:
    if (r.format == BarcodeFormat.QRCode):
        data = r.text

if data is None:
    print("ERRO: Não foi possível encontrar um QRCode")
    exit()

result = requests.get(data)

if result.status_code != 200:
     print("Nao foi possivel ler a URL: ", data)

content = result.text

content = result.text
soup = BeautifulSoup(content, "html.parser")

valor_total = soup.find("span", class_="totalNumb txtMax").text.strip()

produtos = []
linhas = soup.select('#tabResult tr')
for linha in linhas:
    nome = linha.find("span", class_="txtTit")
    quantidade = linha.find("span", class_="Rqtd")
    valor_total_item = linha.find("span", class_="valor")
    produtos.append({
        "nome": nome.text.strip() if nome else None,
        "quantidade": quantidade.text.replace("Qtde.:", "").strip() if quantidade else None,
        "valor_total": valor_total_item.text.strip() if valor_total_item else None,
    })

print("Valor Total (R$): ", valor_total)
pprint(produtos)
