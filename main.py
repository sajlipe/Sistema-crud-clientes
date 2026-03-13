import sqlite3
import shutil
import os
import sys
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from datetime import datetime
from tkinter import messagebox
from PIL import Image, ImageTk


CONFIG_ARQUIVO = "config.txt"
def caminho_banco():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

pasta_projeto = caminho_banco()
caminho_banco = os.path.join(pasta_projeto, "clientes.db")

# Criar o banco de dados na pasta do projeto

conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()

# Criar a tabela clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nome TEXT NOT NULL,
    telefone TEXT,
    endereco TEXT,
    cpf_cnpj TEXT UNIQUE,
    data_cadastro TEXT
)""")

# Tabela de pedidos
cursor.execute("""
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    numero_pedido TEXT UNIQUE,
    caminho_pdf TEXT,
    data_pedido TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
)""")

# Índices para melhorar velocidade das buscas
cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_nome ON clientes(nome)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_cpf ON clientes(cpf_cnpj)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_cliente_tel ON clientes(telefone)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedido_numero ON pedidos(numero_pedido)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedido_cliente ON pedidos(cliente_id)")

conexao.commit()
conexao.close()

print("Banco de dados e tabelas criados com sucesso!")

# ============================================
# FUNÇÕES DE UTILIDADE
# ============================================

def painel_cliente(cliente_id):

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT nome, telefone, endereco, cpf_cnpj, data_cadastro
    FROM clientes
    WHERE id = ?
    """, (cliente_id,))

    cliente = cursor.fetchone()

    if not cliente:
        messagebox.showerror("Erro", "Cliente não encontrado.",
            parent=janela
        )
        return

    nome, telefone, endereco, cpf_cnpj, data_cadastro = cliente

    janela, frame = nova_janela("Painel do Cliente")

def painel_cliente(cliente_id):

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT nome, telefone, endereco, cpf_cnpj, data_cadastro
    FROM clientes
    WHERE id = ?
    """, (cliente_id,))

    cliente = cursor.fetchone()

    if not cliente:
        messagebox.showerror("Erro", "Cliente não encontrado.",
            parent=janela
        )
        return

    nome, telefone, endereco, cpf_cnpj, data_cadastro = cliente

    janela, frame = nova_janela("Painel do Cliente")

    def abrir_pasta_cliente():

        pasta_padrao = carregar_pasta_padrão()

        if not pasta_padrao:
            messagebox.showerror("Erro", "Pasta de pedidos não configurada.",
                parent=janela
            )
            return

        nome_pasta = nome.replace(" ", "_")
        pasta_cliente = os.path.join(pasta_padrao, nome_pasta)

        if os.path.exists(pasta_cliente):
            os.startfile(pasta_cliente)
        else:
            messagebox.showwarning("Aviso", "Pasta do cliente não encontrada.",
                parent=janela
            )

    # INFORMAÇÕES DO CLIENTE
    info = f"""
