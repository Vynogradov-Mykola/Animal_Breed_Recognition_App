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
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import tensorflow as tf
import tensorflow_datasets as tfds
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from keras.src.utils import plot_model
class CNNPetClassifier:
    def __init__(self):
        self.load_data()
        self.model = self.build_model()
        self.load_model_weights()

    def load_data(self):
        (self.train_data, self.test_data), self.info = tfds.load(
            "oxford_iiit_pet", split=["train", "test"], as_supervised=True, with_info=True
        )
        self.class_names = self.info.features["label"].names

        # Добавляем аугментацию данных
        self.train_data = self.train_data.map(self.preprocess).batch(32).prefetch(tf.data.AUTOTUNE)
        self.test_data = self.test_data.map(self.preprocess).batch(32).prefetch(tf.data.AUTOTUNE)

    def preprocess(self, image, label):
        image = tf.image.resize(image, (128, 128)) / 255.0
        image = tf.image.random_flip_left_right(image)
        image = tf.image.random_brightness(image, max_delta=0.2)
        return image, label

    def build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(128, 128, 3)),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),

            tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),

            tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),

            tf.keras.layers.Conv2D(256, (3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),

            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(len(self.class_names), activation="softmax")
        ])

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"]
        )
        plot_model(model, to_file='cnn_model_plot.png', show_shapes=True, show_layer_names=True)

        return model

    def train(self, epochs=30):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("cnn_pet.weights.h5")
        plot_confusion_matrix(self.model, self.test_data, self.class_names)

    def load_model_weights(self):
        if os.path.exists("cnn_pet.weights.h5"):
            self.model.load_weights("cnn_pet.weights.h5")
            print("Model loaded.")
        else:
            print("Can`t find file.")
            self.train()

    def classify(self, image):
        image = image.resize((128, 128))

        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        predictions = self.model.predict(image)[0]

        print("Predictions", predictions)
        class_index = np.argmax(predictions)
        confidence = np.max(predictions)
        return self.class_names[class_index], confidence

class MobileNetV2PetClassifier:
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
        plot_model(model, to_file='moblenetv2_model_plot.png', show_shapes=True, show_layer_names=True)
        return model

    def train(self, epochs=5):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("mobilenetv2_pet.weights.h5")
        plot_confusion_matrix(self.model, self.test_data, self.class_names)

    def load_model_weights(self):
        if os.path.exists("mobilenetv2_pet.weights.h5"):
            self.model.load_weights("mobilenetv2_pet.weights.h5")
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

class ResNet50PetClassifier:
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
        image = tf.image.resize(image, (224, 224))
        image = tf.keras.applications.resnet50.preprocess_input(image)
        return image, label

    def build_model(self):
        base_model = tf.keras.applications.ResNet50(input_shape=(224, 224, 3), include_top=False, weights="imagenet")
        base_model.trainable = False  # можно разморозить несколько последних слоёв

        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(len(self.class_names), activation="softmax")
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                      loss="sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        plot_model(model, to_file='resnet_model_plot.png', show_shapes=True, show_layer_names=True)
        return model

    def train(self, epochs=5):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("resnet50_pet.weights.h5")
        plot_confusion_matrix(self.model, self.test_data, self.class_names)

    def load_model_weights(self):
        if os.path.exists("resnet50_pet.weights.h5"):
            self.model.load_weights("resnet50_pet.weights.h5")
            print("ResNet50 Weights loaded.")
        else:
            print("Weights not found, training ResNet50...")
            self.train()

    def classify(self, image):
        image = image.resize((224, 224))
        image = np.array(image)
        image = tf.keras.applications.resnet50.preprocess_input(image)
        image = np.expand_dims(image, axis=0)
        predictions = self.model.predict(image)
        class_index = np.argmax(predictions)
        confidence = np.max(predictions)
        return self.class_names[class_index], confidence
