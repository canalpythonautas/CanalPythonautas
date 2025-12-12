from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from zxingcpp import read_barcodes, BarcodeFormat
import requests
from bs4 import BeautifulSoup

app = FastAPI()


@app.post("/processar-cupom")
async def processar_cupom(imagem: UploadFile = File(...)):
    conteudo = await imagem.read()

    img_arr = np.frombuffer(conteudo, np.uint8)
    img = cv2.imdecode(img_arr, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise HTTPException(status_code=400, detail="Arquivo inválido ou não é imagem")

    results = read_barcodes(img)

    data = None
    for r in results:
        if r.format == BarcodeFormat.QRCode:
            data = r.text

    if data is None:
        raise HTTPException(status_code=422, detail="Não foi possível encontrar um QRCode válido na imagem")

    result = requests.get(data)
    if result.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro ao acessar URL do QRCode")

    soup = BeautifulSoup(result.text, "html.parser")

    valor_total_elem = soup.find("span", class_="totalNumb txtMax")
    valor_total = valor_total_elem.text.strip() if valor_total_elem else None

    produtos = []
    linhas = soup.select('#tabResult tr')

    for linha in linhas:
        nome = linha.find("span", class_="txtTit")
        quantidade = linha.find("span", class_="Rqtd")
        valor_total_item = linha.find("span", class_="valor")

        if nome:
            produtos.append({
                "nome": nome.text.strip(),
                "quantidade": quantidade.text.replace("Qtde.:", "").strip() if quantidade else None,
                "valor_total": valor_total_item.text.strip() if valor_total_item else None,
            })

    return JSONResponse({
        "valor_total": valor_total,
        "produtos": produtos
    })
