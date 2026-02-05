import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
from datetime import datetime
import pytz
from threading import Thread

# --- 1. CONFIGURAÇÃO DO SERVIDOR (FLASK) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online e Rodando!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURAÇÃO DO ROBÔ (AQUI ESTAVA O ERRO) ---
TOKEN = "8464937509:AAFQjGW4BD2g25d_2HjYdIh_rTVJO_DUTY"
bot = telebot.TeleBot(TOKEN)  # <--- ESSA LINHA É A QUE FAZ FUNCIONAR

# --- 3. FERRAMENTAS DE BUSCA ---
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_timestamp():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz).strftime('%d/%m/%Y às %H:%M')

def buscar_google(termo):
    try:
        url = f"https://www.google.com/search?q={termo}&tbm=nws&num=3"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        noticias = [div.get_text() for div in soup.find_all('div', class_='GI74Re')]
        if not noticias:
            noticias = [div.get_text() for div in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')]
        return list(set(noticias))[:2] if noticias else ["Sem notícias recentes."]
    except:
        return ["Erro ao buscar dados."]

# --- 4. COMANDOS E MENU ---
@bot.message_handler(commands=['start'])
def menu_principal(message):
    texto = (
        "🔥 **SISTEMA PRO SCOUT LIGADO**\n"
        "Bora analisar. Escolha o time:"
    )
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    botoes = [
        telebot.types.InlineKeyboardButton("Flamengo", callback_data="Flamengo"),
        telebot.types.InlineKeyboardButton("Palmeiras", callback_data="Palmeiras"),
        telebot.types.InlineKeyboardButton("São Paulo", callback_data="São Paulo"),
        telebot.types.InlineKeyboardButton("Corinthians", callback_data="Corinthians"),
        telebot.types.InlineKeyboardButton("Vasco", callback_data="Vasco"),
        telebot.types.InlineKeyboardButton("Botafogo", callback_data="Botafogo"),
        telebot.types.InlineKeyboardButton("Bahia", callback_data="Bahia"),
        telebot.types.InlineKeyboardButton("Grêmio", callback_data="Grêmio")
    ]
    markup.add(*botoes)
    bot.reply_to(message, texto, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def relatorio_time(call):
    time = call.data
    bot.answer_callback_query(call.id, "🔍 Buscando informações...")
    
    msg = bot.send_message(call.message.chat.id, f"⏳ **Varrendo notícias do {time}...**", parse_mode="Markdown")
    
    # Buscas Inteligentes
    logistica = buscar_google(f"{time} viagem cansaço desgaste logística")
    dm = buscar_google(f"{time} lesão desfalque departamento médico")
    geral = buscar_google(f"{time} provável escalação treino hoje")
    
    def lista(itens): return "\n".join([f"• {i}" for i in itens])
    
    texto_final = (
        f"📂 **RELATÓRIO: {time.upper()}**\n"
        f"📅 {get_timestamp()}\n"
        "--------------------------------\n"
        f"🔋 **LOGÍSTICA (Cansaço/Viagem)**\n{lista(logistica)}\n"
        "--------------------------------\n"
        f"🚑 **DM (Lesões)**\n{lista(dm)}\n"
        "--------------------------------\n"
        f"🔎 **NOTÍCIAS DO TREINO**\n{lista(geral)}\n"
        "--------------------------------\n"
        "⚠️ *Dados extraídos em tempo real.*"
    )
    
    bot.delete_message(call.message.chat.id, msg.message_id)
    bot.send_message(call.message.chat.id, texto_final, parse_mode="Markdown")

# --- 5. LIGAR TUDO ---
t = Thread(target=run_flask)
t.start()
bot.polling()