Nome: {nome}
Telefone: {formatar_telefone(telefone)}
Endereço: {endereco}
CPF/CNPJ: {formatar_documento(cpf_cnpj)}
Data de Cadastro: {data_cadastro}
"""

    tk.Label(frame, text=info, font=("Arial", 14), justify="left").pack(pady=10)

    tk.Button(
        frame,
        text="Abrir pasta do cliente",
        command=abrir_pasta_cliente
    ).pack(pady=5)

    tk.Button(
        frame,
        text="➕ Anexar Pedido",
        command=lambda: anexar_pdf_gui(cliente_id)
    ).pack(pady=5)

    tk.Button(
        frame,
        text="✏️ Editar Cliente",
        command=lambda: editar_cliente(cliente_id)
    ).pack(pady=5)

    tk.Button(
        frame,
        text="🗑 Excluir Cliente",
        command=lambda: excluir_cliente(cliente_id)
    ).pack(pady=5)

    tk.Button(
        frame,
        text="Voltar",
        font=("Arial", 12),
        width=15,
        command=janela.destroy
    ).pack(pady=10)
    
    # TABELA DE PEDIDOS
    tabela = ttk.Treeview(
        frame,
        columns=("Numero", "Data"),
        show="headings"
    )

    style = ttk.Style()
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 11))
    style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))

    tabela.heading("Numero", text="Número do Pedido")
    tabela.heading("Data", text="Data do Pedido")

    tabela.column("Numero", width=200)
    tabela.column("Data", width=200)

    tabela.pack(fill="both", expand=True)

    cursor.execute("""
    SELECT numero_pedido, data_pedido, caminho_pdf
    FROM pedidos
    WHERE cliente_id = ?
    ORDER BY data_pedido DESC
    """, (cliente_id,))

    pedidos = cursor.fetchall()

    for pedido in pedidos:
        tabela.insert("", "end", values=(pedido[0], pedido[1]))

    def abrir_pdf(event):

        item = tabela.selection()

        if not item:
            return

        item = item[0]
        indice = tabela.index(item)

        caminho = pedidos[indice][2]

        if os.path.exists(caminho):
            os.startfile(caminho)
        else:
            messagebox.showerror("Erro", "PDF não encontrado.",
                parent=janela
            )

    tabela.bind("<Double-1>", abrir_pdf)

    conexao.close()

def buscar_cliente_inteligente(termo):
    """Busca clientes por nome, CPF/CNPJ, telefone ou endereço"""
    
    termo = termo.strip().lower()
    
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    query = """
    SELECT * FROM clientes 
    WHERE LOWER(nome) LIKE ?
    or endereco LIKE ?
    """
    parametros = (f"%{termo}%", f"%{termo}%")

    termo_doc = limpar_documento(termo)
    termo_tel = limpar_telefone(termo)
    
    if termo_doc:
        query += " OR cpf_cnpj LIKE ?"
        parametros += (f"%{termo_doc}%",)
    
    if termo_tel:
        query += " OR telefone LIKE ?"
        parametros += (f"%{termo_tel}%",)
    
    cursor.execute(query, parametros)

    resultados = cursor.fetchall()
    conexao.close()

    return resultados

def pausar():
    """Sistema de pausa para melhor visualização dos resultados"""
    print("\n" + "="*60 + "\n")
    input("Pressione Enter para voltar ao menu...")

def limpar_documento(doc):
    """Remove caracteres especiais do documento"""
    return ''.join(filter(str.isdigit, doc))

def validar_cpf_cnpj(doc):
    """Valida se o documento tem 11 (CPF) ou 14 (CNPJ) dígitos"""
    doc_limpo = limpar_documento(doc)
    
    if len(doc_limpo) == 11:
        return True, doc_limpo, "CPF"
    elif len(doc_limpo) == 14:
        return True, doc_limpo, "CNPJ"
    else:
        return False, doc_limpo, None

def formatar_documento(doc):
    """Formata CPF ou CNPJ com separadores"""
    if len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14:
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    else:
        return doc


def limpar_telefone(tel):
    """Remove caracteres não numéricos de um telefone"""
    return ''.join(filter(str.isdigit, tel))


def formatar_telefone(tel):
    """Formata um número de telefone brasileiro (10 ou 11 dígitos)

    Exemplos:
        11987654321 -> (11) 98765-4321
        1132456789  -> (11) 3245-6789
    """
    digitos = limpar_telefone(tel)
    if len(digitos) == 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    elif len(digitos) == 11:
        return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"
    else:
        # retorna como veio se não for um padrão conhecido
        return tel

def salvar_pasta_padrão(caminho):
    """Salva o caminho da pasta padrão em um arquivo de configuração"""
    with open(CONFIG_ARQUIVO, 'w') as f:
        f.write(caminho)

def carregar_pasta_padrão():
    """Carrega o caminho da pasta padrão do arquivo de configuração"""
    if os.path.exists(CONFIG_ARQUIVO):
        with open(CONFIG_ARQUIVO, 'r') as f:
            return f.read().strip()
    return None

def nova_janela(titulo):
   janela = ttk.Toplevel()
   janela.title(titulo)
   janela.state("zoomed")

   janela.iconbitmap("logo.ico")

   frame = ttk.Frame(janela)
   frame.pack(pady=30)

   return janela, frame
# ============================================
# FUNÇÕES DE SELEÇÃO
# ============================================

def selecionar_cliente_busca(resultados=None):
    """Retorna o ID do cliente selecionado a partir de uma lista de resultados.

    Se ``resultados`` for None, solicita ao usuário um termo de busca e usa
    ``buscar_cliente_inteligente`` para gerar a lista.
    """
    if resultados is None:
        termo = input("Digite nome, CPF/CNPJ, telefone ou endereço do cliente: ")
        resultados = buscar_cliente_inteligente(termo)

    if not resultados:
        print("\n❌ Nenhum cliente encontrado.\n")
        pausar()
        return None
    
    print("\n✅ Clientes encontrados:\n")

    for i, cliente in enumerate(resultados):
        print(f"[{i}] cliente: {cliente[1]} | CPF/CNPJ: {formatar_documento(cliente[4])}")
    
    escolha = input("\nEscolha o cliente: ")

    try:
        indice = int(escolha)
        return resultados[indice][0]  # Retorna o ID do cliente
    except Exception:
        print("\n❌ Opção inválida. Operação cancelada.\n")
        return None

# ============================================
# FUNÇÃO CADASTRO
# ============================================

def cadastrar_cliente():
   
    janela, frame = nova_janela("Cadastrar Cliente")

    tk.Label(frame, text="Nome:", font=("Arial", 14)).pack(pady=5)
    entry_nome = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_nome.pack()

    tk.Label(frame, text="CPF/CNPJ:", font=("Arial", 14)).pack(pady=5)
    entry_cpf_cnpj = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_cpf_cnpj.pack()

    tk.Label(frame, text="Telefone:", font=("Arial", 14)).pack(pady=5)
    entry_telefone = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_telefone.pack()

    tk.Label(frame, text="Endereço:", font=("Arial", 14)).pack(pady=5) 
    entry_endereco = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_endereco.pack()

    def salvar():
        nome = entry_nome.get().strip()
        cpf_cnpj = entry_cpf_cnpj.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório.",
                parent=janela
            )
            return
        
        valido, cpf_cnpj_limpo, tipo = validar_cpf_cnpj(cpf_cnpj)
        if not valido:
            messagebox.showerror("Erro", f"CPF/CNPJ inválido! Deve conter exatamente 11 dígitos (CPF) ou 14 dígitos (CNPJ).",
                parent=janela
            )
            return
        
        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        cursor.execute("SELECT id FROM clientes WHERE LOWER(nome) = LOWER(?)", (nome,))
        if cursor.fetchone():
            messagebox.showerror("Erro", "Já existe um cliente com esse nome completo.",
                parent=janela
            )
            conexao.close()
            return
        
        cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = ?", (cpf_cnpj_limpo,))
        if cursor.fetchone():
            messagebox.showerror("Erro", f"Esse {tipo} já existe no sistema.", 
                parent=janela
            )
            conexao.close()
            return
        
        data_cadastro = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        cursor.execute("""
        INSERT INTO clientes (nome, telefone, endereco, cpf_cnpj, data_cadastro)
        VALUES (?, ?, ?, ?, ?)
        """, (nome, limpar_telefone(telefone), endereco, cpf_cnpj_limpo, data_cadastro))

        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!",
            parent=janela
        )
        janela.destroy()
    tk.Button(frame, text="Salvar", font=("Arial", 14), command=salvar).pack(pady=20)

    tk.Button(
        frame,
        text="Voltar",
        font=("Arial", 12),
        width=15,
        command=janela.destroy
    ).pack(pady=10)

# ============================================
# FUNÇÃO EDITAR e EXCLUIR
# ============================================

def editar_cliente(cliente_id):

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT nome, telefone, endereco, cpf_cnpj 
    FROM clientes 
    WHERE id = ?
    """, (cliente_id,))
    
    cliente = cursor.fetchone()
    conexao.close()

    if not cliente:
        messagebox.showerror("Erro", "Cliente não encontrado.", 
            parent=janela
        )
        return
    
    nome_atual, telefone_atual, endereco_atual, cpf_cnpj_atual = cliente
    
    janela, frame = nova_janela("Editar Cliente")

    tk.Label(frame, text="Nome:", font=("Arial", 14)).pack(pady=5)
    entry_nome = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_nome.insert(0, nome_atual)
    entry_nome.pack()

    tk.Label(frame, text="CPF/CNPJ:", font=("Arial", 14)).pack(pady=5)
    entry_cpf_cnpj = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_cpf_cnpj.insert(0, formatar_documento(cpf_cnpj_atual))
    entry_cpf_cnpj.pack()

    tk.Label(frame, text="Telefone:", font=("Arial", 14)).pack(pady=5)
    entry_telefone = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_telefone.insert(0, formatar_telefone(telefone_atual))
    entry_telefone.pack()

    tk.Label(frame, text="Endereço:", font=("Arial", 14)).pack(pady=5)
    entry_endereco = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_endereco.insert(0, endereco_atual)
    entry_endereco.pack()

    def salvar():
        nome = entry_nome.get().strip()
        cpf_cnpj = entry_cpf_cnpj.get().strip()
        telefone = entry_telefone.get().strip()
        endereco = entry_endereco.get().strip()

        if not nome:
            messagebox.showerror("Erro", "O nome é obrigatório.",
                parent=janela
            )
            return
        
        valido, cpf_cnpj_limpo, tipo = validar_cpf_cnpj(cpf_cnpj)
        if not valido:
            messagebox.showerror("Erro", f"CPF/CNPJ inválido! Deve conter exatamente 11 dígitos (CPF) ou 14 dígitos (CNPJ).",
                parent=janela
            )
            return
        
        telefone_limpo = limpar_telefone(telefone)

        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id FROM clientes WHERE LOWER(nome) = LOWER(?) AND id != ?", 
            (nome, cliente_id))
        
        if cursor.fetchone():
           continuar = messagebox.askyesno(
               "Nome já existe",
                "Já existe outro cliente com esse nome completo. \nDeseja continuar mesmo assim?",
                parent=janela
            )
           if not continuar:
               conexao.close()
               return
        
        cursor.execute("SELECT id FROM clientes WHERE cpf_cnpj = ? AND id != ?", (cpf_cnpj_limpo, cliente_id))
        if cursor.fetchone():
            messagebox.showerror("Erro", f"Esse {tipo} já existe no sistema para outro cliente.", 
                parent=janela)
            conexao.close()
            return
        
        cursor.execute("""
        UPDATE clientes
        SET nome = ?, telefone = ?, endereco = ?, cpf_cnpj = ?
        WHERE id = ?
        """, (nome, limpar_telefone(telefone), endereco, cpf_cnpj_limpo, cliente_id))

        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!",
            parent=janela
        )
        janela.destroy()
    
    tk.Button(frame, text="Salvar", font=("Arial", 14), command=salvar).pack(pady=20)

