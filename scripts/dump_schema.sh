#!/bin/bash

# supply postgresql db url as arg
if [ $# -lt 1 ] || [ $# -gt 2 ]; then
	echo "Usage: $0 <postgres url> [output_file]"
	exit 1
fi

OUTPUT_FILE="${2:-scripts/schema.sql}"

# Dump schema with public-safe flags:
# -O, --no-owner: skip ALTER OWNER commands
# -x, --no-privileges: don't dump GRANT/REVOKE commands
# --no-comments: don't dump comments
# --schema-only: structure only, no data
# Then filter out Neon-specific \restrict and \unrestrict tokens
pg_dump "$1" \
	--schema-only \
	--no-owner \
	--no-privileges \
	--no-comments | \
	sed -e '/^\\restrict/d' -e '/^\\unrestrict/d' > "$OUTPUT_FILE"

echo "schema dumped to $OUTPUT_FILE (sanitized for public repo)"
