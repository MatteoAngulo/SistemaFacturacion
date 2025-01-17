import streamlit as st
import pandas as pd
import re
from class_invoice_pdf import ApiConnector
from io import BytesIO

# -------------- SETTINGS --------------

page_title = "Generador de facturas"
page_icon = "💳"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "wide"
peso_symbol = '\u0024'
total_expenses = 0
final_price = 0
df_expense = ""
css = "style/main.css"
file_name_gs = ""
google_sheet = ""
sheet_name = ""
to_email = ""
sender = "Negocio***"
code = ""
scope = ""
csv = "invoices.csv"
logo = "logo valerapp"
file_authentication_gs = "invoice-tool-authentication.json"
google_sheet = "invoice-tool"
sheet_name = "invoices"
# url_logo="https://i.ibb.co/12MHwBs/logo.png"
url_logo = 'https://i.ibb.co/vLFYTZd/Ingemex-Logo.png'

st.set_page_config(
    page_title="Ingemex Facturación",
    page_icon=page_icon,
    layout=layout,
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.instagram.com/ingemexindustrias/',
        'Report a bug': 'https://www.instagram.com/ingemexindustrias/',
        'About': "Interfaz de facturación de ingemex!"
    }
)

hide_st_style = """
  <style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  </style>
  """

st.markdown(hide_st_style, unsafe_allow_html=True)

# --------------- Functions ------------------------

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # r' ' significa cadenas sin formato
    if re.match(pattern, email):
        return True
    else:
        return False


# -------------- Session_state variables --------------

if "first_time" not in st.session_state:
    st.session_state.first_time = ""
if "items" not in st.session_state:
    st.session_state.items_invoice = []

# -------------- Frontend code ----------------

# section invoice info
with st.container():
    cc1, cc2 = st.columns(2)
    cc1.image('https://i.ibb.co/vLFYTZd/Ingemex-Logo.png', caption="Ingemex", width=200)  # "assets/logo.PNG"
    from_who = cc1.text_input("De: *", placeholder="Quién envía esta factura")
    to_who = cc1.text_input("Cobrar a: *", placeholder="Para quién es la factura")
    cc2.subheader("FACTURA")
    num_invoice = cc2.text_input("#", placeholder="Número de factura")
    date_invoice = cc2.date_input("Fecha *")
    due_date = cc2.date_input("Fecha de vencimiento *")

# form for expenses
with st.form("entry_form", clear_on_submit=True):
    if "expense_data" not in st.session_state:
        st.session_state.expense_data = []
    if "invoice_data" not in st.session_state:
        st.session_state.invoice_data = []

    cex1, cex2, cex3 = st.columns(3)
    articulo = cex1.text_input("Articulo", placeholder="Descripción del servicio o producto")
    amount_expense = cex2.number_input("Cantidad", step=1, min_value=1)
    precio = cex3.number_input("Precio", min_value=0, step=50000)
    submitted_expense = st.form_submit_button("Añadir artículo")
    if submitted_expense:
        if articulo == "":
            st.warning("Añade una descripción del artículo o servicio")
        else:
            st.success("Artículo añadido")
            st.session_state.expense_data.append({"Artículo": articulo, "Cantidad": amount_expense, "Precio": precio, "Total": amount_expense * precio})
            st.session_state.invoice_data.append({"name": articulo, "quantity": amount_expense, "unit_cost": precio})

    # Display table for Transportation costs
    if st.session_state.expense_data:
        df_expense = pd.DataFrame(st.session_state.expense_data)
        df_expense_invoice = pd.DataFrame(st.session_state.invoice_data)

        st.subheader("Artículos añadidos")
        st.table(df_expense)

        total_expenses = df_expense["Total"].sum()
        st.text(f"Total: {total_expenses}" + " " + peso_symbol)

        # convert de pandas dataframe to an array of objects
        st.session_state.items_invoice = df_expense.to_dict('records')
        st.session_state.invoice_data = df_expense_invoice.to_dict('records')
        final_price = total_expenses

# section additional invoice info
with st.container():
    cc3, cc4 = st.columns(2)
    notes = cc3.text_area("Notas")
    term = cc4.text_area("Términos")
    cc3.write("Subtotal: " + str(total_expenses) + " " + peso_symbol)
    impuesto = cc3.number_input("Impuesto %: ", min_value=0)
    if impuesto:
        imp = float('1.' + str(impuesto))
        final_price = final_price * imp
    descuento = cc3.number_input("Descuento %: ", min_value=0)
    if descuento:
        final_price = round(final_price - ((descuento / 100) * final_price), 2)
    cc3.write("Total: " + str(final_price) + " " + peso_symbol)

submit = st.button("Enviar")

# actions after submitting the form: validations, show summary, generate pdf, send email with attachments and pdf, write in google sheet info submitted
if submit:
    if not from_who or not to_who or not num_invoice or not date_invoice or not due_date:
        st.warning("Completa los campos obligatorios")
    elif len(st.session_state.items_invoice) == 0:
        st.warning("Añade algún artículo")
    else:
        try:
            # generate invoice pdf
            api = ApiConnector()
            pdf_bytes = api.connect_to_api_and_save_invoice_pdf(
                from_who, to_who, url_logo, num_invoice, str(date_invoice), str(due_date), st.session_state.invoice_data, notes, term, impuesto, descuento)

            if pdf_bytes:
                st.success("Desde aquí puedes descargar la factura generada")
                st.download_button(label="Descargar factura", data=pdf_bytes, file_name=f"Factura_{to_who}_{num_invoice}.pdf", mime="application/pdf")
            else:
                st.warning("Hubo un problema generando la factura pdf.")
        except Exception as excep:
            print(str(excep))
            st.warning("Hubo un problema generando la factura pdf.")