def excluir_cliente(cliente_id):

    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT nome, telefone, endereco, cpf_cnpj 
    FROM clientes
    WHERE id = ?
    """, (cliente_id,))

    cliente = cursor.fetchone()

    if not cliente:
        messagebox.showerror("Erro", "Cliente não encontrado.",
            parent=nova_janela)
        conexao.close()
        return

    nome, telefone, endereco, cpf_cnpj = cliente

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE cliente_id = ?", (cliente_id,))
    num_pedidos = cursor.fetchone()[0]

    info_cliente = f"""
Nome: {nome}
Telefone: {formatar_telefone(telefone)}
Endereço: {endereco}
CPF/CNPJ: {formatar_documento(cpf_cnpj)}
"""
    if num_pedidos > 0: 

        confirmar = messagebox.askyesno(
            "Atenção",
            f"O cliente possui {num_pedidos} pedido(s) associado(s).\n\n"
            f"{info_cliente}\n"
            "Ao excluir o cliente, todos os pedidos também serão excluídos.\n\n"
            "Deseja continuar?",
            parent=nova_janela
        )

        if not confirmar:
            conexao.close()
            return
    
        confirmar2 = messagebox.askyesno(
            "Confirmação Final",
            f"Tem certeza que deseja excluir este cliente?\n\n"
            f"{info_cliente}\n"
            "Esta ação é irreversível.",
            parent=nova_janela
        )

        if not confirmar2:
            conexao.close()
            return
    
        cursor.execute(
            "DELETE FROM pedidos WHERE cliente_id = ?",
            (cliente_id,))
    
    else:

        confirmar = messagebox.askyesno(
            "Confirmação",
            f"Tem certeza que deseja excluir este cliente?\n\n"
            f"{info_cliente}\n"
            "Esta ação é irreversível.",
            parent=nova_janela
        )

        if not confirmar:
            conexao.close()
            return
    
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))

    conexao.commit()
    conexao.close()

    messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!",
        parent=nova_janela)

# ============================================
# FUNÇÃO ANEXAR PDF
# ============================================

def anexar_pdf_gui(cliente_id):

    janela, frame = nova_janela("Anexar Pedido")

    tk.Label(frame, text="Número do Pedido:", font=("Arial", 14)).pack(pady=5)
    entry_pedido = tk.Entry(frame, font=("Arial", 14), width=40)
    entry_pedido.pack()

    def selecionar_pdf():

        numero_pedido = entry_pedido.get().strip()

        if not numero_pedido:
            messagebox.showerror("Erro", "O número do pedido é obrigatório.",
                parent=janela)
            return

        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT id FROM pedidos WHERE numero_pedido = ?",
            (numero_pedido,)
        )

        if cursor.fetchone():
            messagebox.showerror("Erro", "Já existe um pedido com esse número.",
            parent=janela)
            conexao.close()
            return

        pasta_padrao = carregar_pasta_padrão()

        if not pasta_padrao or not os.path.exists(pasta_padrao):

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)

            pasta_busca = filedialog.askdirectory(
                title="Selecione a pasta de pedidos"
            )

            root.destroy()

            if not pasta_busca:
                conexao.close()
                return

            salvar_pasta_padrão(pasta_busca)
            pasta_padrao = pasta_busca

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        arquivo = filedialog.askopenfilename(
            initialdir=pasta_padrao,
            title="Selecione o PDF do pedido",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )

        root.destroy()

        if not arquivo:
            conexao.close()
            return

        nome_arquivo = os.path.basename(arquivo)

        cursor.execute(
            "SELECT nome FROM clientes WHERE id = ?",
            (cliente_id,)
        )

        nome_cliente = cursor.fetchone()[0]

        nome_pasta = nome_cliente.replace(" ", "_")

        pasta_cliente = os.path.join(pasta_padrao, nome_pasta)

        if not os.path.exists(pasta_cliente):
            os.makedirs(pasta_cliente)

        destino = os.path.join(pasta_cliente, nome_arquivo)

        shutil.copy(arquivo, destino)

        data_pedido = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        cursor.execute("""
        INSERT INTO pedidos (cliente_id, numero_pedido, caminho_pdf, data_pedido)
        VALUES (?, ?, ?, ?)
        """, (cliente_id, numero_pedido, destino, data_pedido))

        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Pedido anexado com sucesso!",
            parent=janela)
        janela.destroy()

    tk.Button(
        frame,
        text="Selecionar PDF",
        font=("Arial", 14),
        command=selecionar_pdf
    ).pack(pady=20)

    tk.Button(
        frame,
        text="Voltar",
        font=("Arial", 12),
        width=15,
        command=janela.destroy
        ).pack(pady=10)
# ============================================
# FUNÇÕES DE BUSCA DE CLIENTE
# ============================================

def buscar_cliente():
    """Submenu para buscar clientes por diferentes critérios (CLI)"""
    while True:
        print("""
