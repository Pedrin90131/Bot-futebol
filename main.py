import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
from threading import Thread
from flask import Flask
import os
import re
from datetime import datetime
import pytz

app = Flask('')

@app.route('/')
def home():
    return "Intelligence Football API Online"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# CONFIGURAÇÃO DO BOT
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8464937509:AAFQjGW4BD2g25d_2HjYdIhF_rTvJU_SUTY")
bot = telebot.TeleBot(TOKEN)

# MONITORAMENTO ESTRATÉGICO
TIMES_MONITORADOS = ["Flamengo", "Palmeiras", "Corinthians", "São Paulo", "Vasco", "Santos", "Grêmio", "Botafogo", "Internacional", "Cruzeiro", "Atlético-MG", "Fluminense", "Fortaleza", "Bahia"]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

def get_timestamp():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz).strftime("%d/%m/%Y | %H:%M")

def analisar_horario(texto):
    match = re.search(r'(\d{1,2})[h:](\d{2})?', texto)
    if match:
        hora = int(match.group(1))
        periodo = "☀️ DIURNO" if 6 <= hora < 18 else "🌑 NOTURNO"
        return f"{match.group(0)} ({periodo})"
    return "🕒 Horário a confirmar"

def scout_investigativo(time_nome):
    time.sleep(1)
    
    # 1. CENÁRIO DA PARTIDA E CLIMA
    try:
        url_jogo = f"https://www.google.com/search?q={time_nome}+próximo+jogo+horário+clima&tbm=nws&tbs=qdr:w"
        res = requests.get(url_jogo, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        noticias = [n.get_text() for n in soup.find_all('div', {'class': 'BNeawe'})]
        
        partida = noticias[0] if noticias else "Dados de confronto indisponíveis."
        horario = analisar_horario(partida)
        
        # Lógica de Chuva (Fundamental para análise de campo)
        clima_txt = " ".join(noticias).lower()
        previsao = "🌤️ Estável (Sem alertas de chuva)"
        if any(x in clima_txt for x in ["chuva", "temporal", "pancada", "chover"]):
            previsao = "🌧️ ALERTA: Probabilidade de Chuva (Campo Pesado)"
    except:
        return "❌ Erro na extração de dados da partida."

    # 2. INTELIGÊNCIA DE TREINO E TÁTICA
    try:
        url_treino = f"https://www.google.com/search?q={time_nome}+treinou+titular+esboço+vaga+substituto&tbm=nws&tbs=qdr:w"
        res_t = requests.get(url_treino, headers=HEADERS, timeout=10)
        soup_t = BeautifulSoup(res_t.text, "html.parser")
        manchetes_t = [m.get_text() for m in soup_t.find_all('div', {'class': 'BNeawe'})]
        
        titulares = "• Escalação em fase de teste/sigilo."
        trocas = "• Nenhuma alteração tática relevante detetada."
        
        if manchetes_t:
            melhor_fonte = max(manchetes_t, key=len)
            if len(melhor_fonte) > 45: titulares = f"👥 {melhor_fonte}"
            
            # Filtro de Substituições (Quem treinou na vaga de quem)
            for m in manchetes_t:
                if any(x in m.lower() for x in ["vaga", "lugar", "testado", "substitui"]):
                    trocas = f"🔄 **Movimentação:** {m}"
                    break
    except:
        titulares = "• Informação de treino inacessível."

    # 3. RELATÓRIO DO DEPARTAMENTO MÉDICO (DM)
    try:
        url_dm = f"https://www.google.com/search?q={time_nome}+desfalque+lesão+vetado+fora+dúvida&tbm=nws&tbs=qdr:w"
        res_dm = requests.get(url_dm, headers=HEADERS, timeout=10)
        soup_dm = BeautifulSoup(res_dm.text, "html.parser")
        manchetes_dm = [m.get_text() for m in soup_dm.find_all('div', {'class': 'BNeawe'})]
        
        alerta_dm = "✅ Sem baixas confirmadas no elenco principal."
        if manchetes_dm:
            txt_dm = " ".join(manchetes_dm).lower()
            if any(x in txt_dm for x in ["lesão", "fora", "vetado", "dúvida", "poupado"]):
                alerta_dm = f"🚑 **Risco/Baixa:** {manchetes_dm[0]}"
    except:
        alerta_dm = "• Sem boletim clínico atualizado."

    # FORMATAÇÃO DO RELATÓRIO FINAL
    return (
        f"📂 **RELATÓRIO DE INTELIGÊNCIA: {time_nome.upper()}**\n"
        f"📅 Análise em: {get_timestamp()}\n"
        f"──────────────────────\n"
        f"🏟️ **CENÁRIO PRÉ-JOGO**\n"
        f"• Confronto: {partida}\n"
        f"• Horário: {horario}\n"
        f"• Clima: {previsao}\n\n"
        f"📋 **BASTIDORES DO TREINO**\n"
        f"{titulares}\n\n"
        f"🔎 **INSIGHT TÁTICO**\n"
        f"{trocas}\n\n"
        f"🏥 **DM E DISPONIBILIDADE**\n"
        f"{alerta_dm}\n"
        f"──────────────────────\n"
        f"📊 *Filtro: Notícias e Treinos dos últimos 7 dias.*"
    )

# INTERFACE DO UTILIZADOR
def botoes_principais():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    botoes = [types.KeyboardButton(t) for t in TIMES_MONITORADOS[:8]]
    markup.add(*botoes)
    return markup

@bot.message_handler(commands=['start', 'menu'])
def iniciar(message):
    bot.reply_to(message, 
                 f"Olá, {message.from_user.first_name}.\n**Sistema de Scouting Profissional Ativado.**\n\nSelecione o clube para processar o relatório tático:", 
                 reply_markup=botoes_principais(), parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def processar_consulta(message):
    time_ref = message.text.strip().title()
    if time_ref in TIMES_MONITORADOS or len(time_ref) > 3:
        status = bot.reply_to(message, f"⏳ **A analisar dados de {time_ref}...**\n_Cruzando informações de treino e DM._", parse_mode="Markdown")
        
        relatorio = scout_investigativo(time_ref)
        
        bot.delete_message(message.chat.id, status.message_id)
        bot.reply_to(message, relatorio, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ Utilize os botões do menu para uma análise precisa.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
        
