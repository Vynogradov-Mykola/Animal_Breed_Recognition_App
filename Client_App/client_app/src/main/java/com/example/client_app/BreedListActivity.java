package com.example.client_app;

import android.os.Bundle;
import android.widget.Button;
import android.widget.ListView;
import androidx.appcompat.app.AppCompatActivity;

import java.util.List;

public class BreedListActivity extends AppCompatActivity {

    private ListView listView;
    private BreedAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_breed_list);

        listView = findViewById(R.id.breed_list_view);
        Button buttonBack = findViewById(R.id.button_back);
        buttonBack.setOnClickListener(v -> {
            // Закрытие текущей активности и возврат на предыдущую
            finish();
        });
        List<Breed> breeds = BreedData.getAllBreeds(this);
        adapter = new BreedAdapter(this, breeds);
        listView.setAdapter(adapter);
    }
}
