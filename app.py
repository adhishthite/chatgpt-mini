import requests
from typing import Optional

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from chat_gpt import ChatGPT

app = Flask(__name__)
app.secret_key = 'supersecretkey'
chat_gpt: Optional[ChatGPT] = None


@app.route('/')
def setup():
    return render_template('setup.html')


@app.route('/setup', methods=['POST'])
def setup_submit():
    global chat_gpt
    api_key = request.form['api_key']
    model_id = request.form['model_id']
    context = request.form['context']

    if not test_api(api_key):
        return jsonify({'status': 'error', 'message': 'Failed to connect to OpenAI API'})

    chat_gpt = ChatGPT(model_id, api_key, context)
    chat_gpt.add_system_message(f"{context}. Respond precisely. Do not give more information than necessary.")

    try:
        chat_gpt.gpt_conversation()
        return jsonify({'status': 'success', 'message': 'Connection successful'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


def test_api(api_key: str) -> bool:
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    response = requests.get('https://api.openai.com/v1/models', headers=headers)
    return response.status_code == 200


@app.route('/chat')
def chat():
    if chat_gpt is None:
        return redirect(url_for('setup'))
    return render_template('chat.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.form['message']
    chat_gpt.add_user_message(user_input)
    response = chat_gpt.gpt_conversation()

    if response['status'] == 'success':
        return jsonify({'status': 'success', 'message': response['message']})
    else:
        return jsonify({'status': 'error', 'message': response['message']})


if __name__ == '__main__':
    app.run(debug=True, port=8801)
