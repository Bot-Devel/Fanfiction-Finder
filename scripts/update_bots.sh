#!/bin/bash

# Function to update and restart services
update_and_restart() {
    local project_directory=$1
    local service_name=$2

    # Updating the bot
    cd "$project_directory"
    git reset --hard HEAD~1
    git pull

    # Updating the service
    sudo cp "$project_directory/$service_name.service" "/etc/systemd/system/$service_name.service"
    sudo systemctl daemon-reload
    sudo systemctl restart "$service_name.service"
}

# Main script

# Check for the argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 {all|qf|ff}"
    exit 1
fi

# Determine which option was provided
case "$1" in
    all)
        # Update and restart both bots and services
        update_and_restart "/home/arbaaz/Projects/Fanfiction-Finder" "Fanfiction-Finder"
        update_and_restart "/home/arbaaz/Projects/Quote-Finder" "Quote-Finder"
        ;;
    qf)
        # Update and restart Quote-Finder bot and service
        update_and_restart "/home/arbaaz/Projects/Quote-Finder" "Quote-Finder"
        ;;
    ff)
        # Update and restart Fanfiction-Finder bot and service
        update_and_restart "/home/arbaaz/Projects/Fanfiction-Finder" "Fanfiction-Finder"
        ;;
    *)
        echo "Invalid option: $1. Use {all|qf|ff}"
        exit 1
        ;;
esac
