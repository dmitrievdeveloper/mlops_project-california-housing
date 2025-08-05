#!/bin/sh

# Start MinIO server in background
/usr/bin/docker-entrypoint.sh server /data --console-address ":9001" &

# Wait for MinIO to be ready
until curl -f http://localhost:9000/minio/health/live; do 
  sleep 1
done

# Configure client and create buckets
mc alias set local http://localhost:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}
for bucket in $(echo ${MINIO_BUCKETS} | tr "," " "); do
  mc mb local/${bucket} || true
  mc policy set public local/${bucket} || true
done

# Keep container running
wait