╔══════════════════════════════════════════╗
║            BUSCAR CLIENTE               ║
╚══════════════════════════════════════════╝

1 - Por Nome
2 - Por CPF/CNPJ
3 - Por Telefone
4 - Por Endereço
5 - Interface Gráfica
0 - Voltar ao Menu Principal

""")
        opcao_busca = input("Escolha um critério de busca: ").strip()
        
        if opcao_busca == '1':
            buscar_por_nome(input("Digite o nome do cliente: "))
        elif opcao_busca == '2':
            buscar_por_cpf_cnpj(input("Digite o CPF/CNPJ do cliente: "))
        elif opcao_busca == '3':
            buscar_por_telefone(input("Digite o telefone do cliente: "))
        elif opcao_busca == '4':
            buscar_por_endereco(input("Digite o endereço do cliente: "))
        elif opcao_busca == '5':
            buscar_cliente_gui()
        elif opcao_busca == '0':
            break
        else:
            print("\n❌ Opção inválida. Tente novamente.\n")
            pausar()

# ============================================

def buscar_cliente_gui(callback=None):

    janela = tk.Toplevel()
    janela.title("Buscar Cliente")
    janela.state("zoomed")

    janela.iconbitmap("logo.ico")
    
    frame = tk.Frame(janela)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="Buscar Cliente:", font=("Arial", 14)).pack(pady=10)

    entry_busca = tk.Entry(frame, font=("Arial", 14))
    entry_busca.pack(fill="x", padx=20, pady=10)

    scrollbar = tk.Scrollbar(frame)

    tabela_clientes = ttk.Treeview(
        frame,
        columns=("Nome", "Cpf/Cnpj"),
        show="headings",
        yscrollcommand=scrollbar.set
    )
    
    tabela_clientes.heading("Nome", text="Nome")
    tabela_clientes.heading("Cpf/Cnpj", text="CPF/CNPJ")

    tabela_clientes.column("Nome", width=400)
    tabela_clientes.column("Cpf/Cnpj", width=200)

    scrollbar.config(command=tabela_clientes.yview)

    tabela_clientes.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    resultados = []

    def atualizar_tabela(clientes):

        for item in tabela_clientes.get_children():
            tabela_clientes.delete(item)
        
        for cliente in clientes:
            tabela_clientes.insert(
                "",
                "end", 
                values=(cliente[1], formatar_documento(cliente[4]))
            )
    
    def filtrar_clientes(event=None):
        
        termo = entry_busca.get().strip()

        nonlocal resultados
        resultados = buscar_cliente_inteligente(termo)

        atualizar_tabela(resultados)
    
    def abrir_cliente(event):
        
        item = tabela_clientes.selection()

        if not item:
            return
        
        item = item[0]
        indice = tabela_clientes.index(item)

        cliente = resultados[indice]
        cliente_id = cliente[0]

        janela.destroy()

        if callback:
            callback(cliente_id)
        else:
            painel_cliente(cliente_id)

    entry_busca.bind("<KeyRelease>", filtrar_clientes)

    tabela_clientes.bind("<Double-1>", abrir_cliente)

    resultados = buscar_cliente_inteligente("")
    atualizar_tabela(resultados)

    entry_busca.focus()

    tk.Button(
        frame,
        text="Voltar",
        font=("Arial", 12),
        width=15,
        command=janela.destroy
    ).pack(pady=10)
# ============================================

def buscar_por_nome(nome):
    """Busca clientes por nome"""
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""
    SELECT * FROM clientes 
    WHERE LOWER(nome) LIKE ?
    """, ('%' + nome + '%',))

    resultados = cursor.fetchall()
    
    if not resultados:
        print("\n❌ Nenhum cliente encontrado com esse nome.\n")
    else:
        print("\n✅ Clientes encontrados:\n")
        for cliente in resultados:
            print(f"""
ID: {cliente[0]}
Nome: {cliente[1]}
Telefone: {formatar_telefone(cliente[2])}
Endereço: {cliente[3]}
CPF/CNPJ: {formatar_documento(cliente[4])}
Data de Cadastro: {cliente[5]}
-----------------------------
""")
    pausar()
    conexao.close()

