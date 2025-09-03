    package com.example.client_app;

    import android.content.Context;

    import java.util.ArrayList;
    import java.util.List;

    public class BreedData {
        public static List<Breed> getAllBreeds(Context context) {
            List<Breed> list = new ArrayList<>();

            // Cats
            list.add(new Breed(
                    context.getString(R.string.breed_abyssinian_name),
                    context.getString(R.string.breed_abyssinian_desc),
                    R.drawable.abyssinian
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_bengal_name),
                    context.getString(R.string.breed_bengal_desc),
                    R.drawable.bengal
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_bombay_name),
                    context.getString(R.string.breed_bombay_desc),
                    R.drawable.bombay
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_birman_name),
                    context.getString(R.string.breed_birman_desc),
                    R.drawable.birman
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_british_shorthair_name),
                    context.getString(R.string.breed_british_shorthair_desc),
                    R.drawable.british_shorthair
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_maine_coon_name),
                    context.getString(R.string.breed_maine_coon_desc),
                    R.drawable.maine_coon
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_persian_name),
                    context.getString(R.string.breed_persian_desc),
                    R.drawable.persian
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_egyptian_mau_name),
                    context.getString(R.string.breed_egyptian_mau_desc),
                    R.drawable.egyptian_mau
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_ragdoll_name),
                    context.getString(R.string.breed_ragdoll_desc),
                    R.drawable.ragdoll
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_russian_blue_name),
                    context.getString(R.string.breed_russian_blue_desc),
                    R.drawable.russian_blue
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_siamese_name),
                    context.getString(R.string.breed_siamese_desc),
                    R.drawable.siamese
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_sphynx_name),
                    context.getString(R.string.breed_sphynx_desc),
                    R.drawable.sphynx
            ));

            // Dogs
            list.add(new Breed(
                    context.getString(R.string.breed_boxer_name),
                    context.getString(R.string.breed_boxer_desc),
                    R.drawable.boxer
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_keeshond_name),
                    context.getString(R.string.breed_keeshond_desc),
                    R.drawable.keeshond
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_havanese_name),
                    context.getString(R.string.breed_havanese_desc),
                    R.drawable.havanese
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_basset_hound_name),
                    context.getString(R.string.breed_basset_hound_desc),
                    R.drawable.basset_hound
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_english_setter_name),
                    context.getString(R.string.breed_english_setter_desc),
                    R.drawable.english_setter
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_miniature_pinscher_name),
                    context.getString(R.string.breed_miniature_pinscher_desc),
                    R.drawable.miniature_pinscher
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_chihuahua_name),
                    context.getString(R.string.breed_chihuahua_desc),
                    R.drawable.chihuahua
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_great_pyrenees_name),
                    context.getString(R.string.breed_great_pyrenees_desc),
                    R.drawable.great_pyrenees
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_german_shorthaired_name),
                    context.getString(R.string.breed_german_shorthaired_desc),
                    R.drawable.german_shorthaired
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_beagle_name),
                    context.getString(R.string.breed_beagle_desc),
                    R.drawable.beagle
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_staffordshire_bull_terrier_name),
                    context.getString(R.string.breed_staffordshire_bull_terrier_desc),
                    R.drawable.staffordshire_bull_terrier
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_english_cocker_spaniel_name),
                    context.getString(R.string.breed_english_cocker_spaniel_desc),
                    R.drawable.english_cocker_spaniel
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_newfoundland_name),
                    context.getString(R.string.breed_newfoundland_desc),
                    R.drawable.newfoundland
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_pomeranian_name),
                    context.getString(R.string.breed_pomeranian_desc),
                    R.drawable.pomeranian
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_leonberger_name),
                    context.getString(R.string.breed_leonberger_desc),
                    R.drawable.leonberger
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_american_pit_bull_terrier_name),
                    context.getString(R.string.breed_american_pit_bull_terrier_desc),
                    R.drawable.american_pit_bull_terrier
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_wheaten_terrier_name),
                    context.getString(R.string.breed_wheaten_terrier_desc),
                    R.drawable.wheaten_terrier
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_japanese_chin_name),
                    context.getString(R.string.breed_japanese_chin_desc),
                    R.drawable.japanese_chin
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_samoyed_name),
                    context.getString(R.string.breed_samoyed_desc),
                    R.drawable.samoyed
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_scottish_terrier_name),
                    context.getString(R.string.breed_scottish_terrier_desc),
                    R.drawable.scottish_terrier
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_shiba_inu_name),
                    context.getString(R.string.breed_shiba_inu_desc),
                    R.drawable.shiba_inu
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_pug_name),
                    context.getString(R.string.breed_pug_desc),
                    R.drawable.pug
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_saint_bernard_name),
                    context.getString(R.string.breed_saint_bernard_desc),
                    R.drawable.saint_bernard
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_american_bulldog_name),
                    context.getString(R.string.breed_american_bulldog_desc),
                    R.drawable.american_bulldog
            ));
            list.add(new Breed(
                    context.getString(R.string.breed_yorkshire_terrier_name),
                    context.getString(R.string.breed_yorkshire_terrier_desc),
                    R.drawable.yorkshire_terrier
            ));

            return list;
        }
    }
