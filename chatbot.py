from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Substitua pelos seus dados
INSTANCE_ID = "3D8D5C2F8DF4907B9157F6819FEED502"
INSTANCE_TOKEN = "78951A9DD9FD29419149549A"
BASE_URL = f"https://api.z-api.io/instances/{INSTANCE_ID}/token/{INSTANCE_TOKEN}"

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
        data = request.json  # Recebe os dados enviados pela Z-API
        print(f"Dados recebidos: {data}")  # Depuração para verificar os dados

        # Captura os campos necessários do JSON
        phone = data.get("phone")  # Número de quem enviou a mensagem
        text = data.get("text", {})  # Garante que 'text' exista no JSON
        message = text.get("message", "").strip()  # Captura a mensagem

        if not phone or not message:
            # Retorna erro se os campos esperados estiverem ausentes
            return jsonify({"error": "Dados inválidos ou incompletos"}), 400

        print(f"Mensagem de {phone}: {message}")  # Depuração para ver os dados processados

        # Resposta inicial do chatbot
        if message.lower() in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]:
            welcome_message = (
                "Olá, tudo bem?\n"
                "Que prazer te ter por aqui! 🤩\n\n"
                "Para agilizar seu atendimento vou te direcionar a algumas opções:\n\n"
                "Digite 1 - se você gostaria de um orçamento ✍️\n"
                "Digite 2 - se você quer saber as promoções prontas que temos disponíveis ☑️\n"
                "Digite 3 - se você gostaria de receber as ofertas que forem surgindo, direto em seu WhatsApp 📨\n"
                "Digite 4 - se você precisa falar com um atendente 👩‍💻"
            )
            send_message(phone, welcome_message)

        # Opção 1 - Solicita informações para orçamento
        elif message == "1":
            option_1_message = (
                "Preciso que me passe essas informações abaixo:\n"
                "- Seu nome;\n"
                "- Destino que quer o orçamento;\n"
                "- Data do orçamento;\n"
                "- Quantidade de pessoas (se tiver criança, preciso também da idade).\n\n"
                "Obs: Se for mais de um apartamento, informe a quantidade de pessoas e as idades das crianças para cada quarto! ✍️"
            )
            send_message(phone, option_1_message)

        # Opção 2 - Envia o link do Instagram
        elif message == "2":
            option_2_message = (
                "Dá uma olhada no nosso destaque do Instagram 👇\n"
                "(Incluir aqui o link do destaque)\n\n"
                "Estamos sempre atualizando, mas confirme disponibilidade, pois a rotatividade é grande!"
            )
            send_message(phone, option_2_message)

        # Opção 3 - Adiciona à lista de transmissão
        elif message == "3":
            option_3_message = (
                "Já iremos adicionar seu número à nossa lista de transmissão!\n\n"
                "Por favor, adicione nosso contato à sua agenda para receber as ofertas diretamente pelo WhatsApp! 😄✈️"
            )
            send_message(phone, option_3_message)

        # Opção 4 - Atendimento humano
        elif message == "4":
            option_4_message = (
                "Nosso horário de atendimento é de segunda à sexta das 08:00 às 18:00, "
                "e sábado das 08:30 às 12:30 ⏰\n\n"
                "Caso esteja dentro desses horários, aguarde um momento que um de nossos consultores irá te atender! "
                "Se estiver EM VIAGEM, sinalize a urgência ou ligue, mesmo fora do horário de atendimento! ☎️"
            )
            send_message(phone, option_4_message)

        # Mensagem padrão para entradas inválidas
        else:
            default_message = "Desculpe, não entendi sua mensagem. Por favor, escolha uma das opções enviando o número correspondente (1, 2, 3 ou 4)."
            send_message(phone, default_message)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Erro no webhook: {e}")  # Log do erro para depuração
        return jsonify({"error": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    app.run(port=5000)
