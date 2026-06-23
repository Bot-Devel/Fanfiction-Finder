```bash
#!/usr/bin/env bash

set -Eeuo pipefail

readonly FF_DIR="/home/arbaaz/Projects/Fanfiction-Finder"
readonly QF_DIR="/home/arbaaz/Projects/Quote-Finder"
readonly BRANCH="main"

log() {
    printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

deploy_project() {
    local project_directory="$1"
    shift

    local services=("$@")

    if [[ ! -d "$project_directory/.git" ]]; then
        echo "Error: $project_directory is not a Git repository." >&2
        return 1
    fi

    log "Deploying $project_directory"

    cd "$project_directory"

    log "Syncing with origin/$BRANCH"

    git fetch --prune origin "$BRANCH"
    git reset --hard "origin/$BRANCH"
    git clean -fd

    if [[ -f "requirements.txt" ]]; then
        log "Updating Python dependencies"

        if [[ -x ".venv/bin/python" ]]; then
            .venv/bin/python -m pip install \
                --disable-pip-version-check \
                -r requirements.txt
        elif [[ -x "/home/arbaaz/.pyenv/versions/fanfic-finder-bot/bin/python" \
            && "$project_directory" == "$FF_DIR" ]]; then
            /home/arbaaz/.pyenv/versions/fanfic-finder-bot/bin/python \
                -m pip install \
                --disable-pip-version-check \
                -r requirements.txt
        else
            echo "Error: No Python environment found for $project_directory." >&2
            return 1
        fi
    fi

    if [[ -f "alembic.ini" ]]; then
        if [[ -x ".venv/bin/alembic" ]]; then
            log "Running database migrations"
            .venv/bin/alembic upgrade head
        else
            echo "Error: alembic.ini exists but .venv/bin/alembic was not found." >&2
            return 1
        fi
    fi

    for service in "${services[@]}"; do
        local service_file="$project_directory/$service.service"

        if [[ ! -f "$service_file" ]]; then
            echo "Error: Service file not found: $service_file" >&2
            return 1
        fi

        log "Installing $service.service"

        sudo install \
            -m 0644 \
            "$service_file" \
            "/etc/systemd/system/$service.service"
    done

    sudo systemctl daemon-reload

    for service in "${services[@]}"; do
        log "Restarting $service.service"

        sudo systemctl restart "$service.service"

        sleep 2

        if ! sudo systemctl is-active --quiet "$service.service"; then
            echo "Error: $service.service failed to start." >&2

            sudo systemctl status \
                "$service.service" \
                --no-pager || true

            sudo journalctl \
                -u "$service.service" \
                -n 50 \
                --no-pager || true

            return 1
        fi

        log "$service.service is active"
    done
}

usage() {
    echo "Usage: $0 {all|qf|ff}"
}

main() {
    if [[ $# -ne 1 ]]; then
        usage
        exit 1
    fi

    case "$1" in
        all)
            deploy_project \
                "$FF_DIR" \
                "Fanfiction-Finder"

            deploy_project \
                "$QF_DIR" \
                "quote-finder-bot" \
                "quote-finder-worker"
            ;;

        qf)
            deploy_project \
                "$QF_DIR" \
                "quote-finder-bot" \
                "quote-finder-worker"
            ;;

        ff)
            deploy_project \
                "$FF_DIR" \
                "Fanfiction-Finder"
            ;;

        *)
            echo "Invalid option: $1" >&2
            usage
            exit 1
            ;;
    esac
}

main "$@"
```
