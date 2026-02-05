import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
from datetime import datetime
import pytz
from threading import Thread

# --- 1. SERVIDOR ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Rodando!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURAÇÃO DO ROBÔ (AQUI ESTAVA O ERRO) ---
TOKEN = "8464937509:AAFQjGW4BD2g25d_2HjYdIh_rTVJO_DUTY"

# A LINHA ABAIXO É A QUE ESTAVA FALTANDO NO SEU PRINT:
bot = telebot.TeleBot(TOKEN) 
# ----------------------------------------------------

# --- 3. FUNÇÕES ---
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
        return ["Erro na busca."]

# --- 4. COMANDOS ---
@bot.message_handler(commands=['start'])
def menu(message):
    texto = "🤖 **ROBÔ PRO SCOUT ATIVO**\nEscolha o time:"
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    times = ["Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Vasco", "Botafogo", "Bahia", "Grêmio"]
    botoes = [telebot.types.InlineKeyboardButton(t, callback_data=t) for t in times]
    markup.add(*botoes)
    bot.reply_to(message, texto, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def relatorio(call):
    time = call.data
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, f"⏳ Analisando {time}...")
    
    # Buscas
    logistica = buscar_google(f"{time} viagem cansaço logística")
    dm = buscar_google(f"{time} lesão desfalque médico")
    geral = buscar_google(f"{time} escalação treino hoje")
    
    resumo = (
        f"📂 **{time.upper()}** | 📅 {get_timestamp()}\n\n"
        f"🔋 **LOGÍSTICA/CANSAÇO**\n" + "\n".join([f"• {n}" for n in logistica]) + "\n\n"
        f"🚑 **DM/LESÕES**\n" + "\n".join([f"• {n}" for n in dm]) + "\n\n"
        f"🔎 **BASTIDORES**\n" + "\n".join([f"• {n}" for n in geral])
    )
    
    bot.delete_message(call.message.chat.id, msg.message_id)
    bot.send_message(call.message.chat.id, resumo, parse_mode="Markdown")

# --- 5. EXECUÇÃO ---
t = Thread(target=run_flask)
t.start()
bot.polling()
    
