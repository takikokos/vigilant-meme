import telebot
import redis
from pydub import AudioSegment
import io
import cv2
import numpy as np


# t.me/TraneeBot.
TOKEN = ""

bot = telebot.TeleBot(TOKEN)
redisClient = redis.Redis(host='localhost', port=6379, db=0)
faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
print("Be sure redis-server is working")

def save_audio_todb(audio, user_id):
    data_stream = io.BytesIO()
    AudioSegment.from_ogg(io.BytesIO(audio)).export(data_stream, format="wav", parameters=["-ar", "16000"])
    data = data_stream.getvalue()
    redisClient.rpush(user_id, data)

def download_voice_msg(msg, bot):
    '''
        downloads and returns ogg file bytes
    '''
    assert msg.content_type == 'voice'

    file_id = msg.voice.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    return downloaded_file

def download_img_msg(msg, bot):
    assert msg.content_type == 'photo'
    file_id = msg.photo[0].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    return downloaded_file

def detect_face(img):
    jpg_as_np = np.frombuffer(img, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
    return len(faces) != 0

@bot.message_handler(content_types=["voice"])
def save_voice(message):
    audio = download_voice_msg(message, bot)
    print(f"Saved message from {message.from_user.id}")
    save_audio_todb(audio, message.from_user.id)
    bot.send_message(message.chat.id, f'Your audio saved to db!')

@bot.message_handler(content_types=["photo"])
def analize_img(message):
    img = download_img_msg(message, bot)
    face_on_photo = detect_face(img)
    if face_on_photo:
        bot.send_message(message.chat.id, "You look awesome today!")
    else:
        bot.send_message(message.chat.id, "Don't see your face on photo :(")

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "I can see if there is a face on a photo and i can save your voice messages to Redis DB!")

bot.polling()
