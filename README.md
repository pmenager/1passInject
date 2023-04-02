# 1PassInject

1PassInject is a Python script that automates the process of injecting 1Password secrets into your configuration files
or templates. The script supports both direct file download and processing of templates with embedded placeholders for
1Password values.

### Use cases

1PassInject is designed to streamline the process of managing development secrets and sharing them between team members
using 1Password. This script is particularly useful for handling frequently updated passwords, quickly setting up
development environments, and ensuring that secrets remain synchronized across the team. By using 1Password templates,
which can be versioned, developers can maintain a consistent and up-to-date configuration across their local
environments.

:warning: **Important**: This tool is designed for non-production or non-critical secrets, such as development secrets
and files. It is not recommended to store plain-text secrets on a computer, as it may expose sensitive information. Use
this tool with caution and always follow best security practices.

## Prerequisites

- Python 3.6 or later
- 1Password CLI (v1.0.0 or later) installed and configured on your system

## Installation

Clone the 1PassInject repository or download the script directly from the repository.

## Usage

1PassInject relies on a configuration file named 1passwordrc.yml, which should be located in the same directory where
the script is executed. The configuration file contains a list of items and their corresponding settings.

Here's an example of a 1passwordrc.yml file:

```yaml
items:
  - name: database_config
    type: template
    source: templates/database_config_template.yml
    destination: configs/database_config.yml
    account: something.1password.com
    vault: Development
    item: database_credentials
  - name: ssl_certificate
    type: file
    item: ssl_certificate_document
    destination: configs/ssl_certificate.pem
    account: something.1password.com
    vault: Dev env
```

In your templates, use the following placeholders to indicate which 1Password values should be injected:

```
{{Vault Name.Item Name.Field Name}}
{{Item Name.Field Name}}
{{Field Name}}
```

:warning: Warning: Using a period (.) in the template field names, item names, or vault names can lead to unexpected
behavior and failures during the processing of templates. Please avoid using periods within these names to ensure proper
functionality of the script.

### Mandatory and Optional Fields

When using the 1PassInject script, certain fields are mandatory, while others are optional. Here's a breakdown of what
is required and what happens if an optional field is omitted:

* Vault: Optional. If the vault name is not provided, the script will search for the item in all available vaults. If
  the vault name is provided in both the template and the 1passwordrc.yml file, the template vault takes precedence.
* Item Name: Mandatory for file type items. For template type items, the item name can be provided in the
  1passwordrc.yml file or embedded within the template itself using the format {{ItemName.FieldName}}. If the item name
  is not provided, the script will raise an error.
* Field Name: Mandatory. The field name must be specified within the template using the format {{ItemName.FieldName}} or
  {{VaultName.ItemName.FieldName}}. If the field name is not provided, the script will raise an error.
* Account: Optional. If the account is not provided, the script will use the default account configured for the op CLI
  tool. If you want to use a specific account, you can provide it in the 1passwordrc.yml file.

## Running the script

Navigate to the directory containing the 1passwordrc.yml file and the 1PassInject script, and run the script:

```bash
python 1PassInject.py
```

Or add it to your PATH.

## Contributing

Contributions are welcome! If you'd like to improve 1PassInject or report a bug, please open an issue or submit a pull
request on the GitHub repository.

## License

1PassInject is released under the MIT License. See the LICENSE file for more information.