class EfficientNetB0PetClassifier:
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
        image = tf.image.resize(image, (224, 224))
        image = tf.keras.applications.efficientnet.preprocess_input(image)
        return image, label

    def build_model(self):
        base_model = tf.keras.applications.EfficientNetB0(
            input_shape=(224, 224, 3),
            include_top=False,
            weights="imagenet"
        )
        base_model.trainable = False  # можно разморозить несколько последних слоёв

        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(len(self.class_names), activation="softmax")
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                      loss="sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        plot_model(model, to_file='eff_model_plot.png', show_shapes=True, show_layer_names=True)
        return model

    def train(self, epochs=5):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("efficientnetb0_pet.weights.h5")
        plot_confusion_matrix(self.model, self.test_data, self.class_names)

    def load_model_weights(self):
        if os.path.exists("efficientnetb0_pet.weights.h5"):
            self.model.load_weights("efficientnetb0_pet.weights.h5")
            print("EfficientNetB0 Weights loaded.")
        else:
            print("Weights not found, training EfficientNetB0...")
            self.train()

    def classify(self, image):
        image = image.resize((224, 224))
        image = np.array(image)
        image = tf.keras.applications.efficientnet.preprocess_input(image)
        image = np.expand_dims(image, axis=0)
        predictions = self.model.predict(image)
        class_index = np.argmax(predictions)
        confidence = np.max(predictions)
        return self.class_names[class_index], confidence
class DenseNet121PetClassifier:
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
        image = tf.image.resize(image, (224, 224))
        image = tf.keras.applications.densenet.preprocess_input(image)
        return image, label

    def build_model(self):
        base_model = tf.keras.applications.DenseNet121(
            input_shape=(224, 224, 3),
            include_top=False,
            weights="imagenet"
        )
        base_model.trainable = False  # можно разморозить последние слои

        model = tf.keras.Sequential([
            base_model,
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(len(self.class_names), activation="softmax")
        ])

        model.compile(optimizer=tf.keras.optimizers.Adam(1e-4),
                      loss="sparse_categorical_crossentropy",
                      metrics=["accuracy"])
        plot_model(model, to_file='densenet_model_plot.png', show_shapes=True, show_layer_names=True)
        return model

    def train(self, epochs=5):
        self.model.fit(self.train_data, validation_data=self.test_data, epochs=epochs)
        self.model.save_weights("densenet121_pet.weights.h5")
        plot_confusion_matrix(self.model, self.test_data, self.class_names)

    def load_model_weights(self):
        if os.path.exists("densenet121_pet.weights.h5"):
            self.model.load_weights("densenet121_pet.weights.h5")
            print("DenseNet121 Weights loaded.")
        else:
            print("Weights not found, training DenseNet121...")
            self.train()

    def classify(self, image):
        image = image.resize((224, 224))
        image = np.array(image)
        image = tf.keras.applications.densenet.preprocess_input(image)
        image = np.expand_dims(image, axis=0)
        predictions = self.model.predict(image)
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