def buscar_por_cpf_cnpj(cpf_cnpj):
    """Busca clientes por CPF/CNPJ"""
    cpf_cnpj = limpar_documento(cpf_cnpj)
  
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""SELECT * FROM clientes WHERE cpf_cnpj LIKE ?
    """, ('%' + cpf_cnpj + '%',))
    resultados = cursor.fetchall()
    
    if not resultados:
        print("\n❌ Nenhum cliente encontrado com esse CPF/CNPJ.\n")
    else:
        print("\n✅ Cliente encontrado:\n")
        for cliente in resultados:
            print(f"""ID: {cliente[0]}
Nome: {cliente[1]}
Telefone: {formatar_telefone(cliente[2])}
Endereço: {cliente[3]}
CPF/CNPJ: {formatar_documento(cliente[4])}
Data de Cadastro: {cliente[5]}
-----------------------------
""")
    pausar()
    conexao.close()

def buscar_por_telefone(telefone):
    """Busca clientes por telefone"""
    telefone = limpar_telefone(telefone)
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""SELECT * FROM clientes WHERE telefone LIKE ?
    """, ('%' + telefone + '%',))
    resultados = cursor.fetchall()
    
    if not resultados:
        print("\n❌ Nenhum cliente encontrado com esse telefone.\n")
    else:
        print("\n✅ Cliente encontrado:\n")
        for cliente in resultados:
            print(f"""ID: {cliente[0]}
Nome: {cliente[1]}
Telefone: {formatar_telefone(cliente[2])}
Endereço: {cliente[3]}
CPF/CNPJ: {formatar_documento(cliente[4])}
Data de Cadastro: {cliente[5]}
-----------------------------
""")
    pausar()
    conexao.close()

