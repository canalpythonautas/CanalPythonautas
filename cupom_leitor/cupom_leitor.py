import cv2
import requests
import sys
from pprint import pprint
from bs4 import BeautifulSoup


if len(sys.argv) < 2:
    print("ERRO: Informe o arquivo de cupom fiscal. Ex:")
    print("\t$ cupom_leitor.py cupom_fiscal.jpeg")
    exit()

filename = sys.argv[1]
print(f"Processando arquivo: {filename}")

img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

_, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

detector = cv2.QRCodeDetector()

data, bbox, _ = detector.detectAndDecode(img)

if not data:
    print("QR Code nao detectado")
    exit()

print(data)

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
