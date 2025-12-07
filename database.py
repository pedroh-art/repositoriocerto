# database.py
import sqlite3
import bcrypt
import os

def init_db():
    """
    Inicializa a conexão com o banco de dados e cria todas as tabelas necessárias.
    Retorna o objeto de conexão.
    """
    try:
        conn = sqlite3.connect("equipe.db", check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        _create_tables(conn)
        return conn
    except Exception as e:
        raise RuntimeError(f"Erro ao inicializar o banco de dados: {e}")

def _create_tables(conn):
    """
    Cria todas as tabelas do sistema, se ainda não existirem.
    """
    c = conn.cursor()

    # Tabela: integrantes
    c.execute("""
        CREATE TABLE IF NOT EXISTS integrantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    """)

    # Tabela: atribuicoes
    c.execute("""
        CREATE TABLE IF NOT EXISTS atribuicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            integrante_id INTEGER,
            setor TEXT NOT NULL,
            funcao TEXT NOT NULL,
            UNIQUE(integrante_id, setor, funcao),
            FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE CASCADE
        )
    """)

    # Tabela: usuarios (para login)
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha BLOB NOT NULL,  -- Agora é BLOB para bcrypt
            tipo TEXT NOT NULL CHECK(tipo IN ('administrador', 'membro'))
        )
    """)

    # Tabela: tarefas (Kanban)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL CHECK(status IN ('to_do', 'doing', 'done')),
            integrante_id INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(integrante_id) REFERENCES integrantes(id) ON DELETE SET NULL
        )
    """)

    # Tabela: compromissos oficiais
    c.execute("""
        CREATE TABLE IF NOT EXISTS compromissos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            data DATE NOT NULL,
            horario_inicio TEXT NOT NULL,
            horario_fim TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Garantir que o usuário administrador "pedro" exista (com senha segura)
    c.execute("SELECT * FROM usuarios WHERE usuario = 'pedro'")
    if not c.fetchone():
        # Carrega senha do ambiente (obrigatória em produção)
        senha_admin = os.getenv("ADMIN_PASSWORD")
        if senha_admin is None:
            raise RuntimeError("Variável de ambiente ADMIN_PASSWORD não definida!")
        senha_hash = bcrypt.hashpw(senha_admin.encode('utf-8'), bcrypt.gensalt())
        c.execute(
            "INSERT INTO usuarios (usuario, senha, tipo) VALUES (?, ?, ?)",
            ("pedro", senha_hash, "administrador")
        )

    conn.commit()