#!/usr/bin/env bash

if [ -z "${3}" ]
then
      echo "At least 3 arguments are needed"
      echo "1 -> Target URL to download the file"
      echo "2 -> Name of the output file"
      echo "3 -> Number of chunks (file will be downloaded in chunks of size total_size/num_chunks)"
      exit 1
fi

URL="${1}"
OUTPUT_FILE="${2}"
CHUNKS="${3}"

SIZE=$(curl -sI "${URL}" | awk '/^Content-Length:/ {print $2}' | tr -d '\r')
CHUNK_SIZE=$(( SIZE / CHUNKS ))

for ((i=0; i<CHUNKS; i++)); do
    START=$(( i * CHUNK_SIZE ))
    END=""
    if [ ${i} -ne $(( CHUNKS - 1 )) ]; then
        END=$(( (i+1) * CHUNK_SIZE - 1 ))
    fi
    RANGE="${START}-${END}"
    curl -s --retry 3 --retry-delay 5 -r "${RANGE}" -o "${OUTPUT_FILE}.part${i}" "${URL}" &
done

# Wait for download threads to finish
wait

# Concatenate output
rm -f "${OUTPUT_FILE}"
for ((i=0; i<CHUNKS; i++)); do
    cat "${OUTPUT_FILE}.part${i}" >> "${OUTPUT_FILE}"
done

# Clean chunks
rm -f "${OUTPUT_FILE}.part"*