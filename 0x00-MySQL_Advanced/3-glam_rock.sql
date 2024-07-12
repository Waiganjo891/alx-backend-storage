-- Calculate the lifespan of bands with 'Glam rock' as their main style
USE holberton;
SELECT 
    band_name,
    CASE
        WHEN split IS NULL THEN 2022 - formed
        ELSE split - formed
    END AS lifespan
FROM
    metal_bands
WHERE
    main_style = 'Glam rock'
ORDER BY
    lifespan DESC;
