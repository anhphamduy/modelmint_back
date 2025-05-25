#!/bin/bash

# SSH Key Setup Script for ModelMint
echo "Setting up SSH keys for ModelMint..."

# Check if keys exist
if [ ! -f ~/.ssh/modelmint_key ]; then
    echo "Error: Private key not found at ~/.ssh/modelmint_key"
    echo "Please run: ssh-keygen -t rsa -b 4096 -f ~/.ssh/modelmint_key -N '' -C 'modelmint-common-key'"
    exit 1
fi

if [ ! -f ~/.ssh/modelmint_key.pub ]; then
    echo "Error: Public key not found at ~/.ssh/modelmint_key.pub"
    exit 1
fi

# Set correct permissions
chmod 600 ~/.ssh/modelmint_key
chmod 644 ~/.ssh/modelmint_key.pub

echo "✅ SSH key files found and permissions set correctly"

# Read the public key
PUBLIC_KEY=$(cat ~/.ssh/modelmint_key.pub)

# Create or update .env file
ENV_FILE=".env"

echo ""
echo "📝 Adding SSH configuration to $ENV_FILE..."

# Remove existing SSH key entries if they exist
sed -i.bak '/^COMMON_SSH_/d' "$ENV_FILE" 2>/dev/null || true

# Add new SSH key configuration
cat >> "$ENV_FILE" << EOF

# Common SSH Key Configuration
COMMON_SSH_KEY_NAME=modelmint-common-key
COMMON_SSH_PUBLIC_KEY=$PUBLIC_KEY
COMMON_SSH_PRIVATE_KEY_PATH=$HOME/.ssh/modelmint_key
EOF

echo "✅ Environment variables added to $ENV_FILE"
echo ""
echo "🔑 SSH Key Information:"
echo "   Private Key: $HOME/.ssh/modelmint_key"
echo "   Public Key:  $HOME/.ssh/modelmint_key.pub"
echo "   Key Name:    modelmint-common-key"
echo ""
echo "📋 Next steps:"
echo "1. Source your environment: source .env (if using direnv) or restart your application"
echo "2. Use setup_common_ssh_key('provider_name') to add the key to your cloud providers"
echo "3. Launch instances with launch_gpu_instance() - they'll automatically use this key"
echo ""
echo "�� Setup complete!" 