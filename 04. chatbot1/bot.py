from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from secret import key
import json
import math

def leggi_ristoranti():
    with open('chatbot1/dati.json', 'r', encoding='utf-8') as f:
        dati = json.load(f)
    
    ristoranti = []
    for item in dati:
        ristorante = {
            'nome': item.get('name', 'N/A'),
            'latitudine': float(item.get('lat', 0)),
            'longitudine': float(item.get('lon', 0))
        }
        ristoranti.append(ristorante)
    
    return ristoranti

def calcola_distanza(lat1, lon1, lat2, lon2):
    """Calcola la distanza in km tra due coordinate usando la formula di Haversine"""
    R = 6371  # Raggio della Terra in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    distanza = R * c
    return distanza

def trova_ristorante_piu_vicino(latitudine, longitudine):
    """Trova il ristorante più vicino date latitudine e longitudine"""
    ristoranti = leggi_ristoranti()
    
    if not ristoranti:
        return None
    
    ristorante_piu_vicino = None
    distanza_minima = float('inf')
    
    for ristorante in ristoranti:
        distanza = calcola_distanza(latitudine, longitudine, 
                                    ristorante['latitudine'], 
                                    ristorante['longitudine'])
        
        if distanza < distanza_minima:
            distanza_minima = distanza
            ristorante_piu_vicino = ristorante.copy()
            ristorante_piu_vicino['distanza_km'] = round(distanza, 2)
    
    return ristorante_piu_vicino

async def hello(update, context):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def echo(update, context):
    await update.message.reply_text(update.message.text)

async def photo_handler(update, context):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("chatbot/img/user_photo.jpg")
    #await update.message.reply_text(f'photo received {user}')
    chat_id = update.message.chat.id
    await context.bot.send_document(chat_id=chat_id, document=open('chatbot/img/user_photo.jpg', 'rb'))

async def process_location(update, context):
    if update.edited_message:
        message = update.edited_message
    else:
        message = update.message
    user_location = message.location

    user = message.from_user
    print(f"You talk with user {user['first_name']} and his user ID: {user['id']}")
    msg = f'Ti trovi presso lat={user_location.latitude}&lon={user_location.longitude}'
    r = trova_ristorante_piu_vicino(user_location.latitude, user_location.longitude)
    if r:
        msg += f"\nIl ristorante più vicino è {r['nome']} a {r['distanza_km']} km"
    await message.reply_text(msg)

print('starting')


ristoranti = leggi_ristoranti()
app = ApplicationBuilder().token(key).build()
app.add_handler(CommandHandler("hello", hello))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.LOCATION, process_location))
app.run_polling()