breed_descriptions_en = {
    "Abyssinian": "Abyssinian cats are known for their intelligence and playful personality. Care: Provide climbing spaces, mental stimulation, and regular playtime.",
    "Bengal": "Bengal cats have a wild appearance with a gentle domestic temperament. Care: They need lots of exercise, interactive toys, and space to climb.",
    "Bombay": "Bombay cats are sleek, black, and resemble miniature panthers. Care: Brush weekly and give them plenty of social interaction.",
    "Birman": "Birman cats are gentle and affectionate, with beautiful blue eyes. Care: Brush a few times a week and keep them indoors to protect their coat.",
    "British Shorthair": "Known for their round faces and dense coats, these cats are calm and dignified. Care: Brush weekly and control diet to prevent obesity.",
    "Maine Coon": "Large, friendly, and sociable cats with tufted ears and bushy tails. Care: Regular grooming and plenty of space for exercise are essential.",
    "Persian": "Persians are quiet, sweet, and require regular grooming due to long coats. Care: Daily brushing and frequent eye cleaning are necessary.",
    "Egyptian Mau": "One of the few naturally spotted domestic cat breeds. Care: Provide playtime and warmth, as they dislike cold climates.",
    "Ragdoll": "Ragdolls go limp when picked up and are extremely affectionate. Care: Brush weekly and ensure they stay indoors for safety.",
    "Russian Blue": "Elegant cats with a silvery-blue coat and green eyes. Care: Brush weekly and keep to a routine, as they dislike change.",
    "Siamese": "Talkative and affectionate cats with striking blue eyes. Care: Provide attention, toys, and interaction to prevent loneliness.",
    "Sphynx": "Hairless, energetic, and love human attention. Care: Bathe weekly and keep them warm in cooler climates.",
    "Boxer": "Boxers are strong, energetic dogs that love to play. Care: Daily exercise and consistent training are crucial.",
    "Keeshond": "Keeshonds are friendly and alert with a fox-like expression. Care: Brush several times a week to maintain their thick coat.",
    "Havanese": "Havanese dogs are cheerful and great companions. Care: Brush regularly and provide moderate exercise.",
    "Basset Hound": "Low-slung dogs with a great sense of smell and calm demeanor. Care: Clean ears often and ensure regular walks.",
    "English Setter": "Gentle and friendly with a speckled coat. Care: Brush frequently and provide lots of exercise.",
    "Miniature Pinscher": "Small but fearless, with a proud and confident personality. Care: Daily walks and protection from cold weather are important.",
    "Chihuahua": "Tiny and alert, Chihuahuas are full of personality. Care: Protect them from cold and avoid overfeeding.",
    "Great Pyrenees": "Large and calm guardians, often used for livestock protection. Care: Regular grooming and plenty of outdoor space are needed.",
    "German Shorthaired": "Versatile and athletic hunting dogs. Care: Daily exercise and mental stimulation are a must.",
    "Beagle": "Happy, curious dogs with great scent-tracking abilities. Care: Lots of exercise and attention to prevent mischief.",
    "Staffordshire Bull Terrier": "Muscular and loyal, known for their courage. Care: Provide firm but kind training and daily activity.",
    "English Cocker Spaniel": "Merry and energetic dogs with long ears. Care: Brush often and clean ears regularly.",
    "New Found Land": "Giant dogs known for water rescue and gentle nature. Care: Groom frequently and provide space for exercise.",
    "Pomeranian": "Fluffy and lively with a big personality in a tiny body. Care: Brush daily and monitor dental health.",
    "Leonberger": "Large, calm, and friendly giants. Care: Regular grooming and daily exercise are essential.",
    "American Pit Bull Terrier": "Strong and loyal, often misunderstood. Care: Consistent training and plenty of exercise are key.",
    "Wheaten Terrier": "Soft-coated terriers known for friendliness. Care: Brush often to prevent matting and provide regular exercise.",
    "Japanese Chin": "Elegant and charming lap dogs. Care: Brush frequently and protect from extreme heat.",
    "Samyod": "Fluffy white dogs with a signature “smile.” Care: Brush several times a week and ensure daily activity.",
    "Scottish Terrier": "Independent and dignified with a distinctive profile. Care: Regular hand-stripping or trimming is needed.",
    "Shiba Inu": "Alert and confident, with a fox-like appearance. Care: Brush weekly and provide firm training.",
    "Pug": "Small, sociable dogs with wrinkled faces. Care: Clean facial folds often and monitor breathing health.",
    "Saint Bernard": "Huge dogs with a gentle and patient temperament. Care: Brush frequently and ensure regular but moderate exercise.",
    "American Bulldog": "Strong, loyal, and athletic. Care: Provide structured training and daily exercise.",
    "Yorkshire Terrier": "Small dogs with big personalities and long silky hair. Care: Brush daily and trim hair regularly."
}

