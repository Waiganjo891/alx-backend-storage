-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS bands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    origin VARCHAR(255),
    fans INT
);

-- Select the origins and sum of fans, then order by the total number of fans in descending order
SELECT origin, SUM(fans) AS nb_fans
FROM bands
GROUP BY origin
ORDER BY nb_fans DESC;
