#!/bin/sh
set -eu

case "$LAB" in
    rest/crapi)
        compose_file=labs/rest/crapi/deploy/docker/docker-compose.yml
        export LISTEN_IP=127.0.0.1
        export VERSION=1.1.6
        ;;
    rest/*|graphql/*|grpc/*)
        case "${LAB#*/}" in
            ''|*[!a-z0-9-]*)
                printf '%s\n' 'Use LAB=tipo/nome com letras minúsculas, dígitos e hífens.' >&2
                exit 2
                ;;
        esac
        compose_file="labs/$LAB/compose.yaml"
        ;;
    *)
        printf '%s\n' 'Tipo de API desconhecido. Rode make list.' >&2
        exit 2
        ;;
esac

if [ ! -f "$compose_file" ]; then
    printf 'Compose ausente: %s. Consulte o README.md.\n' "$compose_file" >&2
    exit 2
fi

case "$1" in
    up) set -- up -d ;;
    down) set -- down ;;
    logs) set -- logs --follow ;;
    status) set -- ps ;;
    *) exit 2 ;;
esac

exec docker compose -p "vl-${LAB%/*}-${LAB#*/}" -f "$compose_file" "$@"
