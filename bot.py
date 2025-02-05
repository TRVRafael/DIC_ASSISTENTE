from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler, filters
import requests

from config.auth import auth
from config.config import (
    NOTIFICATION_CHAT_ID, NOTIFICATION_CHAT_THREAD_ID, COMMANDS, ACCOUNTS_CG, ACCOUNTS_COMANDO, ACCOUNTS_CORE, ACCOUNTS_GOE, ACCOUNTS_PRES
)
from message_handler import read_message_file, write_message_file
from permissions import check_permissions

bot = Bot(token=auth.BOT_TOKEN)

async def send_notification(comando : str, user: str, old_text: str, new_text: str) -> None:
    """Envia um aviso para o tópico de atualizações quando um comando for atualizado"""
    message = (
        f"🔄 <b>Comando `{comando}` atualizado!</b>\n\n"
        f"👤 <b>Responsável:</b> @{user}\n"
        f"📜 <b>Mensagem antiga:</b>\n{old_text}\n\n"
        f"🆕 <b>Mensagem atualizada:</b>\n{new_text}"
    )
    
    url = f"https://api.telegram.org/bot{auth.BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": NOTIFICATION_CHAT_ID,  # ID do grupo
        "message_thread_id": NOTIFICATION_CHAT_THREAD_ID,  # ID do tópico
        "text": message,
        "parse_mode": "HTML",
    }

    response = requests.post(url, json=payload)
    print(response.json())
        

# Função genérica para exibir a mensagem de um comando
async def handle_command(update : Update, context : CallbackContext) -> None:
    command = update.message.text.lstrip("/")
    if command in COMMANDS:
        text = read_message_file(text)
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("❌ Comando inválido.")
        

async def cmd_atualizar(update : Update, context : CallbackContext) -> None:
    
    keyboard = [
        [InlineKeyboardButton("🛡️ Comando", callback_data="update_comando")],
        [InlineKeyboardButton("🔱 Comando-Geral", callback_data="update_comandogeral")],
        [InlineKeyboardButton("👑 Acessoria Presidencial", callback_data="update_apr")],
        [InlineKeyboardButton("🦅 CORE", callback_data="update_core")],
        [InlineKeyboardButton("💀 GOE", callback_data="update_goe")],
        [InlineKeyboardButton("⚔️ [CSI] Pronto Emprego", callback_data="update_csi")],
        [InlineKeyboardButton("📜 Instruções", callback_data="update_ins")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Por favor, seleciona o comando que deseja atualizar", reply_markup=reply_markup)


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    command = query.data.split("_")[-1]
    user_id = query.from_user.username
    
    if command == "ins" and (user_id, ACCOUNTS_CG, ACCOUNTS_COMANDO, ACCOUNTS_CORE, ACCOUNTS_GOE, ACCOUNTS_PRES):
        return await query.edit_message_text(read_message_file("instru.txt"))
    
    if command == "core" and not check_permissions(user_id, ACCOUNTS_CORE, ACCOUNTS_PRES):
        return await query.edit_message_text("🚫 Você não tem permissão para atualizar este comando.")
    elif command == "goe" and not check_permissions(user_id, ACCOUNTS_CORE, ACCOUNTS_GOE, ACCOUNTS_PRES):
        return await query.edit_message_text("🚫 Você não tem permissão para atualizar este comando.")
    elif command == "csi" and not check_permissions(user_id, ACCOUNTS_CORE, ACCOUNTS_GOE, ACCOUNTS_PRES):
        return await query.edit_message_text("🚫 Você não tem permissão para atualizar este comando.")
    
    if command not in ["core", "goe", "csi"] and not check_permissions(user_id, ACCOUNTS_CORE, ACCOUNTS_COMANDO, ACCOUNTS_CG, ACCOUNTS_PRES):
        return await query.edit_message_text("🚫 Você não tem permissão para atualizar este comando.")
    
    if command in COMMANDS:
        old_text = read_message_file(COMMANDS[command])
        context.user_data["update_type"] = COMMANDS[command]
        context.user_data["old_text"] = old_text
        await query.message.edit_text(f'📝 Insira a nova mensagem para `{command}`:')
    else:
        await query.message.edit_text("❌ Comando inválido.")
        

async def process_message(update: Update, context: CallbackContext) -> None:
    if "update_type" in context.user_data:
        filename = context.user_data["update_type"]
        old_text = context.user_data.get("old_text", "⚠️ Nenhuma mensagem antiga encontrada.")
        new_text = update.message.text
        print(f"Mensagem antiga: {old_text}")
        print(f"Nova mensagem: {new_text}")
        response = write_message_file(filename, new_text)
        
        # Enviar notificação para o grupo
        comando_nome = [key for key, value in COMMANDS.items() if value == filename][0]
        user_nome = update.message.from_user.username
        await send_notification(f"/{comando_nome}", user_nome, old_text, new_text)

        await update.message.reply_text(response)
        del context.user_data["update_type"]
        del context.user_data["old_text"]
        
    else:
        command = update.message.text.split("/")[-1]
        print(command)
        if command in COMMANDS:
            await update.message.reply_text(read_message_file(COMMANDS[command]), parse_mode="HTML")
            

async def cmd_instruction(update : Update, callback : CallbackContext, username = False) -> None:
    user_id = update.message.from_user.username
    if check_permissions(user_id, ACCOUNTS_CG, ACCOUNTS_COMANDO, ACCOUNTS_CORE, ACCOUNTS_GOE, ACCOUNTS_PRES):
        instruc = read_message_file("instru.txt")
        return await update.message.reply_text(instruc)

def main():
    app = Application.builder().token(auth.BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("atualizar", cmd_atualizar))
    app.add_handler(CommandHandler("ajuda", cmd_instruction))
    app.add_handler(CallbackQueryHandler(button_handler, pattern="^update_"))
    app.add_handler(MessageHandler(filters.TEXT, process_message))
    print("Bot running...")
    app.run_polling()
    

if __name__ == '__main__':
    main()