def buscar_por_endereco(endereco):
    """Busca clientes por endereço"""
    conexao = sqlite3.connect(caminho_banco)
    cursor = conexao.cursor()

    cursor.execute("""SELECT * FROM clientes WHERE endereco LIKE ?
    """, ('%' + endereco + '%',))
    resultados = cursor.fetchall()
    
    if not resultados:
        print("\n❌ Nenhum cliente encontrado com esse endereço.\n")
    else:
        print("\n✅ Cliente encontrado:\n")
        for cliente in resultados:
            print(f"""ID: {cliente[0]}
Nome: {cliente[1]}
Telefone: {formatar_telefone(cliente[2])}
Endereço: {cliente[3]}
CPF/CNPJ: {formatar_documento(cliente[4])}
Data de Cadastro: {cliente[5]}
-----------------------------
""")
    pausar()
    conexao.close()

def buscar_pedido_gui():

    janela = tk.Toplevel()
    janela.title("Buscar Pedido")
    janela.state("zoomed")

    janela.iconbitmap("logo.ico")

    frame = tk.Frame(janela)
    frame.pack(fill="both", expand=True, padx=20, pady=20)

    tk.Label(frame, text="Número do Pedido:", font=("Arial", 14)).pack(pady=10)

    entry_busca = tk.Entry(frame, font=("Arial", 14))
    entry_busca.pack(fill="x", padx=20, pady=10)

    scrollbar = tk.Scrollbar(frame)

    tabela = ttk.Treeview(
        frame,
        columns=("Cliente", "Numero", "Data"),
        show="headings",
        yscrollcommand=scrollbar.set
    )

    tabela.heading("Cliente", text="Cliente")
    tabela.heading("Numero", text="Número do Pedido")
    tabela.heading("Data", text="Data do Pedido")

    tabela.column("Cliente", width=400)
    tabela.column("Numero", width=200)
    tabela.column("Data", width=200)

    scrollbar.config(command=tabela.yview)

    tabela.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    resultados = []

    def atualizar_tabela(dados):

        for item in tabela.get_children():
            tabela.delete(item)

        for pedido in dados:
            tabela.insert(
                "",
                "end",
                values=(pedido[1], pedido[2], pedido[3])
            )

    def filtrar(event=None):

        termo = entry_busca.get().strip()

        conexao = sqlite3.connect(caminho_banco)
        cursor = conexao.cursor()

        cursor.execute("""
        SELECT pedidos.id, clientes.nome, pedidos.numero_pedido,
               pedidos.data_pedido, pedidos.caminho_pdf
        FROM pedidos
        JOIN clientes ON pedidos.cliente_id = clientes.id
        WHERE pedidos.numero_pedido LIKE ?
        """, ('%' + termo + '%',))

        nonlocal resultados
        resultados = cursor.fetchall()

        conexao.close()

        atualizar_tabela(resultados)

    def abrir_pdf(event):

        item = tabela.selection()

        if not item:
            return

        item = item[0]
        indice = tabela.index(item)

        caminho = resultados[indice][4]

        if os.path.exists(caminho):
            os.startfile(caminho)
        else:
            messagebox.showerror("Erro", "PDF não encontrado.",
            parent=janela)

    entry_busca.bind("<KeyRelease>", filtrar)
    tabela.bind("<Double-1>", abrir_pdf)

    tk.Button(
        frame,
        text="Voltar",
        font=("Arial", 12),
        width=15,
        command=janela.destroy
    ).pack(pady=10)
    
    filtrar()
    entry_busca.focus()
