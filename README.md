# Sistema de Gerenciamento de Clientes e Pedidos

Versao 2.0 do sistema desktop para cadastro de clientes, pedidos em PDF,
backup local, exportacao Excel e preparacao para futura nuvem.

## Principais recursos

- Dashboard com totais e ultimos registros.
- Cadastro, edicao, exclusao e busca instantanea de clientes.
- Mascara automatica para CPF, CNPJ e telefone.
- Anexo de pedidos em PDF por cliente.
- Busca de pedidos com abertura por duplo clique.
- Backup manual em `backup_YYYY_MM_DD.db`.
- Restauracao de backup local.
- Exportacao de `clientes.xlsx` e `pedidos.xlsx`.
- Tela de configuracoes para pastas, tema e dados da empresa.
- Estrutura preparada com tabelas `empresas`, `usuarios` e campo `empresa_id`.

## Estrutura

```text
main.py
database.py
clientes.py
pedidos.py
backup.py
excel.py
interface.py
config.py
assets/
    logo.ico
    logo.png
```

## Dependencias

```text
ttkbootstrap
pillow
openpyxl
pyinstaller
```

## Empacotamento e instalador

1. Gere o executável com PyInstaller:
   ```powershell
   python -m pyinstaller --clean --noconsole --onefile --icon assets/logo.ico --add-data "assets/logo.png;assets" --add-data "assets/logo.ico;assets" main.py
   ```
2. O instalador deve copiar o EXE e os assets para `Program Files`.
3. O banco de dados e as configuracoes agora sao salvos em `%LOCALAPPDATA%\SistemaCRUD`, por isso a atualizacao mantem os dados antigos.
4. Se uma versao antiga estiver instalada com o banco no mesmo diretorio do executavel, o sistema tenta migrar esse banco para o novo local de dados automaticamente.

## Fora do escopo da V2.0

Login, banco online, servidor, sincronizacao, aplicativo Android e atualizacao
automatica ficam planejados para a V3.0.
