-- Ranking country origins by the number of non-unique fans
SELECT 
    origin,
    SUM(nb_fans) AS total_fans
FROM 
    bands
GROUP BY 
    origin
ORDER BY 
    total_fans DESC;
