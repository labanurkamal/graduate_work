SELECT id::text, full_name
FROM content.person
WHERE modified > $1
ORDER BY modified