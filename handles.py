"""Lista de handles do bot
"""

import json

import pandas as pd
import requests
from telegram import Update
from telegram.ext import ContextTypes

CONFIG_FILE = 'config.json'

def start(update: Update, context: ContextTypes):
    """Checar se o robo está funcionando

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Iae meu bom, tô vivo hein!")


def echo(update: Update, context: ContextTypes):
    """Repete tudo que for escrito no chat

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=update.message.text)


def invert(update: Update, context: ContextTypes):
    """Inverte as frases que foram passadas como argumentos

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    text = str(' '.join(context.args))[::-1]
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text)


def caps(update: Update, context: ContextTypes):
    """Retorna o texto em caps

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """

    text = ' '.join(context.args).upper()
    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text)


def respostas(update: Update, context: ContextTypes):
    """Se a ultima palavra for alguma da lista de messagens, ele retorna com a frase padrão

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    texto = str(update.message.text).split(None)[-1].lower()
    file = open(CONFIG_FILE, "r", encoding="utf-8")
    respostas = json.load(file)
    if texto in respostas['mensagens']:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=respostas["mensagens"][texto])
    file.close()


def loteria(update: Update, context: ContextTypes):
    """Avisa os ultimos dados da loteria

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    try:
        # DOC da API https://github.com/guto-alves/loterias-api
        URL = 'https://loteriascaixa-api.herokuapp.com/api/mega-sena/latest'
        request = requests.get(URL, timeout=60).json()
        if request:
            text = (
                f'{request["nome"]}\n'
                f'Data: {request["data"]}\n'
                f'Concurso: {request["concurso"]}\n'
                f'Data do proximo jogo: {request["dataProxConcurso"]}\n'
                f'Dezenas: {"-".join(request["dezenas"])}\n'
            )
            if request["acumulou"] is True:
                text += (f'Acumulou para: {request["acumuladaProxConcurso"]}\n')
            for premio in request['premiacoes']:
                text += (
                    f'{premio["acertos"]}:\n'
                    f'  Nº de vencedores: {premio["vencedores"]}\n'
                    f'  Premio: R${premio["premio"]}\n'
                )
            df_mega = pd.DataFrame(
                {"data_ult": [request['data']], "data_prox": [request['dataProxConcurso']]})
            df_mega.to_csv('mega.csv', index=False, sep=';')

        else:
            text = 'Sem dados'

    except:
        request = {'Erro ao buscar os dados'}

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=text)


def unknown(update: Update, context: ContextTypes):
    """Se o comando não for reconhecido, ele retorna com a mensagem padrão

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Desculpa, nao falo americano e esse comando não existe!")


def cep(update: Update, context: ContextTypes):
    """Retorna o endereço para o CEP passado como argumento

    Args:
        update (Update): _description_
        context (ContextTypes): _description_
    """
    cep = context.args[0]
    if len(cep) == 8:
        url = f'https://viacep.com.br/ws/{cep}/json/'
        request = requests.get(url, timeout=30).json()
        if request:
            text = (
                f'CEP: {request["cep"]}\n'
                f'Logradouro: {request["logradouro"]}\n'
                f'Complemento: {request["complemento"]}\n'
                f'Bairro: {request["bairro"]}\n'
                f'Localidade: {request["localidade"]} - {request["uf"]}\n'
            )
    else:
        request = 'CEP inválido'
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
