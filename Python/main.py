import base64
from io import BytesIO

import timm
from PIL import Image, ImageTk
import paho.mqtt.client as mqtt
import tkinter as tk
import torch
import torchvision.models as models
from torchvision import transforms
import urllib.request
import torch
import timm
from torchvision import transforms
from PIL import Image
import matplotlib.pyplot as plt
import urllib.request

import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class DeepPetClassifier:
    def __init__(self):
        self.load_data()
        self.model = self.build_model()
        self.load_model_weights()

    def load_data(self):
        (self.train_data, self.test_data), self.info = tfds.load(
            "oxford_iiit_pet", split=["train", "test"], as_supervised=True, with_info=True
        )
        self.class_names = self.info.features["label"].names

        self.train_data = self.train_data.map(self.preprocess).batch(32).prefetch(tf.data.AUTOTUNE)
        self.test_data = self.test_data.map(self.preprocess).batch(32).prefetch(tf.data.AUTOTUNE)

    def preprocess(self, image, label):
        image = tf.image.resize(image, (128, 128))
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        return image, label

    def build_model(self):
        base_model = tf.keras.applications.MobileNetV2(input_shape=(128, 128, 3), include_top=False, weights="imagenet")
        for layer in base_model.layers[-20:]:  # Размораживаем последние 20 слоев
            layer.trainable = True

        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(len(self.class_names), activation="softmax")
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001), loss="sparse_categorical_crossentropy",
                      metrics=["accuracy"])

        return model

    def train(self, epochs=5):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("pet_classifier_weights1.weights.h5")

    def load_model_weights(self):
        if os.path.exists("pet_classifier_weights1.weights.h5"):
            self.model.load_weights("pet_classifier_weights1.weights.h5")
            print('Weights loaded.')
        else:
            print('Weights file not found. Start training...')
            self.train()

    def classify(self, image):
        image = image.resize((128, 128))
        image = np.array(image)
        image = tf.keras.applications.mobilenet_v2.preprocess_input(image)
        image = np.expand_dims(image, axis=0)
        predictions = self.model.predict(image)
        print("Predictions", predictions)
        class_index = np.argmax(predictions)
        confidence = np.max(predictions)
        return self.class_names[class_index], confidence
# === Функция для создания графического интерфейса ===
def create_gui():
    global root, img_label
    root = tk.Tk()
    root.title("MQTT Image Viewer")

    # Место для отображения изображения
    img_label = tk.Label(root)
    img_label.pack()


def update_image(image: Image.Image):
    # Конвертируем PIL Image в изображение, которое можно отобразить в Tkinter
    img_tk = ImageTk.PhotoImage(image)
    img_label.config(image=img_tk)
    img_label.image = img_tk  # Сохраняем ссылку на изображение, чтобы избежать его удаления


# === MQTT настройки ===
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    client.subscribe("animal/photo")

breed_descriptions = {
    "Abyssinian": "Abyssinian cats are known for their intelligence and playful personality.",
    "Bengal": "Bengal cats have a wild appearance with a gentle domestic temperament.",
    "Bombay": "Bombay cats are sleek, black, and resemble miniature panthers.",
    "Birman": "Birman cats are gentle and affectionate, with beautiful blue eyes.",
    "British Shorthair": "Known for their round faces and dense coats, these cats are calm and dignified.",
    "Maine Coon": "Large, friendly, and sociable cats with tufted ears and bushy tails.",
    "Persian": "Persians are quiet, sweet, and require regular grooming due to long coats.",
    "Egyptian Mau": "One of the few naturally spotted domestic cat breeds.",
    "Ragdoll": "Ragdolls go limp when picked up and are extremely affectionate.",
    "Russian Blue": "Elegant cats with a silvery-blue coat and green eyes.",
    "Siamese": "Talkative and affectionate cats with striking blue eyes.",
    "Sphynx": "Hairless, energetic, and love human attention.",
    "Boxer": "Boxers are strong, energetic dogs that love to play.",
    "Keeshond": "Keeshonds are friendly and alert with a fox-like expression.",
    "Havanese": "Havanese dogs are cheerful and great companions.",
    "Basset Hound": "Low-slung dogs with a great sense of smell and calm demeanor.",
    "English Setter": "Gentle and friendly with a speckled coat.",
    "Miniature Pinscher": "Small but fearless, with a proud and confident personality.",
    "Chihuahua": "Tiny and alert, Chihuahuas are full of personality.",
    "Great Pyrenees": "Large and calm guardians, often used for livestock protection.",
    "German Shorthaired": "Versatile and athletic hunting dogs.",
    "Beagle": "Happy, curious dogs with great scent-tracking abilities.",
    "Staffordshire Bull Terrier": "Muscular and loyal, known for their courage.",
    "English Cocker Spaniel": "Merry and energetic dogs with long ears.",
    "New Found Land": "Giant dogs known for water rescue and gentle nature.",
    "Pomeranian": "Fluffy and lively with a big personality in a tiny body.",
    "Leonberger": "Large, calm, and friendly giants.",
    "American Pit Bull Terrier": "Strong and loyal, often misunderstood.",
    "Wheaten Terrier": "Soft-coated terriers known for friendliness.",
    "Japanese Chin": "Elegant and charming lap dogs.",
    "Samyod": "Fluffy white dogs with a signature “smile.”",
    "Scottish Terrier": "Independent and dignified with a distinctive profile.",
    "Shiba Inu": "Alert and confident, with a fox-like appearance.",
    "Pug": "Small, sociable dogs with wrinkled faces.",
    "Saint Bernard": "Huge dogs with a gentle and patient temperament.",
    "American Bulldog": "Strong, loyal, and athletic.",
    "Yorkshire Terrier": "Small dogs with big personalities and long silky hair."
}
def on_message(client, userdata, msg):
    try:
        # Получаем сообщение от MQTT
        payload = msg.payload.decode()
        user_id, image_b64 = payload.split("||")

        # Декодируем base64 изображение
        image_bytes = base64.b64decode(image_b64)

        # Открываем изображение с помощью PIL
        image = Image.open(BytesIO(image_bytes))

        # Обновляем изображение в графическом интерфейсе (if need)
        # update_image(image)
        image = image.resize((250, 250), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        global classifier
        
        classifier = DeepPetClassifier()
        # Классификация изображения
        predicted_label, confidence = classifier.classify(image)
        print(predicted_label)
        print(confidence)


        # Отправляем результат в MQTT
        result_topic = f"animal/result/{user_id}"

        formatted_label = predicted_label.replace('_', ' ').title()

        # Получаем описание
        description = breed_descriptions.get(formatted_label, "No description available.")

        # Объединяем название и описание
        message = f"{formatted_label}: {description}"

        # Публикуем результат
        client.publish(result_topic, message)
        print(f"Result sent to {result_topic}: {message}")

    except Exception as e:
        print("Error:", e)


# Создание графического интерфейса
create_gui()

# MQTT клиент
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Подключение к MQTT брокеру
client.connect("test.mosquitto.org", 1883)

# Запуск цикла обработки событий MQTT
client.loop_start()

# Запуск графического интерфейса Tkinter
root.mainloop()
