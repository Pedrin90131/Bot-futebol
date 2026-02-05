import telebot
import requests
from bs4 import BeautifulSoup
import time
from threading import Thread
from flask import Flask
import os

# --- 1. CONFIGURAÇÃO DO SERVIDOR ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIGURAÇÃO DO BOT ---
TOKEN = "8464937509:AAFQjGW4BD2g25d_2HjYdIhF_rTvJU_SUTY"
bot = telebot.TeleBot(TOKEN)

TIMES_SERIE_A = [
    "Flamengo", "Palmeiras", "Botafogo", "Fortaleza", "São Paulo", 
    "Internacional", "Cruzeiro", "Bahia", "Corinthians", "Atlético-MG", 
    "Vasco", "Vitória", "Athletico-PR", "Fluminense", "Criciúma", 
    "Juventude", "Grêmio", "Bragantino", "Cuiabá", "Atlético-GO"
]

def busca_news(time_nome):
    time.sleep(2)
    query = f'"{time_nome}" escalação provável poupar ge'
    url = f"https://www.google.com/search?q={query}&tbm=nws"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        manchetes = [m.get_text() for m in soup.find_all('div', {'class': 'BNeawe'}) if len(m.get_text()) > 20]
        
        if not manchetes: return None
        
        texto = "\n".join(manchetes).lower()
        gatilhos = ["poup", "reserv", "misto", "fora", "desfalque", "vida", "decisiv"]
        
        if any(x in texto for x in gatilhos):
            return f"🚨 **{time_nome.upper()}**: {manchetes[0]}"
        return None
    except:
        return None

# --- 3. COMANDOS DO TELEGRAM ---

@bot.message_handler(commands=['start'])
def boas_vindas(mensagem):
    texto = (
        "🚀 **BOT INSIDER ONLINE!**\n\n"
        "Comandos:\n"
        "🔹 `/radar [Time]` -> Checa um time específico\n"
        "🔹 `/alerta_geral` -> Varre os 20 times (demora 1 min)\n\n"
        "_Estou pronto._"
    )
    bot.reply_to(mensagem, texto, parse_mode="Markdown")

@bot.message_handler(commands=['alerta_geral'])
def alerta(mensagem):
    bot.reply_to(mensagem, "📡 Iniciando varredura... Aguarde cerca de 1 minuto.")
    
    def tarefa():
        encontrados = []
        for t in TIMES_SERIE_A:
            res = busca_news(t)
            if res: encontrados.append(res)
        
        if encontrados:
            msg = "⚠️ **RELATÓRIO DE RISCO:**\n\n" + "\n\n".join(encontrados)
        else:
            msg = "✅ **TUDO LIMPO:** Nenhuma notícia crítica encontrada agora."
            
        bot.send_message(mensagem.chat.id, msg, parse_mode="Markdown")
        
    Thread(target=tarefa).start()

@bot.message_handler(commands=['radar'])
def radar(mensagem):
    t = mensagem.text.replace("/radar", "").replace("/", "").strip().title()
    
    if not t:
        bot.reply_to(mensagem, "❌ Digite o nome do time. Ex: `/radar Vasco`")
        return

    if t not in TIMES_SERIE_A:
        bot.reply_to(mensagem, "❌ Time não encontrado na lista da Série A.")
        return
        
    bot.send_message(mensagem.chat.id, f"🔍 Buscando sobre {t}...")
    res = busca_news(t)
    bot.send_message(mensagem.chat.id, res if res else f"✅ **{t}**: Tudo indica força máxima.", parse_mode="Markdown")

# --- 4. START DO SISTEMA ---
if __name__ == "__main__":
    print(">>> SISTEMA CORRIGIDO E ONLINE!")
    Thread(target=run_flask).start()
    bot.infinity_polling()
