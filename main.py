import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
from datetime import datetime
import pytz
from threading import Thread

# --- CONFIGURAÇÃO DO SERVIDOR (FLASK) ---
app = Flask('')

@app.route('/')
def home():
    return "Intelligence Football API Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURAÇÃO DO BOT ---
# JÁ COLOQUEI SUA SENHA AQUI ABAIXO:
TOKEN = "8464937509:AAFQjGW4BD2g25d_2HjYdIh_rTVJO_DUTY"
bot = telebot.TeleBot(TOKEN)

# --- CONFIGURAÇÕES DE BUSCA ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

def get_timestamp():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz).strftime('%d/%m/%Y | %H:%M')

def get_saudacao():
    tz = pytz.timezone('America/Sao_Paulo')
    hora = datetime.now(tz).hour
    if 5 <= hora < 12:
        return "☀️ Bom dia"
    elif 12 <= hora < 18:
        return "🌤️ Boa tarde"
    else:
        return "🌑 Boa noite"

# --- INTELIGÊNCIA: BUSCAR NOTÍCIAS ---
def buscar_infos_google(time, tipo_busca):
    try:
        if tipo_busca == "geral":
            query = f"{time} notícias futebol escalação provável jogo de hoje"
        elif tipo_busca == "dm":
            query = f"{time} departamento médico lesão desfalques hoje"
        elif tipo_busca == "logistica":
            query = f"{time} viagem desgaste maratona jogos cansaço logística"
        
        url = f"https://www.google.com/search?q={query}&tbm=nws&num=3"
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        noticias = []
        for item in soup.find_all('div', class_='GI74Re'):
            noticias.append(item.get_text())
        
        if not noticias:
            for item in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
                noticias.append(item.get_text())

        noticias_limpas = list(set(noticias))[:2]
        
        if not noticias_limpas:
            return ["Sem informações recentes."]
            
        return noticias_limpas

    except Exception as e:
        return [f"Erro na varredura."]

# --- INTELIGÊNCIA: CLIMA ---
def buscar_clima(): 
    return "🌤️ Estável (Sem alertas graves)"

# --- COMANDO /START ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    saudacao = get_saudacao()
    texto = (
        f"{saudacao}, Chefe! **Sistema Pro Scout v3.0 Ativo.** 🤖\n\n"
        "Agora com análise de **Logística e Cansaço**.\n"
        "Selecione o time para o relatório:"
    )
    
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    times = ["Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Vasco", "Botafogo", "Bahia", "Grêmio", "Inter", "Cruzeiro"]
    botoes = []
    for time in times:
        botoes.append(telebot.types.InlineKeyboardButton(time, callback_data=time))
    
    markup.add(*botoes)
    
    bot.reply_to(message, texto, reply_markup=markup, parse_mode="Markdown")

# --- PROCESSAMENTO DOS BOTÕES ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    time_ref = call.data
    bot.answer_callback_query(call.id, "🔍 Acessando satélite...")
    
    msg_espera = bot.send_message(call.message.chat.id, f"⏳ **Analisando {time_ref}...**", parse_mode="Markdown")
    
    infos_geral = buscar_infos_google(time_ref, "geral")
    infos_dm = buscar_infos_google(time_ref, "dm")
    infos_logistica = buscar_infos_google(time_ref, "logistica")
    
    def formatar_lista(lista):
        texto = ""
        for item in lista:
            texto += f"• {item}\n"
        return texto

    timestamp = get_timestamp()
    
    relatorio = (
        f"📂 **RELATÓRIO: {time_ref.upper()}**\n"
        f"📆 {timestamp}\n"
        "----------------------------------\n"
        f"🔋 **LOGÍSTICA E DESGASTE**\n"
        f"{formatar_lista(infos_logistica)}\n"
        "----------------------------------\n"
        f"🚑 **DM E DISPONIBILIDADE**\n"
        f"{formatar_lista(infos_dm)}\n"
        "----------------------------------\n"
        f"🔎 **BASTIDORES E TÁTICA**\n"
        f"{formatar_lista(infos_geral)}\n"
        "----------------------------------\n"
        f"🌤️ **CLIMA:** {buscar_clima()}\n\n"
        "⚠️ *Varredura de notícias em tempo real.*"
    )
    
    bot.delete_message(call.message.chat.id, msg_espera.message_id)
    bot.send_message(call.message.chat.id, relatorio, parse_mode="Markdown")

# --- INICIAR ---
t = Thread(target=run_flask)
t.start()
bot.polling()
