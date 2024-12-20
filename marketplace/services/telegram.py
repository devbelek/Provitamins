import requests
from django.utils.timezone import localtime
from decouple import config
from marketplace.models import Order, OrderModerator


class Bot:

    api_url = 'https://api.telegram.org/'
    bot_token = config('BOT_TOKEN')

    def bot_url(self):
        return f'{self.api_url}bot{self.bot_token}/'

    def test_token(self):
        response = requests.get('{}{}'.format(
            self.bot_url(),
            "getMe"))
        if response.status_code == 200:
            r_json = response.json()
            if 'ok' in r_json and r_json['ok']:
                print(r_json['result'])
                return True
        else:
            print(response.status_code, response.json())

        return False

    def get_chat_ids(self):
        """
        Method to extract chat id from telegram request.
        """
        chat_ids = list(OrderModerator.objects.all().values_list('telegram_id', flat=True))
        return chat_ids

    def send_message(self, order: Order):
        message = self.format_order_to_msg(order)
        message_url = '{bot_url}sendMessage'.format(
            bot_url=self.bot_url()
        )
        chat_ids = self.get_chat_ids()
        print('chat_ids', chat_ids)
        for chat_id in chat_ids:
            json_data = {
                "chat_id": int(chat_id),
                "text": message,
                "parse_mode": 'HTML',
            }
            response = requests.post(message_url, json=json_data)
            print('response', response)
        return True

    def format_order_to_msg(self, order: Order):
        items = order.items.all()
        print('items', items)
        items_info = []
        for i, item in enumerate(items):
            # Construct item information
            item_info = f"Товар {i+1}.\n"
            item_info += f"     Название: {item.product.name}\n"
            item_info += f"     Количество: {item.quantity}\n"
            item_info += f"     Ссылка: https://provitamins.kg/products/{item.product.id}\n\n"
            items_info.append(item_info)

        # Construct the message with general order information and item details
        message = f"Заказ №{order.id}\n"
        local_time = localtime(order.date_created)
        message += f"Дата создания: {local_time.strftime('%Y-%m-%d %H:%M')}\n"
        message += f"ФИО: {order.full_name}\n"
        message += f"Номер телефона: {order.phone}\n\n"
        message += f"Количество товаров: {len(items)}\n"
        message += f"Общая сумма: {order.total_price}\n\n"
        message += "Товары:\n" + "\n".join(items_info)
        print('message', message)
        return message


bot = Bot()
