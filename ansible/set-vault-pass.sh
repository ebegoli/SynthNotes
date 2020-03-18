echo "Please enter your Ansible Vault Password: "
read -sr ANSIBLE_VAULT_PASSWORD_INPUT
export ANSIBLE_VAULT_PASSWORD=$ANSIBLE_VAULT_PASSWORD_INPUT
