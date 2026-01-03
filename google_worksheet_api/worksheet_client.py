import gspread
from google.oauth2.service_account import Credentials


scopes = ["https://www.googleapis.com/auth/spreadsheets",
           "https://www.googleapis.com/auth/drive"]

creds = Credentials.from_service_account_file("credentials.json",
     scopes=scopes)

gc = gspread.authorize(creds)

sheet = gc.open("NomePlanilha")

worksheet = sheet.worksheet("Página1")
values = worksheet.get_all_values()
print(values)

worksheet.append_row(["Joao", 1])
