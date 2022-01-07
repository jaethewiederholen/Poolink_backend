#/usr/bin/env bash

# Install necessary (but not required) tools
apt-get update && apt-get install -y \
    bash-completion

cat <<EOF >> ~/.bashrc
source /etc/profile.d/bash_completion.sh
EOF

# Install pre-commit hook
$(PYTHON_COMMAND_EXECUTOR) pre-commit install --install-hooks