breed_descriptions_uk = {
    "Abyssinian": "Абіссінські коти відомі своєю розумністю та грайливим характером. Догляд: забезпечуйте простір для лазання, ігри та розумові завдання.",
    "Bengal": "Бенгальські коти мають дикий вигляд, але лагідний домашній темперамент. Догляд: потребують багато вправ, інтерактивних іграшок та місця для лазання.",
    "Bombay": "Бомбейські коти гладкі, чорні, схожі на мініатюрних пантер. Догляд: розчісуйте щотижня та приділяйте їм багато уваги.",
    "Birman": "Бірманські коти ніжні та ласкаві, з красивими синіми очима. Догляд: розчісуйте кілька разів на тиждень та тримайте вдома.",
    "British Shorthair": "Відомі своїми круглими обличчями та густою шерстю, ці коти спокійні та гідні. Догляд: розчісуйте раз на тиждень і контролюйте вагу.",
    "Maine Coon": "Великі, дружелюбні та соціальні коти з китицями на вухах та пухнастими хвостами. Догляд: регулярний догляд за шерстю та багато простору для активності.",
    "Persian": "Перські коти тихі, лагідні та потребують регулярного догляду через довгу шерсть. Догляд: щоденне розчісування та очищення очей.",
    "Egyptian Mau": "Одна з небагатьох природньо плямистих порід домашніх котів. Догляд: забезпечуйте ігри та тепло, бо вони не люблять холод.",
    "Ragdoll": "Реагують м'яко при підйомі та надзвичайно ласкаві. Догляд: розчісуйте раз на тиждень та тримайте вдома.",
    "Russian Blue": "Елегантні коти зі сріблясто-блакитною шерстю та зеленими очима. Догляд: розчісуйте раз на тиждень та дотримуйтеся рутини.",
    "Siamese": "Балакучі та ласкаві коти з виразними блакитними очима. Догляд: потребують багато уваги та ігор, щоб не нудьгували.",
    "Sphynx": "Лисі, енергійні та люблять увагу людини. Догляд: купайте щотижня та тримайте в теплі.",
    "Boxer": "Боксерські собаки сильні, енергійні та люблять грати. Догляд: потрібні щоденні вправи та послідовне виховання.",
    "Keeshond": "Кішонди дружелюбні та пильні з лисоподібним виразом морди. Догляд: розчісуйте кілька разів на тиждень.",
    "Havanese": "Гаванські собаки життєрадісні та чудові компаньйони. Догляд: розчісуйте регулярно та давайте помірні навантаження.",
    "Basset Hound": "Собаки з низьким корпусом, відмінним нюхом та спокійним характером. Догляд: часто чистіть вуха та забезпечуйте прогулянки.",
    "English Setter": "Ніжні та дружелюбні, з плямистою шерстю. Догляд: розчісуйте часто та давайте багато активності.",
    "Miniature Pinscher": "Маленькі, але безстрашні, з гордим та впевненим характером. Догляд: щоденні прогулянки та захист від холоду.",
    "Chihuahua": "Крихітні та пильні, повні характеру. Догляд: оберігайте від холоду та не перегодовуйте.",
    "Great Pyrenees": "Великі та спокійні охоронці, часто використовуються для захисту худоби. Догляд: регулярне розчісування та багато простору.",
    "German Shorthaired": "Універсальні та спортивні мисливські собаки. Догляд: щоденні вправи та розумові ігри.",
    "Beagle": "Щасливі, допитливі собаки з чудовим нюхом. Догляд: потрібні тривалі прогулянки та увага.",
    "Staffordshire Bull Terrier": "Міцні та віддані, відомі своєю сміливістю. Догляд: виховання з любов'ю та щоденна активність.",
    "English Cocker Spaniel": "Веселі та енергійні собаки з довгими вухами. Догляд: часто розчісуйте та чистіть вуха.",
    "New Found Land": "Гігантські собаки, відомі рятувальною діяльністю у воді та лагідним характером. Догляд: регулярний догляд за шерстю та багато простору.",
    "Pomeranian": "Пухнасті та життєрадісні, великі особистості у маленькому тілі. Догляд: щоденне розчісування та догляд за зубами.",
    "Leonberger": "Великі, спокійні та дружелюбні гіганти. Догляд: потребують щоденних прогулянок та регулярного розчісування.",
    "American Pit Bull Terrier": "Сильні та віддані, часто неправильно зрозумілі. Догляд: послідовне виховання та багато вправ.",
    "Wheaten Terrier": "М’якошерсті тер’єри, відомі своєю дружелюбністю. Догляд: часто розчісуйте, щоб уникнути ковтунів.",
    "Japanese Chin": "Елегантні та чарівні собаки-компаньйони. Догляд: регулярно розчісуйте та оберігайте від спеки.",
    "Samyod": "Пухнасті білі собаки з характерною «усмішкою». Догляд: кілька разів на тиждень розчісування та щоденні прогулянки.",
    "Scottish Terrier": "Самостійні та гідні з характерним профілем. Догляд: потрібне регулярне триммінгування шерсті.",
    "Shiba Inu": "Пильні та впевнені, з лисоподібною зовнішністю. Догляд: розчісуйте раз на тиждень та проводьте чітке виховання.",
    "Pug": "Маленькі, товариські собаки з морщинистими мордами. Догляд: чистіть складки на морді та слідкуйте за диханням.",
    "Saint Bernard": "Величезні собаки з лагідним та терплячим характером. Догляд: регулярне розчісування та помірні вправи.",
    "American Bulldog": "Сильні, віддані та спортивні. Догляд: потрібне виховання та щоденні фізичні навантаження.",
    "Yorkshire Terrier": "Маленькі собаки з великим характером та довгою шовковистою шерстю. Догляд: щоденне розчісування та підстригання шерсті."
}

