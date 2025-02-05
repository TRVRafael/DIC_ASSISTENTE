import os

def read_message_file(filename: str) -> str:
    """Lê o conteúdo do arquivo"""
    try:
        with open(f"{filename}", "r", encoding="utf-8") as file:
            content = file.read()
        return content
    except Exception as e:
        return f"❌ Erro ao ler o arquivo: {str(e)}"
        
def write_message_file(filename: str, message : str) -> str:
    """Escreva a mensagem no arquivo"""
    try:
        with open(f"{filename}", "w") as file:
            file.write(message)
        return "✅ Mensagem atualizada com sucesso!"
    except Exception as e:
        return f"❌ Erro ao atualizar mensagem: {str(e)}"