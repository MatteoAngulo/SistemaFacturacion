import requests
from io import BytesIO

class ApiConnector:
    def __init__(self) -> None:
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer sk_9IFgOiaSQhL9I8B52nPypY5l1xpWGyFH',
            'Accept-Language': 'es-ES'
        }
        self.url = 'https://invoice-generator.com/'

    def connect_to_api_and_save_invoice_pdf(self, from_who, to_who, logo, number, date, due_date, items, notes, terms, tax, discounts) -> BytesIO:
        invoice_parsed = {
            'from': from_who,
            'to': to_who,
            'logo': logo,
            'number': number,
            'currency': 'COP',
            'date': date,
            'due_date': due_date,
            'items': items,
            'fields': {"tax": "%", "discounts": "%", "shipping": False},
            'discounts': discounts,
            'tax': tax,
            'notes': notes,
            'terms': terms
        }

        request = requests.post(self.url, json=invoice_parsed, headers=self.headers)
        if request.status_code == 200 or request.status_code == 201:
            pdf = request.content
            pdf_bytes = BytesIO(pdf)
            return pdf_bytes
        else:
            print("Fail :", request.text)
            return None
