from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Carrega os dados do Excel
df = pd.read_excel("compras_05-04-2025.xlsx")
df["Descrição do Item"] = df["Descrição do Item"].astype(str)
df["Valor Unitário"] = pd.to_numeric(df["Valor Unitário"], errors="coerce")

# Remove duplicatas e ordena os produtos
produtos_unicos = sorted(df["Descrição do Item"].dropna().unique())

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html", produtos=produtos_unicos)

@app.route("/resultado", methods=["POST"])
def resultado():
    total_itens = int(request.form.get("total_itens", 0))
    produtos_check = request.form.getlist("produto")
    itens_selecionados = []

    for i in range(total_itens):
        produto = request.form.get(f"produto_nome_{i}")
        quantidade_str = request.form.get(f"quantidade_{i}")
        quantidade = int(quantidade_str) if quantidade_str and quantidade_str.isdigit() else 1

        if produto in produtos_check:
            itens_selecionados.append((produto, quantidade))

    if not itens_selecionados:
        return "Nenhum item selecionado."

    resultado_por_mercado = {}
    economia_total = 0
    gasto_total = 0

    for item, qtde in itens_selecionados:
        dados_item = df[df["Descrição do Item"] == item]
        if not dados_item.empty:
            dados_item = dados_item.sort_values("Valor Unitário")
            local_mais_barato = dados_item.iloc[0]
            local_mais_caro = dados_item.iloc[-1]

            valor_unitario = local_mais_barato["Valor Unitário"]
            valor_mais_barato = valor_unitario * qtde
            valor_mais_caro = local_mais_caro["Valor Unitário"] * qtde

            economia = valor_mais_caro - valor_mais_barato
            economia_total += economia
            gasto_total += valor_mais_barato

            local = local_mais_barato["Local"]
            item_resultado = {
                "item": item,
                "quantidade": qtde,
                "local": local,
                "valor_unitario": round(valor_unitario, 2),
                "valor_total": round(valor_mais_barato, 2)
            }

            if local not in resultado_por_mercado:
                resultado_por_mercado[local] = []

            resultado_por_mercado[local].append(item_resultado)

    return render_template(
        "resultado.html",
        resultado_por_mercado=resultado_por_mercado,
        economia_total=round(economia_total, 2),
        gasto_total=round(gasto_total, 2)
    )

if __name__ == "__main__":
    app.run(debug=True)
