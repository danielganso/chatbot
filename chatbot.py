from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Substitua pelos seus dados
INSTANCE_ID = "3D8D5C2F8DF4907B9157F6819FEED502"
INSTANCE_TOKEN = "78951A9DD9FD29419149549A"
BASE_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{INSTANCE_TOKEN}"

# Armazena o estado dos usuários
estados_usuarios = {}
atendimentos_encerrados = {}

def send_message(phone, message):
    """Envia uma mensagem de texto simples usando a Z-API."""
    url = f"{BASE_URL}/send-text"
    payload = {
        "phone": phone,
        "message": message
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": "F90940ab202714a8d987298388bd01a72S"  # Substitua pelo seu Client-Token
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Resposta da API ao enviar mensagem: {response.json()}")  # Log para depuração
    return response.json()

def send_button_list(phone, message, buttons):
    """Envia uma mensagem com botões interativos usando a Z-API."""
    url = f"{BASE_URL}/send-button-list"
    payload = {
        "phone": phone,
        "message": message,
        "buttonList": {
            "buttons": buttons
        }
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": "F90940ab202714a8d987298388bd01a72S"  # Substitua pelo seu Client-Token
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Resposta da API ao enviar botões: {response.json()}")  # Log para depuração
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"Dados recebidos: {data}")

        # Captura os campos necessários do JSON
        phone = data.get("phone")
        text = data.get("text", {}).get("message", "").strip()
        button_id = data.get("buttonResponse", {}).get("id", "").strip()  # Captura o ID do botão
        today = datetime.now().strftime("%Y-%m-%d")

        # Prioriza o ID do botão, se ele existir
        if button_id:
            text = button_id

        if not phone or not text:
            return jsonify({"error": "Dados inválidos ou incompletos"}), 400

        # Verifica se o atendimento já foi encerrado para este número no dia
        if atendimentos_encerrados.get(phone) == today:
            print(f"Atendimento encerrado para {phone} hoje. Ignorando mensagem.")
            return jsonify({"status": "ignored"}), 200

        # Gerenciamento de estados
        if estados_usuarios.get(phone) == "aguardando_orcamento":
            if text == "sim_concluir":
                send_message(phone, "Obrigado pelas informações! Logo você receberá seu orçamento! 😊")
                estados_usuarios.pop(phone, None)  # Remove o estado do usuário
                atendimentos_encerrados[phone] = today
                return jsonify({"status": "success"}), 200

            elif text == "nao_enviando":
                send_message(phone, "Favor enviar todas as informações de uma só vez para agilizar seu atendimento.")
                return jsonify({"status": "success"}), 200

            else:
                send_message(phone, "Continuando o envio das informações. Envie mais detalhes ou clique em 'Sim Concluir' para finalizar.")
                return jsonify({"status": "success"}), 200

        # Menu principal
        if text.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
            welcome_message = (
                "Olá, tudo bem?\n"
                "Que prazer te ter por aqui! 🤩\n\n"
                "Para agilizar seu atendimento vou te direcionar a algumas opções:\n\n"
                "📌 *1* - Gostaria de um orçamento ✍️\n"
                "📌 *2* - Quero saber promoções prontas ☑️\n"
                "📌 *3* - Receber ofertas diretamente pelo WhatsApp 📨\n"
                "📌 *4* - Falar com um atendente 👩‍💻"
            )
            send_message(phone, welcome_message)

        # Opção 1 - Solicita informações para orçamento
        elif text == "1":
            info_message = (
                "Preciso que me passe essas informações abaixo:\n"
                "- Seu nome;\n"
                "- Destino que quer o orçamento;\n"
                "- Data do orçamento;\n"
                "- Quantidade de pessoas (se tiver criança, preciso também da idade).\n\n"
                "Obs: Se for mais de um apartamento, informe a quantidade de pessoas e as idades das crianças para cada quarto! ✍️"
            )
            send_message(phone, info_message)

            buttons = [
                {"id": "sim_concluir", "label": "Sim, Concluir"},
                {"id": "nao_enviando", "label": "Não, Ainda Estou Enviando"}
            ]
            estados_usuarios[phone] = "aguardando_orcamento"
            send_button_list(
                phone,
                message="Já enviou todas as informações? Escolha uma opção abaixo:",
                buttons=buttons
            )

        # Opção 2 - Envia o link do Instagram
        elif text == "2":
            option_2_message = (
                "Dá uma olhada no nosso destaque do Instagram 👇\n"
                "(Incluir aqui o link do destaque)\n\n"
                "Estamos sempre atualizando, mas confirme disponibilidade, pois a rotatividade é grande!"
            )
            send_message(phone, option_2_message)

        # Opção 3 - Adiciona à lista de transmissão
        elif text == "3":
            option_3_message = (
                "Já iremos adicionar seu número à nossa lista de transmissão!\n\n"
                "Por favor, adicione nosso contato à sua agenda para receber as ofertas diretamente pelo WhatsApp! 😄✈️"
            )
            send_message(phone, option_3_message)

        # Opção 4 ou "Falar com Atendente"
        elif text == "4" or text.lower() == "falar com atendente":
            atendimentos_encerrados[phone] = today
            send_message(phone, "Um atendente irá falar com você. O chatbot está encerrado para hoje.")
            return jsonify({"status": "success"}), 200

        else:
            default_message = "Desculpe, não entendi sua mensagem. Por favor, escolha uma das opções enviando o número correspondente (1, 2, 3 ou 4)."
            send_message(phone, default_message)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Erro no webhook: {e}")
        return jsonify({"error": "Erro interno no servidor"}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usa a porta definida pelo Render ou 5000 como fallback
    app.run(host='0.0.0.0', port=port)
