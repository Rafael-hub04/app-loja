import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# 🔥 EVITA ERRO EXCEL
os.environ["PANDAS_IO_EXCEL_XLSX_WRITER"] = ""

# CONFIG
st.set_page_config(page_title="Loja", layout="centered")

# 🎨 ESTILO PREMIUM
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    color: white;
}
h1, h2, h3 { color: #f8fafc; }

.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.stButton>button {
    background: linear-gradient(90deg, #3b82f6, #06b6d4);
    color: white;
    border-radius: 12px;
    height: 50px;
    font-weight: bold;
    width: 100%;
}

[data-testid="metric-container"] {
    background: #1e293b;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🛍️ <span style='color:#38bdf8;'>Controle da Loja</span></h1>", unsafe_allow_html=True)

# BANCO
conn = sqlite3.connect("loja.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS produtos (
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT, tamanho TEXT, quantidade INTEGER, cor TEXT, preco REAL)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS vendas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
produto_id INTEGER, quantidade INTEGER, valor_total REAL,
cliente TEXT, pagamento TEXT, cor TEXT, data TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS encomendas (
id INTEGER PRIMARY KEY AUTOINCREMENT,
cliente TEXT, produto TEXT, tamanho TEXT, cor TEXT,
valor REAL, status TEXT, data TEXT, observacao TEXT)""")

conn.commit()

# MENU
menu = st.radio("", ["📊 Dashboard","📦 Estoque","🛒 Venda","📋 Histórico","📦 Encomendas"], horizontal=True)

# ================= DASHBOARD =================
if menu == "📊 Dashboard":
    vendas = pd.read_sql("SELECT * FROM vendas", conn)
    produtos = pd.read_sql("SELECT * FROM produtos", conn)

    total_vendas = vendas["valor_total"].sum() if not vendas.empty else 0
    total_produtos = produtos["quantidade"].sum() if not produtos.empty else 0

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("💰 Vendas", f"R$ {total_vendas:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("📦 Estoque", total_produtos)
        st.markdown('</div>', unsafe_allow_html=True)

# ================= ESTOQUE =================
elif menu == "📦 Estoque":
    st.subheader("📦 Produtos")

    # ================= CADASTRO =================
    nome = st.text_input("Nome", key="cad_nome")
    tamanho = st.selectbox("Tamanho", ["P","M","G","GG"], key="cad_tam")
    quantidade = st.number_input("Quantidade", min_value=0, key="cad_qtd")
    cor = st.text_input("Cor", key="cad_cor")
    preco = st.number_input("Preço", key="cad_preco")

    if st.button("➕ Cadastrar Produto", key="btn_cad"):
        cursor.execute("""
        INSERT INTO produtos (nome, tamanho, quantidade, cor, preco)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, tamanho, quantidade, cor, preco))
        conn.commit()
        st.success("Produto cadastrado!")

    st.divider()

    # ================= TABELA =================
    df = pd.read_sql("SELECT * FROM produtos", conn)

    if not df.empty:
        st.dataframe(df, use_container_width=True, height=300)

    # ================= EDITAR PRODUTO =================
    st.subheader("✏️ Editar Produto")

    if not df.empty:
        prod_id = st.selectbox("Selecione o produto", df["id"], key="edit_id")

        prod = df[df["id"] == prod_id].iloc[0]

        novo_nome = st.text_input("Nome", value=prod["nome"], key="edit_nome")
        novo_tamanho = st.selectbox(
            "Tamanho",
            ["P","M","G","GG"],
            index=["P","M","G","GG"].index(prod["tamanho"]),
            key="edit_tam"
        )
        nova_qtd = st.number_input("Quantidade", value=int(prod["quantidade"]), key="edit_qtd")
        nova_cor = st.text_input("Cor", value=prod["cor"], key="edit_cor")
        novo_preco = st.number_input("Preço", value=float(prod["preco"]), key="edit_preco")

        if st.button("💾 Salvar Alterações", key="btn_edit"):
            cursor.execute("""
            UPDATE produtos
            SET nome=?, tamanho=?, quantidade=?, cor=?, preco=?
            WHERE id=?
            """, (
                novo_nome,
                novo_tamanho,
                nova_qtd,
                nova_cor,
                novo_preco,
                prod_id
            ))
            conn.commit()
            st.success("Produto atualizado!")
            st.rerun()

    st.divider()

    # ================= AJUSTE DE ESTOQUE =================
    # st.subheader("⚙️ Ajustar Estoque")

    # if not df.empty:
    #     prod_id_ajuste = st.selectbox("Produto", df["id"], key="ajuste_id")

    #     prod = df[df["id"] == prod_id_ajuste].iloc[0]

    #     st.info(f"""
    #     🧥 {prod['nome']}  
    #     📏 {prod['tamanho']} | 🎨 {prod['cor']}  
    #     📦 Atual: {prod['quantidade']}
    #     """)

    #     tipo = st.selectbox(
    #         "Tipo de ajuste",
    #         ["Entrada (+)", "Saída (-)", "Ajuste manual"],
    #         key="tipo_ajuste"
    #     )

    #     qtd = st.number_input("Quantidade", min_value=0, key="qtd_ajuste")

    #     if st.button("Aplicar Ajuste", key="btn_ajuste"):
    #         estoque_atual = prod["quantidade"]

    #         if tipo == "Entrada (+)":
    #             novo = estoque_atual + qtd

    #         elif tipo == "Saída (-)":
    #             if qtd > estoque_atual:
    #                 st.error("Estoque insuficiente!")
    #                 st.stop()
    #             novo = estoque_atual - qtd

    #         else:
    #             novo = qtd

    #         cursor.execute("""
    #         UPDATE produtos
    #         SET quantidade = ?
    #         WHERE id = ?
    #         """, (novo, prod_id_ajuste))

    #         conn.commit()

    #         st.success(f"Estoque atualizado: {novo}")
    #         st.rerun()

# ================= VENDA =================
elif menu == "🛒 Venda":
    st.subheader("🛒 Nova Venda")

    produtos = pd.read_sql("SELECT * FROM produtos", conn)

    if not produtos.empty:
        nome = st.selectbox("Produto", produtos["nome"].unique())
        dados = produtos[produtos["nome"]==nome]

        tamanho = st.selectbox("Tamanho", dados["tamanho"].unique())
        cor = st.selectbox("Cor", dados["cor"].unique())

        prod = produtos[
            (produtos["nome"]==nome)&
            (produtos["tamanho"]==tamanho)&
            (produtos["cor"]==cor)
        ].iloc[0]

        st.info(f"💰 {prod['preco']} | 📦 {prod['quantidade']}")

        qtd = st.number_input("Qtd", min_value=1)
        cliente = st.text_input("Cliente")
        pagamento = st.selectbox("Pagamento",["Pix","Dinheiro","Cartão"])

        if st.button("Finalizar"):
            cursor.execute("INSERT INTO vendas VALUES(NULL,?,?,?,?,?,?,?)",
                           (prod["id"],qtd,qtd*prod["preco"],cliente,pagamento,cor,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            cursor.execute("UPDATE produtos SET quantidade=quantidade-? WHERE id=?",(qtd,prod["id"]))
            conn.commit()
            st.success("Venda feita")
            st.rerun()

# ================= HISTÓRICO =================
elif menu == "📋 Histórico":
    st.subheader("📋 Histórico de Vendas")

    df = pd.read_sql("""
    SELECT 
        v.*, 
        p.nome, 
        p.tamanho, 
        p.cor AS cor_produto
    FROM vendas v
    JOIN produtos p ON v.produto_id = p.id
    ORDER BY v.data DESC
    """, conn)

    if not df.empty:
        # 🔥 FORMATAR DATA
        df["data"] = pd.to_datetime(df["data"]).dt.strftime("%d/%m/%Y %H:%M")

        st.dataframe(df, use_container_width=True, height=300)

        # ================= EDITAR VENDA =================
        st.divider()
        st.subheader("✏️ Editar Venda")

        venda_id = st.selectbox("Selecione a venda", df["id"], key="hist_venda")

        venda = df[df["id"] == venda_id].iloc[0]

        nova_qtd = st.number_input(
            "Quantidade",
            min_value=1,
            value=int(venda["quantidade"]),
            key="hist_qtd"
        )

        novo_pag = st.selectbox(
            "Pagamento",
            ["Pix", "Dinheiro", "Cartão"],
            index=["Pix", "Dinheiro", "Cartão"].index(venda["pagamento"]),
            key="hist_pag"
        )

        if st.button("💾 Salvar Alterações", key="btn_hist"):
            qtd_antiga = venda["quantidade"]
            diff = nova_qtd - qtd_antiga

            cursor.execute("SELECT quantidade FROM produtos WHERE id=?", (venda["produto_id"],))
            estoque = cursor.fetchone()[0]

            if diff > 0 and diff > estoque:
                st.error("Estoque insuficiente!")
            else:
                cursor.execute("""
                UPDATE produtos
                SET quantidade = quantidade - ?
                WHERE id = ?
                """, (diff, venda["produto_id"]))

                preco_unit = venda["valor_total"] / venda["quantidade"]

                cursor.execute("""
                UPDATE vendas
                SET quantidade=?, pagamento=?, valor_total=?
                WHERE id=?
                """, (
                    nova_qtd,
                    novo_pag,
                    nova_qtd * preco_unit,
                    venda_id
                ))

                conn.commit()
                st.success("Venda atualizada!")
                st.rerun()

        # ================= ESTORNO =================
        st.divider()
        st.subheader("↩️ Estornar Venda")

        venda_estorno_id = st.selectbox(
            "Selecione a venda para estorno",
            df["id"],
            key="estorno_venda"
        )

        venda_estorno = df[df["id"] == venda_estorno_id].iloc[0]

        st.warning(f"""
        ⚠️ Estorno da venda:

        🧥 Produto: {venda_estorno['nome']}  
        📏 Tamanho: {venda_estorno['tamanho']}  
        🎨 Cor: {venda_estorno['cor_produto']}  
        📦 Quantidade: {venda_estorno['quantidade']}
        """)

        confirmar = st.checkbox("Confirmar estorno", key="confirmar_estorno")

        if st.button("↩️ Estornar Venda", key="btn_estorno"):
            if not confirmar:
                st.error("Confirme o estorno!")
            else:
                # 🔥 DEVOLVE AO ESTOQUE
                cursor.execute("""
                UPDATE produtos
                SET quantidade = quantidade + ?
                WHERE id = ?
                """, (
                    int(venda_estorno["quantidade"]),
                    int(venda_estorno["produto_id"])
                ))

                # 🔥 REMOVE VENDA
                cursor.execute("DELETE FROM vendas WHERE id=?", (venda_estorno_id,))

                conn.commit()

                st.success("Venda estornada com sucesso! ✅")
                st.rerun()

# ================= ENCOMENDAS =================
elif menu == "📦 Encomendas":
    st.subheader("📦 Encomendas")

    cliente = st.text_input("Cliente")
    produto = st.text_input("Produto")
    status = st.selectbox("Status",["Pendente","Pronto","Entregue"])

    if st.button("Registrar"):
        cursor.execute("INSERT INTO encomendas VALUES(NULL,?,?,?,?,?,?,?,?)",
                       (cliente,produto,"","",0,status,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),""))
        conn.commit()
        st.success("Encomenda salva")

    df = pd.read_sql("SELECT * FROM encomendas", conn)
    st.dataframe(df)