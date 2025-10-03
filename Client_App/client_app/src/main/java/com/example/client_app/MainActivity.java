package com.example.client_app;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;

import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.util.Base64;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.widget.ArrayAdapter;
import android.widget.Spinner;
import android.widget.AdapterView;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.hivemq.client.mqtt.MqttClient;
import com.hivemq.client.mqtt.datatypes.MqttQos;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private final String serverUri = "test.mosquitto.org";
    private String userId;
    private final String topicPhoto = "animal/photo";
    private final String topicResultPrefix = "animal/result/";
    private SensorManager sensorManager;
    private Sensor lightSensor;
    private SensorEventListener lightListener;
    private boolean isDarkTheme = false;
    private Button buttonSend;
    private TextView textResult;
    private ImageView imageView;
    private byte[] selectedImageBytes = null;
    private Spinner list_of_models;
    private String selectedTest = "MobileNetV2"; // значение по умолчанию

    private final com.hivemq.client.mqtt.mqtt3.Mqtt3AsyncClient mqttClient = MqttClient.builder()
            .useMqttVersion3()
            .serverHost(serverUri)
            .serverPort(1883)
            .identifier(UUID.randomUUID().toString())
            .buildAsync();

    private final ActivityResultLauncher<String> pickImageLauncher =
            registerForActivityResult(new ActivityResultContracts.GetContent(), uri -> {
                if (uri != null) {
                    loadImage(uri);
                }
            });
    private void setLocale(String langCode) {
        Locale locale = new Locale(langCode);
        Locale.setDefault(locale);

        android.content.res.Configuration config = new android.content.res.Configuration();
        config.setLocale(locale);

        getResources().updateConfiguration(config, getResources().getDisplayMetrics());

        recreate(); // перезапускаем активность, чтобы применился язык
    }
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        userId = Settings.Secure.getString(
                getContentResolver(),
                Settings.Secure.ANDROID_ID
        );
        buttonSend = findViewById(R.id.button_send);
        textResult = findViewById(R.id.text_result);
        imageView = findViewById(R.id.image_view);
        list_of_models = findViewById(R.id.model_list);
        String systemLang = Locale.getDefault().getLanguage();

        // Если язык системы русский, меняем на украинский
        if (systemLang.equals("ru")) {
            setLocale("uk");  // Используем ваш метод setLocale
        }
        FloatingActionButton buttonLang = findViewById(R.id.button_lang);
        buttonLang.setOnClickListener(view -> {
            // Получаем текущий язык приложения из ресурсов
            String currentLang = getResources().getConfiguration().getLocales().get(0).getLanguage();

            if (currentLang.equals("ru")) {
                setLocale("en");  //
            }
            if (currentLang.equals("uk")) {
                setLocale("en"); // переключаем на английский
            } else {
                setLocale("uk"); // переключаем на украинский
            }
        });
// список значений
        String[] testOptions = {"MobileNetV2", "CNN", "ResNet50", "EfficientNetB0", "DenseNet121"};

// адаптер
        ArrayAdapter<String> adapter = new ArrayAdapter<>(
                this,
                android.R.layout.simple_spinner_item,
                testOptions
        );
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        list_of_models.setAdapter(adapter);

// обработка выбора
        list_of_models.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, android.view.View view, int position, long id) {
                selectedTest = parent.getItemAtPosition(position).toString();
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {
                selectedTest = "MobileNetV2"; // fallback
            }
        });


        FloatingActionButton buttonBreeds = findViewById(R.id.button_breeds);
        buttonBreeds.setOnClickListener(view -> {
            Intent intent = new Intent(MainActivity.this, BreedListActivity.class);
            startActivity(intent);
        });
        FloatingActionButton buttonUrl = findViewById(R.id.button_url);
        buttonUrl.setOnClickListener(view -> {
            android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(this);
            builder.setTitle(R.string.paste_url);

            final android.widget.EditText input = new android.widget.EditText(this);
            input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
            builder.setView(input);

            builder.setPositiveButton(R.string.load_url, (dialog, which) -> {
                String url = input.getText().toString();
                loadImageFromUrl(url);
            });
            builder.setNegativeButton(R.string.back_url, (dialog, which) -> dialog.cancel());

            builder.show();
        });

        connectToMqtt();

        buttonSend.setOnClickListener(view -> {
            pickImageLauncher.launch("image/*");
        });
    }





    private void connectToMqtt() {
        mqttClient.connect()
                .whenComplete((ack, throwable) -> {
                    if (throwable == null) {

                        subscribeForResult();
                    } else {
                        runOnUiThread(() -> Toast.makeText(this, R.string.mqtt_connect, Toast.LENGTH_SHORT).show());
                    }
                });
    }

    private void loadImage(Uri uri) {
        try {
            InputStream inputStream = getContentResolver().openInputStream(uri);
            selectedImageBytes = new byte[inputStream.available()];
            inputStream.read(selectedImageBytes);
            imageView.setImageURI(uri);

            sendPhotoRequest();
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this, R.string.ImageError, Toast.LENGTH_SHORT).show();
        }
    }
    private void loadImageFromUrl(String urlString) {
        new Thread(() -> {
            try {
                URL url = new URL(urlString);
                InputStream inputStream = url.openStream();
                Bitmap bitmap = BitmapFactory.decodeStream(inputStream);

                runOnUiThread(() -> {
                    imageView.setImageBitmap(bitmap);

                    // Сжатие и отправка MQTT
                    ByteArrayOutputStream stream = new ByteArrayOutputStream();
                    bitmap.compress(Bitmap.CompressFormat.PNG, 80, stream);
                    selectedImageBytes = stream.toByteArray();

                    sendPhotoRequest();
                });
            } catch (Exception e) {
                e.printStackTrace();
                runOnUiThread(() -> Toast.makeText(this, R.string.Cantloadurl, Toast.LENGTH_SHORT).show());
            }
        }).start();
    }
    private void sendPhotoRequest() {
        if (selectedImageBytes == null) {
            Toast.makeText(this, R.string.ChooseImageFirst, Toast.LENGTH_SHORT).show();
            return;
        }
//  сжатие изображения (если оно слишком большое)
        Bitmap bitmap = BitmapFactory.decodeByteArray(selectedImageBytes, 0, selectedImageBytes.length);
        Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, 800, 600, true);  // Уменьшаем размер
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        scaledBitmap.compress(Bitmap.CompressFormat.PNG, 80, stream);  // Сжимаем в PNG
        selectedImageBytes = stream.toByteArray();

        String imageBase64 = Base64.encodeToString(selectedImageBytes, Base64.NO_WRAP);
        String currentLang = Locale.getDefault().getLanguage();
        if (currentLang=="ru") currentLang="uk";
        String message = userId + "||" + selectedTest + "||" + imageBase64 + "||" + currentLang;

        runOnUiThread(() -> textResult.setText(R.string.waiting_for_result));
        mqttClient.publishWith()
                .topic(topicPhoto)
                .qos(MqttQos.AT_LEAST_ONCE)
                .payload(message.getBytes(StandardCharsets.UTF_8))
                .send();
    }

    private void subscribeForResult() {
        mqttClient.subscribeWith()
                .topicFilter(topicResultPrefix + userId)
                .qos(MqttQos.AT_LEAST_ONCE)
                .callback(publish -> {
                    String result = new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8);
                    String res_rec = getString(R.string.recognition);
                    runOnUiThread(() -> textResult.setText(res_rec + result));
                })
                .send();
    }
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (sensorManager != null && lightListener != null) {
            sensorManager.unregisterListener(lightListener);
        }
    }

}
