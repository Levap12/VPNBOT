import asyncio

from yookassa import Configuration
from yookassa import Payment

YOOKASSA_SHOPID = '993088'
YOOKASSA_TOKEN = 'test_dh02xu0bfdJqOKSSnwUXF6DxVONpOxuf0uZmKblWYv4'

if YOOKASSA_SHOPID and YOOKASSA_TOKEN:
    Configuration.configure(YOOKASSA_SHOPID, YOOKASSA_TOKEN)

async def create_payment(user_id: int,months: int) -> dict:
    amount, description = get_amount_and_description(months)

    resp = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://t.me/nockvpn_bot"
        },
        "capture": True,
        "description": description,
        "save_payment_method": False,
        "metadata": {
            "user_id": user_id,  # Здесь передаем идентификатор пользователя
            "months": months
        },
        "receipt": {
            "customer": {
                "email": 'example@example.com'
            },
            "items": [
                {
                    "description": description,
                    "quantity": "1",
                    "amount": {
                        "value": amount,
                        "currency": "RUB"
                    },
                    "vat_code": "1"
                },
            ]
        }
        })

    return {
        "url": resp.confirmation.confirmation_url,
        "amount": resp.amount.value
    }

def get_amount_and_description(months):
    if months == 1:
        return 190, "Nock 1 месяц"
    elif months == 3:
        return 500, "Nock 3 месяца"
    elif months == 6:
        return 900, "Nock 6 месяцев"
    else:
        return None, None


async def main():
    dict = await create_payment(user_id=452398375, months=3)
    print(dict)

if __name__ == "__main__":
    asyncio.run(main())
