import asyncio
import logging
import uuid
from threading import Thread

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from observer import CurrencyDataSubject, WebSocketObserver

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на свой секретный ключ
socketio = SocketIO(app)
currency_data_subject = CurrencyDataSubject()


@app.route('/')
def index():
    return render_template('client.html')


@socketio.on('connect')
def handle_connect():
    client_id = str(uuid.uuid4())
    observer = WebSocketObserver(socketio, client_id)
    observer.ws = socketio
    logging.info(f"New client connected: {client_id}")
    currency_data_subject.attach(observer)
    emit('client_id', {'client_id': client_id})  # Отправляем id клиенту.


@socketio.on('disconnect')
def handle_disconnect():
    logging.info("Client disconnected")


@app.route('/test')
def test():
    return render_template('base.html')


def start_observing():
    asyncio.run(currency_data_subject.start_polling(15))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app.debug = True


    async def main():
        t = Thread(target=start_observing)
        t.start()
        socketio.run(app, host='0.0.0.0', port=5000,
                     allow_unsafe_werkzeug=True)  # Отключаем релоадер так как он несовместим с asyncio.

    asyncio.run(main())