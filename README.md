# Sistema de Gerenciamento de Clientes e Pedidos

Versão 2.0 do sistema desktop para cadastro de clientes, pedidos em PDF, backup local, exportação Excel e preparação para futura nuvem.

## 🆕 Novidades na Versão 2.0

- **Suporte a clientes sem CPF/CNPJ** — checkbox opcional no formulário.
- **Armazenamento em `%LOCALAPPDATA%\SistemaCRUD`** — dados separados por usuário Windows.
- **Migração automática** — detecta banco antigo e move para novo local.
- **Instalador Windows** — executável distribuível via GitHub Release.
- **Validação melhorada** de CPF e CNPJ com algoritmos corretos.

## Principais recursos

- Dashboard com totais e últimos registros.
- Cadastro, edição, exclusão e busca instantânea de clientes.
- Máscara automática para CPF, CNPJ e telefone.
- Anexo de pedidos em PDF por cliente.
- Busca de pedidos com abertura por duplo clique.
- Backup manual em `backup_YYYY_MM_DD.db`.
- Restauração de backup local.
- Exportação de `clientes.xlsx` e `pedidos.xlsx`.
- Tela de configurações para pastas, tema e dados da empresa.
- Estrutura preparada com tabelas `empresas`, `usuarios` e campo `empresa_id`.

## Instalação

### Opção 1: Usando o Instalador (Recomendado)

1. Baixe `SistemaCRUD_Installer_2.0.exe` em [Releases](https://github.com/seu-usuario/SistemaCRUD/releases).
2. Execute o instalador.
3. O aplicativo será instalado em `Program Files\SistemaCRUD`.
4. Se houver versão anterior, os dados são migrados automaticamente.

### Opção 2: Desenvolvimento Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/SistemaCRUD.git
   cd SistemaCRUD
   ```

2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

3. Execute o aplicativo:
   ```powershell
   python main.py
   ```

## Estrutura

```text
main.py                  # Entrypoint da aplicação
database.py              # Schema e inicialização do banco
clientes.py              # CRUD e validação de clientes
pedidos.py               # Gerenciamento de pedidos
interface.py             # Interface Tkinter
excel.py                 # Exportação para Excel
backup.py                # Funções de backup
config.py                # Gerenciamento de configurações e caminhos
assets/
    logo.ico             # Ícone da aplicação
    logo.png             # Logo da aplicação
requirements.txt         # Dependências Python
```

## Dependências

```text
ttkbootstrap>=1.6.0      # Tema moderno para Tkinter
pillow>=10.0.0           # Processamento de imagens
openpyxl>=3.1.0          # Exportação Excel
pyinstaller>=6.0.0       # Build de executável (apenas para packaging)
```

Instale com:
```powershell
pip install -r requirements.txt
```

## Build e Packaging

Para gerar o executável e instalador, use os scripts locais (não estão no repositório, mas estão no seu PC):

### Gerar Executável (PyInstaller)

```powershell
python -m PyInstaller --clean --noconsole --onefile `
  --name SistemaCRUD `
  --icon assets/logo.ico `
  --add-data "assets/logo.png;assets" `
  --add-data "assets/logo.ico;assets" `
  main.py
```

Resultado: `dist/SistemaCRUD.exe`

### Gerar Instalador (Inno Setup)

Requer Inno Setup 6 instalado.

O instalador gerado fica em `installer/SistemaCRUD_Installer_2.0.exe` e é distribuído como artefato de release no GitHub.