# ============================================
# MENU PRINCIPAL
# ============================================

def interface_principal():
    """Função para iniciar a interface gráfica"""
    janela = ttk.Window(themename="flatly")
    janela.title("Sistema de Gerenciamento de Clientes e Pedidos")
    janela.state("zoomed")


    janela.iconbitmap("logo.ico")

    frame_central = ttk.Frame(janela)
    frame_central.pack(expand=True)

    logo_img = Image.open("logo.png")
    logo_img = logo_img.resize((220, 220))

    logo = ImageTk.PhotoImage(logo_img)

    logo_label = ttk.Label(frame_central, image=logo)
    logo_label.pack(pady=20)

    titulo = ttk.Label(
        frame_central,
        text="Sistema de Gerenciamento de Clientes",
        font=("Segoe UI", 24, "bold")
    )

    titulo.pack(pady=10)

    ttk.Button(
        frame_central,
        text="➕ Cadastrar Cliente",
        bootstyle="success",
        width=35,
        command=cadastrar_cliente
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="🔍 Buscar Cliente",
        bootstyle="info",
        width=35,
        command=buscar_cliente_gui
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="📎 Anexar Pedido (PDF)",
        bootstyle="primary",
        width=35,
        command=lambda: buscar_cliente_gui(anexar_pdf_gui)
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="📄 Buscar Pedido",
        bootstyle="secondary",
        width=35,
        command=buscar_pedido_gui
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="✏️ Editar Cliente",
        bootstyle="warning",
        width=35,
        command=lambda: buscar_cliente_gui(editar_cliente)
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="🗑 Excluir Cliente",
        bootstyle="danger",
        width=35,
        command=lambda: buscar_cliente_gui(excluir_cliente)
    ).pack(pady=8)

    ttk.Button(
        frame_central,
        text="❌ Sair",
        bootstyle="dark",
        width=35,
        command=janela.destroy
    ).pack(pady=20)

    janela.mainloop()

if __name__ == "__main__":
    interface_principal()
