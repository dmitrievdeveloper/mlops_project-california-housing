FROM minio/minio:RELEASE.2025-04-22T22-12-26Z

# Install mc (MinIO client)
RUN curl -O https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/bin/mc

# Copy initialization script
COPY ./scripts/init-minio.sh /init-minio.sh
RUN chmod +x /init-minio.sh

ENTRYPOINT ["/init-minio.sh"]
