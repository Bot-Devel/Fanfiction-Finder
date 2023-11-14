# Script to update the bots and restart the services in the VPS

# Updating the bots
cd /home/arbaaz/Projects/Fanfiction-Finder
git reset --hard HEAD~1
git pull

cd /home/arbaaz/Projects/Quote-Finder
git reset --hard HEAD~1
git pull

# Updating the services
sudo cp /home/arbaaz/Projects/Quote-Finder/Quote-Finder.service  /etc/systemd/system/Quote-Finder.service
sudo cp /home/arbaaz/Projects/Fanfiction-Finder/Fanfiction-Finder.service  /etc/systemd/system/Fanfiction-Finder.service
sudo systemctl daemon-reload
sudo systemctl restart Fanfiction-Finder.service
sudo systemctl restart Quote-Finder.service