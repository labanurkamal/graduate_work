SELECT id::text, name
FROM content.genre
WHERE modified > $1
ORDER BY modified