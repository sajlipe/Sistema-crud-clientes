# Changelog

Todas as mudanças notáveis deste projeto estão documentadas neste arquivo.

## [2.0] - 2026-06-02

### 🆕 Adicionado

- **Suporte a clientes sem CPF/CNPJ** — novo checkbox no formulário de clientes
- **Armazenamento em `%LOCALAPPDATA%\SistemaCRUD`** — dados separados por usuário Windows
- **Migração automática de dados** — detecta banco antigo e move para novo local sem perda de dados
- **Instalador Windows (Inno Setup)** — executável distribuível para instalação sem Python
- **Validação melhorada de documentos** — algoritmos corretos para verificação de CPF e CNPJ
- **Tratamento de NULL no banco** — CPF/CNPJ vazios são armazenados como NULL em vez de string vazia
- **Logging estruturado** — arquivo `app.log` para debug e auditoria

### 🔧 Melhorado

- Interface mais limpa e responsiva
- Melhor tratamento de erros em operações de banco de dados
- Otimização de queries SQL
- Máscaras de entrada melhoradas para CPF, CNPJ e telefone
- Estrutura preparada para multi-empresa (tabelas `empresas` e `usuarios` prontas)

### 🐛 Corrigido

- UNIQUE constraint em `cpf_cnpj` agora tolera múltiplos NULL
- Compatibilidade com instâncias antigas mantida através de migração automática
- Problema de permissões em diretórios do sistema

### ⚠️ Mudanças Importantes

- **Localização do banco de dados mudou** — agora em `%LOCALAPPDATA%\SistemaCRUD/`
- Bancos antigos são migrados automaticamente na primeira execução

---

## [1.1] - 2026-05-XX

### 🐛 Corrigido

- Bug na exclusão de clientes

### 🔧 Melhorado

- Performance ao listar clientes

---

## [1.0] - 2026-XX-XX

### 🆕 Adicionado

- Primeira versão funcional do sistema CRUD
- Cadastro, edição e exclusão de clientes
- Gerenciamento de pedidos com anexos em PDF
- Backup e restauração de banco de dados
- Exportação de dados para Excel
- Interface Tkinter com tema personalizado
- Busca instantânea de clientes e pedidos

---

## Versões Futuras (Planejadas)

### v3.0 (Planejado)

- Login e autenticação de usuários
- Sincronização com banco de dados na nuvem
- Servidor central para múltiplas instâncias
- Aplicativo mobile (Android/iOS)
- Atualização automática de versões
- Suporte a múltiplas empresas
