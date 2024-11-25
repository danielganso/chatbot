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
    """Envia uma mensagem usando a Z-API."""
    url = f"{BASE_URL}/send-text"
    payload = {
        "phone": phone,
        "message": message
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": "F90940ab202714a8d987298388bd01a72S"  # Substitua pelo valor completo do seu Client-Token
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Resposta da API ao enviar mensagem: {response.json()}")  # Log para depuração
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print(f"Dados recebidos: {data}")

        # Captura os campos necessários do JSON
        phone = data.get("phone")
        text = data.get("text", {}).get("message", "").strip()
        today = datetime.now().strftime("%Y-%m-%d")

        if not phone or not text:
            return jsonify({"error": "Dados inválidos ou incompletos"}), 400

        # Verifica se o atendimento já foi encerrado para este número no dia
        if atendimentos_encerrados.get(phone) == today:
            print(f"Atendimento encerrado para {phone} hoje. Ignorando mensagem.")
            return jsonify({"status": "ignored"}), 200

        # Resposta inicial do chatbot
        if phone in estados_usuarios and estados_usuarios[phone] == "aguardando_orcamento":
            if text.lower() == "sim concluir":
                send_message(phone, "Obrigado pelas informações! Logo você receberá seu orçamento! 😊")
                estados_usuarios.pop(phone, None)  # Remove o estado do usuário
                atendimentos_encerrados[phone] = today
                return jsonify({"status": "success"}), 200

            elif text.lower() == "não ainda estou enviando":
                send_message(phone, "Favor enviar todas as informações de uma só vez para agilizar seu atendimento.")
                return jsonify({"status": "success"}), 200

            else:
                send_message(phone, "Continuando o envio das informações. Envie mais detalhes ou clique em 'Sim Concluir' para finalizar.")
                return jsonify({"status": "success"}), 200

        elif text.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
            welcome_message = (
                "Olá, tudo bem?\n"
                "Que prazer te ter por aqui! 🤩\n\n"
                "Para agilizar seu atendimento vou te direcionar a algumas opções:\n\n"
                "📌 *1* - Gostaria de um orçamento ✍️\n"
                "📌 *2* - Quero saber promoções prontas ☑️\n"
                "📌 *3* - Receber ofertas diretamente pelo WhatsApp 📨\n"
                "📌 *4* - Falar com um atendente 👩‍💻\n\n"
                "📌 *Falar com Atendente* - Caso prefira atendimento humano."
            )
            send_message(phone, welcome_message)

        elif text == "1":
            option_1_message = (
                "Por favor, envie as seguintes informações para o orçamento:\n"
                "- Seu nome;\n"
                "- Destino que quer o orçamento;\n"
                "- Data do orçamento;\n"
                "- Quantidade de pessoas (se houver crianças, inclua as idades).\n\n"
                "Após enviar todas as informações, clique no botão abaixo:\n\n"
                "📌 *Sim Concluir* - Para finalizar o envio das informações.\n"
                "📌 *Não Ainda Estou Enviando* - Se precisar enviar mais detalhes."
            )
            estados_usuarios[phone] = "aguardando_orcamento"
            send_message(phone, option_1_message)

        elif text == "2":
            option_2_message = (
                "Dá uma olhada no nosso destaque do Instagram 👇\n"
                "(Incluir aqui o link do destaque)\n\n"
                "Estamos sempre atualizando, mas confirme disponibilidade, pois a rotatividade é grande!"
            )
            send_message(phone, option_2_message)

        elif text == "3":
            option_3_message = (
                "Já iremos adicionar seu número à nossa lista de transmissão!\n\n"
                "Por favor, adicione nosso contato à sua agenda para receber as ofertas diretamente pelo WhatsApp! 😄✈️"
            )
            send_message(phone, option_3_message)

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


