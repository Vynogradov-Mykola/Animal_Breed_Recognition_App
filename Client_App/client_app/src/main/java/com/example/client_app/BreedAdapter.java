package com.example.client_app;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.*;

import java.util.List;

public class BreedAdapter extends ArrayAdapter<Breed> {
    public BreedAdapter(Context context, List<Breed> breeds) {
        super(context, 0, breeds);

    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        Breed breed = getItem(position);

        if (convertView == null) {
            convertView = LayoutInflater.from(getContext()).inflate(R.layout.breed_list_item, parent, false);
        }

        ImageView image = convertView.findViewById(R.id.breed_image);
        TextView name = convertView.findViewById(R.id.breed_name);
        TextView desc = convertView.findViewById(R.id.breed_description);

        image.setImageResource(breed.imageResId);
        name.setText(breed.name);
        desc.setText(breed.description);

        return convertView;
    }
}
