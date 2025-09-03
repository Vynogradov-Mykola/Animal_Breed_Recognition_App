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
import java.nio.charset.StandardCharsets;
import java.util.Locale;
import java.util.UUID;

public class MainActivity extends AppCompatActivity {

    private final String serverUri = "test.mosquitto.org";
    private final String userId = "user123";
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
    private String selectedTest = "test_1"; // значение по умолчанию

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
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        buttonSend = findViewById(R.id.button_send);
        textResult = findViewById(R.id.text_result);
        imageView = findViewById(R.id.image_view);
        list_of_models = findViewById(R.id.model_list);

        FloatingActionButton buttonLang = findViewById(R.id.button_lang);
        buttonLang.setOnClickListener(view -> {
            String currentLang = getResources().getConfiguration().locale.getLanguage();
            if (currentLang.equals("uk")) {
                setLocale("en"); // переключаем на английский
            } else {
                setLocale("uk"); // переключаем на украинский
            }
        });
// список значений
        String[] testOptions = {"test_1", "test_2", "test_3", "test_4"};

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
                selectedTest = "test_1"; // fallback
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
            builder.setTitle("Paste URL");

            final android.widget.EditText input = new android.widget.EditText(this);
            input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
            builder.setView(input);

            builder.setPositiveButton("Load", (dialog, which) -> {
                String url = input.getText().toString();
                loadImageFromUrl(url);
            });
            builder.setNegativeButton("Back", (dialog, which) -> dialog.cancel());

            builder.show();
        });

        connectToMqtt();
        setupLightSensor();
        buttonSend.setOnClickListener(view -> {
            pickImageLauncher.launch("image/*");
        });
    }
    private static final float LIGHT_THRESHOLD = 20;  // Порог освещенности для переключения темы
    private static final long DEBOUNCE_TIME = 50000;  // Время задержки между переключениями в миллисекундах
    private long lastChangeTime = 0;  // Время последнего изменения темы
    private float lastLightLevel = -1;  // Последний уровень освещенности


    private void setupLightSensor() {
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        if (sensorManager != null) {
            lightSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LIGHT);

            if (lightSensor != null) {
                lightListener = new SensorEventListener() {
                    @Override
                    public void onSensorChanged(SensorEvent event) {
                        float lightLevel = event.values[0]; // уровень освещенности в люксах
                        long currentTime = System.currentTimeMillis();

                        // Проверка, прошло ли достаточно времени с последнего изменения
                        if (currentTime - lastChangeTime < DEBOUNCE_TIME) {
                            return; // Если прошло слишком мало времени, игнорируем изменение
                        }

                        // Если уровень освещенности изменился существенно и прошел порог
                        if (lightLevel < LIGHT_THRESHOLD && !isDarkTheme && lightLevel != lastLightLevel) {
                            enableDarkTheme();
                            isDarkTheme = true;
                            lastLightLevel = lightLevel;
                            lastChangeTime = currentTime;
                        } else if (lightLevel >= LIGHT_THRESHOLD && isDarkTheme && lightLevel != lastLightLevel) {
                            enableLightTheme();
                            isDarkTheme = false;
                            lastLightLevel = lightLevel;
                            lastChangeTime = currentTime;
                        }
                    }

                    @Override
                    public void onAccuracyChanged(Sensor sensor, int accuracy) {
                    }
                };

                sensorManager.registerListener(lightListener, lightSensor, SensorManager.SENSOR_DELAY_NORMAL);
            }
        }
    }

    private void enableDarkTheme() {
        runOnUiThread(() -> {
            // Включаем темную тему без перезапуска активности
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES);
            Toast.makeText(this, "Dark theme", Toast.LENGTH_SHORT).show();
        });
    }

    private void enableLightTheme() {
        runOnUiThread(() -> {
            // Включаем светлую тему без перезапуска активности
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO);
            Toast.makeText(this, "Light theme", Toast.LENGTH_SHORT).show();
        });
    }

    private void connectToMqtt() {
        mqttClient.connect()
                .whenComplete((ack, throwable) -> {
                    if (throwable == null) {
                    //    runOnUiThread(() -> Toast.makeText(this, "MQTT Підключено", Toast.LENGTH_SHORT).show());
                        subscribeForResult();
                    } else {
                        runOnUiThread(() -> Toast.makeText(this, "Помилка підключення MQTT", Toast.LENGTH_SHORT).show());
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
            Toast.makeText(this, "Помилка вибору зображення", Toast.LENGTH_SHORT).show();
        }
    }
    private void loadImageFromUrl(String urlString) {
        new Thread(() -> {
            try {
                java.net.URL url = new java.net.URL(urlString);
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
                runOnUiThread(() -> Toast.makeText(this, "Не вдалося завантажити зображення з URL", Toast.LENGTH_SHORT).show());
            }
        }).start();
    }
    private void sendPhotoRequest() {
        if (selectedImageBytes == null) {
            Toast.makeText(this, "Спочатку виберіть зображення!", Toast.LENGTH_SHORT).show();
            return;
        }
//  сжатие изображения (если оно слишком большое)
        Bitmap bitmap = BitmapFactory.decodeByteArray(selectedImageBytes, 0, selectedImageBytes.length);
        Bitmap scaledBitmap = Bitmap.createScaledBitmap(bitmap, 800, 600, true);  // Уменьшаем размер
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        scaledBitmap.compress(Bitmap.CompressFormat.PNG, 80, stream);  // Сжимаем в PNG
        selectedImageBytes = stream.toByteArray();

        String imageBase64 = Base64.encodeToString(selectedImageBytes, Base64.NO_WRAP);
        String message = userId + "||" + selectedTest + "||" + imageBase64;

        runOnUiThread(() -> textResult.setText("Waiting for result"));
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
                    runOnUiThread(() -> textResult.setText("Breed recognized: " + result));
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
