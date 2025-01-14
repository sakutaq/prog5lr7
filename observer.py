import asyncio
import logging
from abc import ABC, abstractmethod

import aiohttp
import requests

CURRENCY_API_URL = "https://www.cbr-xml-daily.ru/daily_json.js"


class Subject(ABC):
    @abstractmethod
    def attach(self, observer):
        pass

    @abstractmethod
    def detach(self, observer):
        pass

    @abstractmethod
    def notify(self):
        pass


class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass


class CurrencyDataSubject(Subject):
    _observers = set()
    _currency_data = {}

    def attach(self, observer):
        self._observers.add(observer)
        logging.info(f"Observer {observer.id} attached.")

    def detach(self, observer):
        self._observers.discard(observer)
        logging.info(f"Observer {observer.id} detached.")

    async def notify(self):
        for observer in self._observers:
            await observer.update(self._currency_data)

    async def fetch_currency_data(self):
        logging.info('FETCHING....')
        try:
            result = requests.get(CURRENCY_API_URL)
            if result.status_code == 200:
                self._currency_data = result.json()
                logging.info("Currency data fetched from API")
                await self.notify()
            else:
                logging.error(f"Error fetching currency data. Status code: {result.status_code}")
            # async with aiohttp.ClientSession() as session:
            #     async with session.get(CURRENCY_API_URL) as resp:
            #         if resp.status == 200:
            #             self._currency_data = await resp.json()
            #             logging.info("Currency data fetched from API")
            #             self.notify()
            #         else:
            #             logging.error(f"Error fetching currency data. Status code: {resp.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching currency data: {e}")

    async def start_polling(self, interval):
        logging.info('START POLLING....')
        while True:
            logging.info('POLLING....')
            await self.fetch_currency_data()
            await asyncio.sleep(interval)


class WebSocketObserver(Observer):
    def __init__(self, socketio, id):
        self.socketio = socketio
        self.id = id

    async def update(self, data):
        if self.socketio is None:
            logging.info(f"Client {self.id} socket closed")
            return
        try:
            self.socketio.emit('currency_update', {'currency_data': data})  # Отправляем данные конкретному клиенту
            logging.info(f"Currency data sent to {self.id}")
        except Exception as e:
            logging.error(f"Error sending data to client: {e}")