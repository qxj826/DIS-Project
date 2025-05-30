BEGIN;

-- Clear tables
TRUNCATE favourite, snack
        RESTART IDENTITY CASCADE;

-- staging + load
CREATE TEMP TABLE food_stage (
    food      text,
    measure   text,
    grams     text,
    calories  text,
    protein   text,
    fat       text,
    sat_fat   text,
    fiber     text,
    carbs     text,
    category  text
);

\copy food_stage FROM 'data/nutrients_csvfile.csv' CSV HEADER;

-- insert
INSERT INTO snack (name, calories, grams, protein, carbs)
SELECT
    food,
    NULLIF( NULLIF( regexp_replace(calories, ',|-.+$', '', 'g'), 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(grams   , ',|-.+$', '', 'g'), 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(protein , ',|-.+$', '', 'g'), 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(carbs   , ',|-.+$', '', 'g'), 't'), '' )::numeric
FROM food_stage
WHERE food IS NOT NULL
ON CONFLICT ON CONSTRAINT snack_name_cal_unique DO NOTHING;

COMMIT;
