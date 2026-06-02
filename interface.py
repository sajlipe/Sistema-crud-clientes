from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import ttkbootstrap as ttk

    HAS_BOOTSTRAP = True
except ImportError:
    from tkinter import ttk

    HAS_BOOTSTRAP = False

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

import logging
import backup as backup_service
import clientes as cliente_service
import database
import excel as excel_service
import pedidos as pedido_service
from config import APP_TITLE, asset_path, load_config, save_config

logger = logging.getLogger(__name__)


COLORS = {
    "primary": "#0F766E",
    "primary_dark": "#115E59",
    "accent": "#F59E0B",
    "background": "#F6F8FB",
    "surface": "#FFFFFF",
    "border": "#D8DEE9",
    "text": "#172033",
    "muted": "#64748B",
    "danger": "#B91C1C",
    "sidebar": "#EBF4F3",
}


class SistemaApp:
    def __init__(self) -> None:
        database.init_database()
        self.config = load_config()
        database.atualizar_empresa_padrao(self.config)

        self.root = self._create_root()
        self.root.title(APP_TITLE)
        self._set_icon(self.root)
        self._zoom(self.root)

        self.logo_photo = None
        self.company_label: tk.Label | None = None
        self.dashboard_labels: dict[str, tk.Label] = {}

        self._configure_style()
        self._build_layout()
        self.refresh_dashboard()

    def _create_root(self):
        theme = self.config.get("theme") or "flatly"
        if HAS_BOOTSTRAP:
            try:
                return ttk.Window(themename=theme)
            except Exception:
                return ttk.Window(themename="flatly")
        return tk.Tk()

    def _configure_style(self) -> None:
        style = ttk.Style() if HAS_BOOTSTRAP else ttk.Style(self.root)
        if not HAS_BOOTSTRAP:
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass

        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=COLORS["muted"])
        style.configure("TButton", font=("Segoe UI", 10))

    def _set_icon(self, window) -> None:
        icon = asset_path("logo.ico")
        if icon.exists():
            try:
                window.iconbitmap(str(icon))
            except tk.TclError:
                pass

    def _zoom(self, window) -> None:
        try:
            window.state("zoomed")
        except tk.TclError:
            window.geometry("1180x760")

    def _load_logo(self, size: int):
        if Image is None or ImageTk is None:
            return None

        logo = asset_path("logo.png")
        if not logo.exists():
            return None

        try:
            image = Image.open(logo).resize((size, size))
            return ImageTk.PhotoImage(image)
        except Exception:
            return None

    def _build_layout(self) -> None:
        self.root.configure(bg=COLORS["background"])

        header = tk.Frame(self.root, bg=COLORS["primary"], height=82)
        header.pack(fill="x")
        header.pack_propagate(False)

        self.logo_photo = self._load_logo(54)
        if self.logo_photo:
            tk.Label(header, image=self.logo_photo, bg=COLORS["primary"]).pack(
                side="left", padx=(24, 12)
            )

        title_box = tk.Frame(header, bg=COLORS["primary"])
        title_box.pack(side="left", fill="y", pady=12)

        self.company_label = tk.Label(
            title_box,
            text=self.config.get("company_name") or "Sua empresa",
            bg=COLORS["primary"],
            fg="white",
            font=("Segoe UI", 16, "bold"),
            anchor="w",
        )
        self.company_label.pack(anchor="w")

        tk.Label(
            title_box,
            text="Sistema de clientes e pedidos - V2.0",
            bg=COLORS["primary"],
            fg="#D7FFFA",
            font=("Segoe UI", 10),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            header,
            text="Banco local preparado para nuvem",
            bg=COLORS["primary"],
            fg="#D7FFFA",
            font=("Segoe UI", 10),
        ).pack(side="right", padx=24)

        body = tk.Frame(self.root, bg=COLORS["background"])
        body.pack(fill="both", expand=True)

        sidebar = tk.Frame(body, bg=COLORS["sidebar"], width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        self._build_sidebar(sidebar)

        self.content = tk.Frame(body, bg=COLORS["background"])
        self.content.pack(side="left", fill="both", expand=True)
        self._build_dashboard()

    def _build_sidebar(self, parent: tk.Frame) -> None:
        tk.Label(
            parent,
            text="Operacoes",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(22, 8))

        self._sidebar_button(parent, "+  Cadastrar cliente", self.open_new_client)
        self._sidebar_button(parent, "?  Buscar cliente", self.open_client_search)
        self._sidebar_button(parent, "PDF  Anexar pedido", self.select_client_for_order)
        self._sidebar_button(parent, "#  Buscar pedido", self.open_order_search)

        tk.Label(
            parent,
            text="Arquivos",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(22, 8))

        self._sidebar_button(parent, "XLS  Exportar clientes", self.export_clients)
        self._sidebar_button(parent, "XLS  Exportar pedidos", self.export_orders)
        self._sidebar_button(parent, "BK  Fazer backup", self.create_backup)
        self._sidebar_button(parent, "BK  Restaurar backup", self.restore_backup)

        tk.Label(
            parent,
            text="Sistema",
            bg=COLORS["sidebar"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(22, 8))

        self._sidebar_button(parent, "CFG  Configuracoes", self.open_settings)
        self._sidebar_button(parent, "X  Sair", self.root.destroy, danger=True)

    def _sidebar_button(
        self,
        parent: tk.Frame,
        text: str,
        command,
        danger: bool = False,
    ) -> None:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            anchor="w",
            bg=COLORS["danger"] if danger else COLORS["surface"],
            fg="white" if danger else COLORS["text"],
            activebackground=COLORS["primary_dark"] if not danger else "#991B1B",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
        )
        button.pack(fill="x", padx=14, pady=4)

    def _build_dashboard(self) -> None:
        for child in self.content.winfo_children():
            child.destroy()

        top = tk.Frame(self.content, bg=COLORS["background"])
        top.pack(fill="x", padx=28, pady=(24, 12))

        tk.Label(
            top,
            text="Dashboard",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")

        tk.Label(
            top,
            text="Visao geral dos clientes, pedidos e ultimos registros.",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        cards = tk.Frame(self.content, bg=COLORS["background"])
        cards.pack(fill="x", padx=28, pady=10)
        cards.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cards")

        self._stat_card(cards, 0, "clientes", "Clientes cadastrados")
        self._stat_card(cards, 1, "pedidos", "Pedidos cadastrados")
        self._stat_card(cards, 2, "ultimo_cliente", "Ultimo cliente")
        self._stat_card(cards, 3, "ultimo_pedido", "Ultimo pedido")

        actions = tk.Frame(self.content, bg=COLORS["surface"], highlightthickness=1)
        actions.configure(highlightbackground=COLORS["border"])
        actions.pack(fill="x", padx=28, pady=(18, 0))

        tk.Label(
            actions,
            text="Atalhos principais",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI", 13, "bold"),
        ).pack(anchor="w", padx=18, pady=(16, 8))

        row = tk.Frame(actions, bg=COLORS["surface"])
        row.pack(fill="x", padx=14, pady=(0, 16))

        self._action_button(row, "+ Cadastrar", self.open_new_client, "success")
        self._action_button(row, "? Buscar cliente", self.open_client_search, "info")
        self._action_button(row, "PDF Anexar", self.select_client_for_order, "primary")
        self._action_button(row, "BK Backup", self.create_backup, "warning")

    def _stat_card(self, parent: tk.Frame, column: int, key: str, title: str) -> None:
        card = tk.Frame(
            parent,
            bg=COLORS["surface"],
            highlightthickness=1,
            highlightbackground=COLORS["border"],
        )
        card.grid(row=0, column=column, sticky="nsew", padx=6)

        tk.Label(
            card,
            text=title,
            bg=COLORS["surface"],
            fg=COLORS["muted"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(14, 4))

        value = tk.Label(
            card,
            text="-",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            font=("Segoe UI", 18, "bold"),
            anchor="w",
            wraplength=220,
            justify="left",
        )
        value.pack(fill="x", padx=16, pady=(0, 14))
        self.dashboard_labels[key] = value

    def _action_button(self, parent: tk.Frame, text: str, command, bootstyle: str) -> None:
        kwargs = {"text": text, "command": command, "width": 18}
        if HAS_BOOTSTRAP:
            kwargs["bootstyle"] = bootstyle
        button = ttk.Button(parent, **kwargs)
        button.pack(side="left", padx=6)

    def refresh_dashboard(self) -> None:
        data = database.dashboard_data()
        self.dashboard_labels["clientes"].configure(text=str(data["clientes"]))
        self.dashboard_labels["pedidos"].configure(text=str(data["pedidos"]))

        ultimo_cliente = data["ultimo_cliente"]
        if ultimo_cliente:
            self.dashboard_labels["ultimo_cliente"].configure(
                text=f"{ultimo_cliente['nome']}\n{ultimo_cliente['data_cadastro'] or ''}"
            )
        else:
            self.dashboard_labels["ultimo_cliente"].configure(text="Nenhum cliente")

        ultimo_pedido = data["ultimo_pedido"]
        if ultimo_pedido:
            self.dashboard_labels["ultimo_pedido"].configure(
                text=f"{ultimo_pedido['numero_pedido']}\n{ultimo_pedido['cliente_nome'] or ''}"
            )
        else:
            self.dashboard_labels["ultimo_pedido"].configure(text="Nenhum pedido")

    def new_window(self, title: str):
        window = ttk.Toplevel(self.root) if HAS_BOOTSTRAP else tk.Toplevel(self.root)
        window.title(title)
        self._set_icon(window)
        self._zoom(window)

        frame = ttk.Frame(window, padding=24)
        frame.pack(fill="both", expand=True)
        return window, frame

    def _form_row(self, parent, label: str, row: int, value: str = "", width: int = 46):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", padx=(0, 10), pady=8)
        entry = ttk.Entry(parent, width=width)
        entry.grid(row=row, column=1, sticky="ew", pady=8)
        if value:
            entry.insert(0, value)
        return entry

    def _apply_mask(self, entry, formatter) -> None:
        state = {"updating": False}

        def update(_event=None):
            if state["updating"]:
                return
            state["updating"] = True
            formatted = formatter(entry.get())
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
            entry.icursor(tk.END)
            state["updating"] = False

        entry.bind("<KeyRelease>", update)

    def open_new_client(self) -> None:
        self.open_client_form()

    def open_client_form(self, cliente_id: int | None = None) -> None:
        cliente = cliente_service.obter_cliente(cliente_id) if cliente_id else None
        if cliente_id and not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado.", parent=self.root)
            return

        title = "Editar Cliente" if cliente else "Cadastrar Cliente"
        window, frame = self.new_window(title)

        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            frame,
            text="Preencha os dados principais do cliente.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 18))

        form = ttk.Frame(frame)
        form.pack(anchor="n", pady=8)
        form.columnconfigure(1, weight=1)

        entry_nome = self._form_row(form, "Nome", 0, cliente["nome"] if cliente else "")
        entry_doc = self._form_row(
            form,
            "CPF/CNPJ",
            1,
            cliente_service.formatar_documento(cliente["cpf_cnpj"]) if cliente else "",
        )

        # Checkbox para permitir cadastro sem documento (na mesma linha do CPF/CNPJ)
        sem_doc_var = tk.BooleanVar(master=form, value=False)
        if cliente and not cliente_service.limpar_documento(cliente.get("cpf_cnpj")):
            sem_doc_var.set(True)

        def _toggle_doc():
            if sem_doc_var.get():
                entry_doc.delete(0, tk.END)
                entry_doc.config(state="disabled")
            else:
                entry_doc.config(state="normal")

        chk = ttk.Checkbutton(form, text="Sem CPF/CNPJ", variable=sem_doc_var, command=_toggle_doc)
        # colocar o checkbox na mesma linha do campo documento, coluna 2
        chk.grid(row=1, column=2, sticky="w", padx=(8, 0))
        entry_tel = self._form_row(
            form,
            "Telefone",
            2,
            cliente_service.formatar_telefone(cliente["telefone"]) if cliente else "",
        )
        entry_endereco = self._form_row(form, "Endereço", 3, cliente["endereco"] if cliente else "")

        # Aplicar estado inicial do checkbox (desabilitar campo documento se necessário)
        _toggle_doc()

        self._apply_mask(entry_doc, cliente_service.formatar_documento_parcial)
        self._apply_mask(entry_tel, cliente_service.formatar_telefone_parcial)

        buttons = ttk.Frame(frame)
        buttons.pack(anchor="n", pady=18)

        def salvar() -> None:
            nome = entry_nome.get()
            documento = entry_doc.get()
            telefone = entry_tel.get()
            endereco = entry_endereco.get()
            permitir_sem_doc = bool(sem_doc_var.get())

            try:
                logger.info("Salvar cliente - nome=%s permitir_sem_doc=%s", nome, permitir_sem_doc)
                if cliente:
                    permitir = False
                    if cliente_service.existe_nome(nome, cliente_id):
                        permitir = messagebox.askyesno(
                            "Nome ja existe",
                            "Ja existe outro cliente com esse nome. Deseja continuar mesmo assim?",
                            parent=window,
                        )
                        if not permitir:
                            return
                    cliente_service.atualizar_cliente(
                        cliente_id,
                        nome,
                        documento,
                        telefone,
                        endereco,
                        permitir_nome_duplicado=permitir,
                        permitir_sem_documento=permitir_sem_doc,
                    )
                    mensagem = "Cliente atualizado com sucesso."
                else:
                    cliente_service.criar_cliente(nome, documento, telefone, endereco, permitir_sem_documento=permitir_sem_doc)
                    mensagem = "Cliente cadastrado com sucesso."
            except cliente_service.ValidationError as exc:
                logger.warning("Validação falhou ao salvar cliente: %s", exc)
                messagebox.showerror("Erro", str(exc), parent=window)
                return
            except Exception as exc:
                logger.exception("Erro inesperado ao salvar cliente")
                messagebox.showerror("Erro inesperado", f"Ocorreu um erro: {exc}", parent=window)
                return

            messagebox.showinfo("Sucesso", mensagem, parent=window)
            window.destroy()
            self.refresh_dashboard()

        self._action_button(buttons, "Salvar", salvar, "success")
        self._action_button(buttons, "Voltar", window.destroy, "secondary")
        entry_nome.focus()

    def open_client_search(self, callback=None) -> None:
        window, frame = self.new_window("Buscar Cliente")
        ttk.Label(frame, text="Buscar Cliente", style="Title.TLabel").pack(anchor="w")

        search_entry = ttk.Entry(frame)
        search_entry.pack(fill="x", pady=(12, 14))

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(
            table_frame,
            columns=("nome", "documento", "telefone", "endereco"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        tree.heading("nome", text="Nome")
        tree.heading("documento", text="CPF/CNPJ")
        tree.heading("telefone", text="Telefone")
        tree.heading("endereco", text="Endereço")
        tree.column("nome", width=300)
        tree.column("documento", width=160)
        tree.column("telefone", width=150)
        tree.column("endereco", width=360)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=tree.yview)

        search_job = {"id": None}

        def selected_cliente_id() -> int | None:
            selection = tree.selection()
            if not selection:
                return None
            return int(selection[0])

        def render(rows) -> None:
            tree.delete(*tree.get_children())
            for cliente in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(cliente["id"]),
                    values=(
                        cliente["nome"],
                        cliente_service.formatar_documento(cliente["cpf_cnpj"]),
                        cliente_service.formatar_telefone(cliente["telefone"]),
                        cliente["endereco"] or "",
                    ),
                )

        def filtrar() -> None:
            search_job["id"] = None
            render(cliente_service.buscar_cliente_inteligente(search_entry.get()))

        def agendar_busca(_event=None) -> None:
            if search_job["id"]:
                window.after_cancel(search_job["id"])
            search_job["id"] = window.after(220, filtrar)

        def abrir(_event=None) -> None:
            cliente_id = selected_cliente_id()
            if cliente_id is None:
                return
            window.destroy()
            if callback:
                callback(cliente_id)
            else:
                self.open_client_panel(cliente_id)

        search_entry.bind("<KeyRelease>", agendar_busca)
        tree.bind("<Double-1>", abrir)

        buttons = ttk.Frame(frame)
        buttons.pack(anchor="e", pady=12)
        self._action_button(buttons, "Abrir", abrir, "primary")
        self._action_button(buttons, "Voltar", window.destroy, "secondary")

        render(cliente_service.listar_clientes())
        search_entry.focus()

    def open_client_panel(self, cliente_id: int) -> None:
        cliente = cliente_service.obter_cliente(cliente_id)
        if not cliente:
            messagebox.showerror("Erro", "Cliente não encontrado.", parent=self.root)
            return

        window, frame = self.new_window("Painel do Cliente")

        header = ttk.Frame(frame)
        header.pack(fill="x")

        ttk.Label(header, text=cliente["nome"], style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text=(
                f"CPF/CNPJ: {cliente_service.formatar_documento(cliente['cpf_cnpj'])} | "
                f"Telefone: {cliente_service.formatar_telefone(cliente['telefone'])}"
            ),
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 0))
        ttk.Label(header, text=f"Endereço: {cliente['endereco'] or ''}", style="Subtitle.TLabel").pack(
            anchor="w", pady=(2, 10)
        )

        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=8)
        self._action_button(actions, "Abrir pasta", lambda: self.open_client_folder(cliente), "secondary")
        self._action_button(actions, "PDF Anexar pedido", lambda: self.open_order_attach(cliente_id), "primary")
        self._action_button(actions, "Editar", lambda: self.open_client_form(cliente_id), "warning")
        self._action_button(actions, "Excluir", lambda: self.delete_client(cliente_id, window), "danger")

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True, pady=(16, 0))

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(
            table_frame,
            columns=("numero", "data", "pdf"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        tree.heading("numero", text="Numero do pedido")
        tree.heading("data", text="Data")
        tree.heading("pdf", text="PDF")
        tree.column("numero", width=180)
        tree.column("data", width=170)
        tree.column("pdf", width=560)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=tree.yview)

        pedidos = pedido_service.listar_pedidos_cliente(cliente_id)
        for pedido in pedidos:
            tree.insert(
                "",
                "end",
                iid=str(pedido["id"]),
                values=(
                    pedido["numero_pedido"],
                    pedido["data_pedido"],
                    pedido["caminho_pdf"],
                ),
            )

        def abrir_pdf(_event=None) -> None:
            selection = tree.selection()
            if not selection:
                return
            pedido = pedido_service.obter_pedido(int(selection[0]))
            if pedido:
                self.open_file(pedido["caminho_pdf"], window)

        tree.bind("<Double-1>", abrir_pdf)

        bottom = ttk.Frame(frame)
        bottom.pack(anchor="e", pady=12)
        self._action_button(bottom, "Abrir PDF", abrir_pdf, "primary")
        self._action_button(bottom, "Voltar", window.destroy, "secondary")

    def open_client_folder(self, cliente) -> None:
        pasta_pdfs = self.config.get("pdf_folder")
        if not pasta_pdfs:
            messagebox.showwarning("Aviso", "Configure a pasta padrao de PDFs primeiro.", parent=self.root)
            return

        pasta_cliente = pedido_service.pasta_do_cliente(cliente["nome"], pasta_pdfs)
        self.open_file(pasta_cliente, self.root)

    def delete_client(self, cliente_id: int, parent_window=None) -> None:
        cliente = cliente_service.obter_cliente(cliente_id)
        if not cliente:
            messagebox.showerror("Erro", "Cliente nao encontrado.", parent=parent_window or self.root)
            return

        total_pedidos = cliente_service.total_pedidos_cliente(cliente_id)
        resumo = (
            f"Nome: {cliente['nome']}\n"
            f"CPF/CNPJ: {cliente_service.formatar_documento(cliente['cpf_cnpj'])}\n"
            f"Pedidos vinculados: {total_pedidos}"
        )

        confirmar = messagebox.askyesno(
            "Confirmar exclusao",
            f"Tem certeza que deseja excluir este cliente?\n\n{resumo}",
            parent=parent_window or self.root,
        )
        if not confirmar:
            return

        if total_pedidos:
            confirmar_final = messagebox.askyesno(
                "Confirmacao final",
                "Todos os pedidos vinculados tambem serao excluidos. Deseja continuar?",
                parent=parent_window or self.root,
            )
            if not confirmar_final:
                return

        cliente_service.excluir_cliente(cliente_id)
        messagebox.showinfo("Sucesso", "Cliente excluido com sucesso.", parent=parent_window or self.root)
        if parent_window:
            parent_window.destroy()
        self.refresh_dashboard()

    def select_client_for_order(self) -> None:
        self.open_client_search(callback=self.open_order_attach)

    def open_order_attach(self, cliente_id: int) -> None:
        cliente = cliente_service.obter_cliente(cliente_id)
        if not cliente:
            messagebox.showerror("Erro", "Cliente nao encontrado.", parent=self.root)
            return

        window, frame = self.new_window("Anexar Pedido")
        tk.Label(frame, text="Anexar Pedido", style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=f"Cliente: {cliente['nome']}", style="Subtitle.TLabel").pack(
            anchor="w", pady=(2, 18)
        )

        form = ttk.Frame(frame)
        form.pack(anchor="n", pady=8)
        entry_numero = self._form_row(form, "Numero do pedido", 0)

        # Se o cliente nao possui CPF/CNPJ, pedir confirmacao antes de prosseguir
        if not cliente_service.limpar_documento(cliente.get("cpf_cnpj")):
            continuar = messagebox.askyesno(
                "Aviso",
                "Cliente não possui CPF/CNPJ. Deseja continuar?",
                parent=self.root,
            )
            if not continuar:
                return


        def selecionar_pdf() -> None:
            numero = entry_numero.get().strip()
            if not numero:
                messagebox.showerror("Erro", "Informe o número do pedido.", parent=window)
                return

            pasta_pdfs = self.config.get("pdf_folder")
            if not pasta_pdfs or not Path(pasta_pdfs).exists():
                pasta_pdfs = filedialog.askdirectory(
                    title="Selecione a pasta padrao de PDFs",
                    parent=window,
                )
                if not pasta_pdfs:
                    return
                self.config["pdf_folder"] = pasta_pdfs
                save_config(self.config)

            arquivo = filedialog.askopenfilename(
                title="Selecione o PDF do pedido",
                initialdir=pasta_pdfs,
                filetypes=[("Arquivos PDF", "*.pdf")],
                parent=window,
            )
            if not arquivo:
                return

            try:
                _pedido_id, destino = pedido_service.anexar_pdf(
                    cliente_id,
                    numero,
                    arquivo,
                    pasta_pdfs,
                )
            except cliente_service.ValidationError as exc:
                messagebox.showerror("Erro", str(exc), parent=window)
                return

            messagebox.showinfo("Sucesso", f"Pedido anexado em:\n{destino}", parent=window)
            window.destroy()
            self.refresh_dashboard()

        buttons = ttk.Frame(frame)
        buttons.pack(anchor="n", pady=18)
        self._action_button(buttons, "Selecionar PDF e salvar", selecionar_pdf, "primary")
        self._action_button(buttons, "Voltar", window.destroy, "secondary")
        entry_numero.focus()

    def open_order_search(self) -> None:
        window, frame = self.new_window("Buscar Pedido")
        ttk.Label(frame, text="Buscar Pedido", style="Title.TLabel").pack(anchor="w")

        search_entry = ttk.Entry(frame)
        search_entry.pack(fill="x", pady=(12, 14))

        table_frame = ttk.Frame(frame)
        table_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        tree = ttk.Treeview(
            table_frame,
            columns=("cliente", "numero", "data", "pdf"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse",
        )
        tree.heading("cliente", text="Cliente")
        tree.heading("numero", text="Numero do pedido")
        tree.heading("data", text="Data")
        tree.heading("pdf", text="PDF")
        tree.column("cliente", width=280)
        tree.column("numero", width=180)
        tree.column("data", width=170)
        tree.column("pdf", width=520)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=tree.yview)

        search_job = {"id": None}

        def render(rows) -> None:
            tree.delete(*tree.get_children())
            for pedido in rows:
                tree.insert(
                    "",
                    "end",
                    iid=str(pedido["id"]),
                    values=(
                        pedido["cliente_nome"] or "",
                        pedido["numero_pedido"] or "",
                        pedido["data_pedido"] or "",
                        pedido["caminho_pdf"] or "",
                    ),
                )

        def filtrar() -> None:
            search_job["id"] = None
            render(pedido_service.buscar_pedidos(search_entry.get()))

        def agendar_busca(_event=None) -> None:
            if search_job["id"]:
                window.after_cancel(search_job["id"])
            search_job["id"] = window.after(220, filtrar)

        def abrir_pdf(_event=None) -> None:
            selection = tree.selection()
            if not selection:
                return
            pedido = pedido_service.obter_pedido(int(selection[0]))
            if pedido:
                self.open_file(pedido["caminho_pdf"], window)

        search_entry.bind("<KeyRelease>", agendar_busca)
        tree.bind("<Double-1>", abrir_pdf)

        buttons = ttk.Frame(frame)
        buttons.pack(anchor="e", pady=12)
        self._action_button(buttons, "Abrir PDF", abrir_pdf, "primary")
        self._action_button(buttons, "Voltar", window.destroy, "secondary")

        render(pedido_service.buscar_pedidos(""))
        search_entry.focus()

    def create_backup(self) -> None:
        pasta = self.config.get("backup_folder")
        if not pasta:
            pasta = filedialog.askdirectory(title="Selecione a pasta de backup", parent=self.root)
            if not pasta:
                return
            self.config["backup_folder"] = pasta
            save_config(self.config)

        destino = backup_service.caminho_backup_do_dia(pasta)
        substituir = False
        if destino.exists():
            substituir = messagebox.askyesno(
                "Backup existente",
                f"Ja existe um backup de hoje:\n{destino}\n\nDeseja substituir?",
                parent=self.root,
            )
            if not substituir:
                return

        try:
            gerado = backup_service.criar_backup(pasta, substituir=substituir)
        except OSError as exc:
            messagebox.showerror("Erro", f"Nao foi possivel criar o backup.\n{exc}", parent=self.root)
            return

        messagebox.showinfo("Backup concluido", f"Backup gerado:\n{gerado}", parent=self.root)

    def restore_backup(self) -> None:
        pasta = self.config.get("backup_folder") or str(Path.cwd())
        arquivo = filedialog.askopenfilename(
            title="Selecione o backup",
            initialdir=pasta,
            filetypes=[("Banco SQLite", "*.db")],
            parent=self.root,
        )
        if not arquivo:
            return

        confirmar = messagebox.askyesno(
            "Restaurar backup",
            "A restauracao vai substituir o banco atual. Deseja continuar?",
            parent=self.root,
        )
        if not confirmar:
            return

        try:
            backup_service.restaurar_backup(arquivo)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Erro", f"Nao foi possivel restaurar o backup.\n{exc}", parent=self.root)
            return

        messagebox.showinfo("Backup restaurado", "Backup restaurado com sucesso.", parent=self.root)
        self.refresh_dashboard()

    def export_clients(self) -> None:
        pasta = filedialog.askdirectory(title="Selecione onde salvar clientes.xlsx", parent=self.root)
        if not pasta:
            return

        try:
            destino = excel_service.exportar_clientes(pasta)
        except (OSError, RuntimeError) as exc:
            messagebox.showerror("Erro", f"Nao foi possivel exportar clientes.\n{exc}", parent=self.root)
            return

        messagebox.showinfo("Exportacao concluida", f"Arquivo gerado:\n{destino}", parent=self.root)

    def export_orders(self) -> None:
        pasta = filedialog.askdirectory(title="Selecione onde salvar pedidos.xlsx", parent=self.root)
        if not pasta:
            return

        try:
            destino = excel_service.exportar_pedidos(pasta)
        except (OSError, RuntimeError) as exc:
            messagebox.showerror("Erro", f"Nao foi possivel exportar pedidos.\n{exc}", parent=self.root)
            return

        messagebox.showinfo("Exportacao concluida", f"Arquivo gerado:\n{destino}", parent=self.root)

    def open_settings(self) -> None:
        window, frame = self.new_window("Configuracoes")
        ttk.Label(frame, text="Configuracoes", style="Title.TLabel").pack(anchor="w")

        form = ttk.Frame(frame)
        form.pack(anchor="n", pady=18)
        form.columnconfigure(1, weight=1)

        entry_pdf = self._form_row(form, "Pasta padrao de PDFs", 0, self.config.get("pdf_folder", ""), 58)
        ttk.Button(
            form,
            text="Selecionar",
            command=lambda: self._select_folder(entry_pdf, window),
        ).grid(row=0, column=2, padx=(8, 0), pady=8)

        entry_backup = self._form_row(
            form,
            "Pasta padrao de backup",
            1,
            self.config.get("backup_folder", ""),
            58,
        )
        ttk.Button(
            form,
            text="Selecionar",
            command=lambda: self._select_folder(entry_backup, window),
        ).grid(row=1, column=2, padx=(8, 0), pady=8)

        ttk.Label(form, text="Tema visual").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=8)
        combo_theme = ttk.Combobox(
            form,
            values=["flatly", "cosmo", "litera", "minty", "pulse", "superhero", "darkly"],
            width=55,
            state="readonly",
        )
        combo_theme.set(self.config.get("theme") or "flatly")
        combo_theme.grid(row=2, column=1, sticky="ew", pady=8)

        entry_company = self._form_row(
            form,
            "Nome da empresa",
            3,
            self.config.get("company_name", ""),
            58,
        )
        entry_company_doc = self._form_row(
            form,
            "CPF/CNPJ da empresa",
            4,
            self.config.get("company_document", ""),
            58,
        )
        entry_company_phone = self._form_row(
            form,
            "Telefone da empresa",
            5,
            self.config.get("company_phone", ""),
            58,
        )
        entry_company_address = self._form_row(
            form,
            "Endereco da empresa",
            6,
            self.config.get("company_address", ""),
            58,
        )

        self._apply_mask(entry_company_doc, cliente_service.formatar_documento_parcial)
        self._apply_mask(entry_company_phone, cliente_service.formatar_telefone_parcial)

        def salvar() -> None:
            self.config = save_config(
                {
                    "pdf_folder": entry_pdf.get().strip(),
                    "backup_folder": entry_backup.get().strip(),
                    "theme": combo_theme.get().strip() or "flatly",
                    "company_name": entry_company.get().strip() or "Sua empresa",
                    "company_document": entry_company_doc.get().strip(),
                    "company_phone": entry_company_phone.get().strip(),
                    "company_address": entry_company_address.get().strip(),
                }
            )
            database.atualizar_empresa_padrao(self.config)
            if self.company_label:
                self.company_label.configure(text=self.config.get("company_name") or "Sua empresa")
            messagebox.showinfo(
                "Configuracoes salvas",
                "Configuracoes salvas com sucesso. O tema visual completo sera aplicado ao reiniciar.",
                parent=window,
            )
            window.destroy()

        buttons = ttk.Frame(frame)
        buttons.pack(anchor="n", pady=18)
        self._action_button(buttons, "Salvar", salvar, "success")
        self._action_button(buttons, "Voltar", window.destroy, "secondary")

    def _select_folder(self, entry, parent) -> None:
        pasta = filedialog.askdirectory(parent=parent)
        if not pasta:
            return
        entry.delete(0, tk.END)
        entry.insert(0, pasta)

    def open_file(self, path_value: str | os.PathLike[str], parent=None) -> None:
        path = Path(path_value)
        if not path.exists():
            messagebox.showerror("Erro", f"Arquivo ou pasta nao encontrado:\n{path}", parent=parent or self.root)
            return

        try:
            os.startfile(str(path))
        except AttributeError:
            messagebox.showinfo("Abrir arquivo", f"Abra manualmente:\n{path}", parent=parent or self.root)
        except OSError as exc:
            messagebox.showerror("Erro", f"Nao foi possivel abrir.\n{exc}", parent=parent or self.root)

    def run(self) -> None:
        self.root.mainloop()


def iniciar_interface() -> None:
    SistemaApp().run()