breed_names_uk = {
    "Abyssinian": "Абіссінська",
    "Bengal": "Бенгальська",
    "Bombay": "Бомбейська",
    "Birman": "Бірманська",
    "British Shorthair": "Британська короткошерста",
    "Maine Coon": "Мейн-кун",
    "Persian": "Перська",
    "Egyptian Mau": "Єгипетська Мау",
    "Ragdoll": "Рагдолл",
    "Russian Blue": "Російська блакитна",
    "Siamese": "Сіамська",
    "Sphynx": "Сфінкс",
    "Boxer": "Боксер",
    "Keeshond": "Кішонд",
    "Havanese": "Гаванська",
    "Basset Hound": "Бассет-хаунд",
    "English Setter": "Англійський сетер",
    "Miniature Pinscher": "Мініатюрний пінчер",
    "Chihuahua": "Чихуахуа",
    "Great Pyrenees": "Великі Піренеї",
    "German Shorthaired": "Німецький короткошерстий",
    "Beagle": "Бігль",
    "Staffordshire Bull Terrier": "Стаффордширський бультер'єр",
    "English Cocker Spaniel": "Англійський кокер-спанієль",
    "New Found Land": "Ньюфаундленд",
    "Pomeranian": "Померанський шпіц",
    "Leonberger": "Леонбергер",
    "American Pit Bull Terrier": "Американський пітбультер'єр",
    "Wheaten Terrier": "Вітонський тер'єр",
    "Japanese Chin": "Японський Чін",
    "Samyod": "Самоїд",
    "Scottish Terrier": "Шотландський тер'єр",
    "Shiba Inu": "Шиба-іну",
    "Pug": "Мопс",
    "Saint Bernard": "Сенбернар",
    "American Bulldog": "Американський бульдог",
    "Yorkshire Terrier": "Йоркширський тер'єр"
}
def plot_confusion_matrix(model, dataset, class_names, save_path="confusion_matrix.png"):
    true_labels = []
    pred_labels = []

    for images, labels in dataset:
        preds = model.predict(images)
        preds = np.argmax(preds, axis=1)
        true_labels.extend(labels.numpy())
        pred_labels.extend(preds)

    cm = confusion_matrix(true_labels, pred_labels)

    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Confusion matrix saved to {save_path}")


def on_message(client, userdata, msg):
    try:
        # Получаем сообщение от MQTT
        payload = msg.payload.decode()
        user_id, model_N, image_b64, App_Localization = payload.split("||")
        print(model_N)
        print(App_Localization)
        if App_Localization.lower() == "uk":
            descriptions = breed_descriptions_uk
        else:
            descriptions = breed_descriptions_en

        # Декодируем base64 изображение
        image_bytes = base64.b64decode(image_b64)

        # Открываем изображение с помощью PIL
        image = Image.open(BytesIO(image_bytes))

        # Обновляем изображение в графическом интерфейсе (if need)
        update_image(image)
        image = image.resize((250, 250), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        global classifier
        if model_N== "MobileNetV2":
            classifier = MobileNetV2PetClassifier()
        if model_N== "ResNet50":
            classifier = ResNet50PetClassifier()
        if model_N== "EfficientNetB0":
            classifier = EfficientNetB0PetClassifier()
        if model_N== "DenseNet121":
            classifier = DenseNet121PetClassifier()
        if model_N == "CNN":
            classifier = CNNPetClassifier()
        # plot_confusion_matrix(classifier.model, classifier.test_data, classifier.class_names)
        # Классификация изображения
        predicted_label, confidence = classifier.classify(image)
       # plot_confusion_matrix(classifier.model, classifier.test_data, classifier.class_names)
        print(predicted_label)
        print(confidence)

        # Отправляем результат в MQTT
        result_topic = f"animal/result/{user_id}"

        formatted_label = predicted_label.replace('_', ' ').title()
        print(formatted_label)
        # Получаем описание

        description = descriptions.get(formatted_label, "No description available.")
        # Объединяем название и описание
        if App_Localization.lower() == "uk":
            breed_display_name = breed_names_uk.get(formatted_label, formatted_label)
            description = breed_descriptions_uk.get(formatted_label, "Опис недоступний.")
        else:
            breed_display_name = formatted_label
            description = breed_descriptions_en.get(formatted_label, "No description available.")
        message = f"{breed_display_name}: {description}"
        #message = f"{formatted_label}: {description}"

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
