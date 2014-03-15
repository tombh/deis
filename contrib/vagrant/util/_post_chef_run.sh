#!/bin/bash

function echo_bold {
  echo -e "\033[1m$1\033[0m"
}

function echo_red {
  echo -e "\e[00;31m$1\e[00m"
}

# Create a globally accessible command for dshell. So you can easily log in to a container.
if [ ! -h /usr/local/bin/dsh ]; then
	sudo ln -s /vagrant/contrib/vagrant/util/dshell /usr/local/bin/dsh
fi

echo_bold "Updating Django site object from 'example.com' to 'deis-controller'..."
cat <<EOF | sudo dsh deis-database
su postgres
psql deis -c " \
  UPDATE django_site \
  SET domain = 'deis-controller.local', \
      name = 'deis-controller.local' \
  WHERE id = 1 " >/dev/null
EOF

if [ $? -eq 0 ]; then
  echo_bold "Site object updated."
fi

echo_bold  "Giving deis role permission to create databases for testing..."
cat <<EOF | dsh deis-database
su postgres
psql -c "ALTER USER deis CREATEDB;" > /dev/null
EOF

if [ $? -eq 0 ]; then
  echo_bold "Deis role granted create permission."
fi

echo_bold "Installing development dependencies..."
cat <<-EOF | dsh deis-server
	cd /app/deis
	pip install -r dev_requirements.txt > /dev/null
EOF
if [ $? -eq 0 ]; then
  echo_bold "Development dependencies installed."
fi
