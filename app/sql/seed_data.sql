\echo '=== Snackster bootstrap ==='

BEGIN;
TRUNCATE favourite, snack RESTART IDENTITY CASCADE;

CREATE TEMP TABLE food_stage(
  food text, measure text, grams text,
  calories text, protein text, fat text,
  sat_fat text, fiber text, carbs text, category text
);

\copy food_stage FROM 'data/nutrients_csvfile.csv' CSV HEADER;

INSERT INTO snack(name, calories, grams, protein, carbs)
SELECT
  food,
  NULLIF(regexp_replace(calories,'[^0-9\.]','','g'),'')::numeric,
  NULLIF(regexp_replace(grams   ,'[^0-9\.]','','g'),'')::numeric,
  NULLIF(regexp_replace(protein ,'[^0-9\.]','','g'),'')::numeric,
  NULLIF(regexp_replace(carbs   ,'[^0-9\.]','','g'),'')::numeric
FROM food_stage
WHERE food IS NOT NULL
ON CONFLICT ON CONSTRAINT snack_name_cal_unique DO NOTHING;
COMMIT;

\echo '=== Snackster bootstrap done ==='
