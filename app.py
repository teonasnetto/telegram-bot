"""Bot para repostas no telegram

Returns:
    _type_: _description_

"""

import os
from datetime import datetime
from time import sleep

import pandas as pd
import requests
import telegram
import json
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from handles import caps, cep, echo, invert, loteria, respostas, start, unknown

CONFIG_FILE = 'config.json'

def main():
    """Inicializa o bot"""

    #Lê o json de configurações
    file = open(CONFIG_FILE, "r", encoding="utf-8")
    config = json.load(file)

    # Inicializa o token e o Bot
    BOT_TOKEN: str = config["BOT"]["BOT_TOKEN"]
    mega_sena_bot = telegram.Bot(BOT_TOKEN)

    # Inicializa o Updater e o dispatcher
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Adiciona os handlers

    # echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    # dispatcher.add_handler(echo_handler)

    start_handler = CommandHandler('start', start)  # type: ignore
    dispatcher.add_handler(start_handler)

    texto_handler = MessageHandler(
        Filters.text & (~Filters.command), respostas)  # type: ignore
    dispatcher.add_handler(texto_handler)

    invert_handler = CommandHandler('invert', invert)  # type: ignore
    dispatcher.add_handler(invert_handler)

    caps_handler = CommandHandler('loteria', loteria)  # type: ignore
    dispatcher.add_handler(caps_handler)

    caps_handler = CommandHandler('caps', caps)  # type: ignore
    dispatcher.add_handler(caps_handler)

    cep_handler = CommandHandler('cep', cep)  # type: ignore
    dispatcher.add_handler(cep_handler)

    # Se não encontrar o comando, chama a função unknown
    unknown_handler = MessageHandler(Filters.command, unknown)  # type: ignore
    dispatcher.add_handler(unknown_handler)

    # Inicia o bot em tempo real
    updater.start_polling()

    # Inicia o loop do bot para avisar no grupo o o sorteio da mega-sena
    if os.path.isfile(("mega.csv")):
        df_mega_existent = pd.read_csv("mega.csv", sep=";")
    else:
        URL = 'https://loteriascaixa-api.herokuapp.com/api/mega-sena/latest'
        request = requests.get(URL, timeout=60).json()
        df_mega = pd.DataFrame(
            {"data_ult": [request['data']], "data_prox": [request['dataProxConcurso']]})
        df_mega.to_csv('mega.csv', index=False, sep=';')
        df_mega_existent = pd.read_csv("mega.csv", sep=";")

    while True:
        now = datetime.now().strftime("%d/%m/%Y")

        if now == df_mega_existent['data_prox'].values[0]:
            mega_sena_bot.send_message(
                chat_id=config["BOT"]["gruoup_megasena_id"], text="Hoje é dia de Mega Sena!")

            while now == df_mega_existent['data_prox'].values[0]:
                now_hour = datetime.now().strftime("%H:%M")
                time_until_game = (datetime.strptime(
                    "20:00", "%H:%M") - datetime.strptime(str(now_hour), "%H:%M")).total_seconds()
                print("Aguardando até a hora do sorteio da Mega Sena")

                if time_until_game >= 0:
                    sleep(int(time_until_game))

                if time_until_game < 0:
                    while True:
                        try:
                            URL = 'https://loteriascaixa-api.herokuapp.com/api/mega-sena/latest'
                            request = requests.get(URL, timeout=60).json()
                            df_mega = pd.DataFrame(
                                {"data_ult": [request['data']], "data_prox": [request['dataProxConcurso']]})
                            if df_mega_existent['data_prox'].values[0] != df_mega['data_prox'].values[0]:
                                df_mega.to_csv(
                                    'mega.csv', index=False, sep=';')
                                df_mega_existent = pd.read_csv(
                                    "mega.csv", sep=";")
                                if request:
                                    text = (
                                        f'{request["nome"]}\n'
                                        f'Data: {request["data"]}\n'
                                        f'Concurso: {request["concurso"]}\n'
                                        f'Data do proximo jogo: {request["dataProxConcurso"]}\n'
                                        f'Dezenas: {"-".join(request["dezenas"])}\n'
                                    )
                                    if request["acumulou"] is True:
                                        text += (
                                            f'Acumulou para: {request["acumuladaProxConcurso"]}\n')
                                    for premio in request['premiacoes']:
                                        text += (
                                            f'{premio["acertos"]}:\n'
                                            f'  Nº de vencedores: {premio["vencedores"]}\n'
                                            f'  Premio: R${premio["premio"]}\n'
                                        )
                                    mega_sena_bot.send_message(
                                        chat_id=config["BOT"]["gruoup_megasena_id"], text=text)
                                break
                        except:
                            print(
                                'erro ao buscar dados, aguardando para tentar novamente')
                        sleep(60)
                    break
        sleep(3600)


if __name__ == "__main__":
    main()
