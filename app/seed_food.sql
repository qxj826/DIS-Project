BEGIN;

------------------------------------------------------------------
-- 1. Clear existing data ----------------------------------------
------------------------------------------------------------------
TRUNCATE favourite, preference, recommendation, snack
        RESTART IDENTITY CASCADE;

------------------------------------------------------------------
-- 2. Ensure snack table exists (with id + columns) --------------
------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS snack (
    id       SERIAL PRIMARY KEY,
    name     text,
    calories numeric,
    grams    numeric,
    protein  numeric,
    carbs    numeric
);

-- 2b. add UNIQUE constraint if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'snack_name_cal_unique'
    ) THEN
        ALTER TABLE snack
          ADD CONSTRAINT snack_name_cal_unique
          UNIQUE (name, calories);
    END IF;
END $$;

------------------------------------------------------------------
-- 3. staging table + CSV import ---------------------------------
------------------------------------------------------------------
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

------------------------------------------------------------------
-- 4. clean & load ------------------------------------------------
------------------------------------------------------------------
INSERT INTO snack (name, calories, grams, protein, carbs)
SELECT
    food,
    NULLIF( NULLIF( regexp_replace(calories, ',|-.+$', '', 'g')
                   , 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(grams   , ',|-.+$', '', 'g')
                   , 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(protein , ',|-.+$', '', 'g')
                   , 't'), '' )::numeric,
    NULLIF( NULLIF( regexp_replace(carbs   , ',|-.+$', '', 'g')
                   , 't'), '' )::numeric
FROM food_stage
WHERE food IS NOT NULL
ON CONFLICT ON CONSTRAINT snack_name_cal_unique DO NOTHING;


COMMIT;