import json
import os
import re
import subprocess

import yaml

# ANSI escape codes for colors and formatting
BLUE = "\033[34m"
GREEN = "\033[32m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"


def get_1password_value(account, vault, item, field):
    """
    Retrieves the value of a specified field from a 1Password item.

    :param account: The 1Password account to use, optional.
    :param vault: The vault containing the item, optional.
    :param item: The name or UUID of the item, mandatory.
    :param field: The field to retrieve the value from, mandatory.
    :return: The value of the specified field or None if not found or an error occurred.
    """
    try:
        if not item:
            print(f"{RED}Item name or UUID is missing ", end="")
            return None
        cmd = ["op", "item", "get", item, "--format", "json"]
        if vault:
            cmd.extend(["--vault", vault])
        if account:
            cmd.extend(["--account", account])
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        item_data = json.loads(result.stdout)
        value = None

        for field_data in item_data.get("fields", []):
            if field_data.get("label") == field:
                value = field_data.get("value")
                break

        if not value:
            print(f"{RED}Field '{field}' not found in item '{item}'{RESET} ", end="")

        return value
    except subprocess.CalledProcessError as e:
        print(f"{RED}Failed to get 1Password item: {e.stderr.strip()}{RESET} ", end="")
        return None
    except json.JSONDecodeError as e:
        print(f"{RED}Fail to decode item: {e}{RESET} ", end="")
        return None


def get_1password_file(account, vault, item):
    """
    Retrieves a file stored as a 1Password document.

    :param account: The 1Password account to use, optional.
    :param vault: The vault containing the document, optional.
    :param item: The name or UUID of the document, mandatory.
    :return: The file content as bytes or None if an error occurred.
    """
    cmd = ["op", "document", "get", item]
    if vault:
        cmd.extend(["--vault", vault])
    if account:
        cmd.extend(["--account", account])

    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8").strip()
        print(f"{RED}{error_message}{RESET} ", end="")
        return None


def process_file(account, vault, item, destination):
    """
    Retrieves a file from 1Password and saves it to the specified destination.

    :param account: The 1Password account to use, optional.
    :param vault: The vault containing the item, optional.
    :param item: The name or UUID of the item, mandatory.
    :param destination: The path to save the file to, mandatory.
    :return: True if the file was successfully saved, False otherwise.
    """
    try:
        file_content = get_1password_file(account, vault, item)

        if not file_content:
            return False

        with open(destination, 'wb') as output_file:
            output_file.write(file_content)

        return True
    except Exception as e:
        print(f"{RED}An exception occurred while processing the file for item '{item}': {e}{RESET}", end="")
        return False


def process_template(account, vault, item_name, template_path, destination):
    """
    Processes a template file, replacing placeholders with values from 1Password items.

    :param account: The 1Password account to use, optional.
    :param vault: The vault containing the item, optional.
    :param item_name: The name or UUID of the item, mandatory.
    :param template_path: The path to the template file, mandatory.
    :param destination: The path to save the processed file to, mandatory.
    :return: True if the template was successfully processed, False otherwise.
    """
    try:
        with open(template_path, 'r') as template_file:
            content = template_file.readlines()

        pattern = re.compile(r"\{\{(?:(?:(.+?)\.)?(.+?)\.)?(.+?)}}")
        success = True
        for line_number, line in enumerate(content):
            for match in re.finditer(pattern, line):
                full_vault, template_item, field = match.groups()

                if not full_vault:
                    full_vault = vault

                if not template_item:
                    template_item = item_name

                print(
                    f"\tLine: {BOLD}{line_number + 1}{RESET} -> Account: {BOLD}{account}{RESET}, Vault: {BOLD}{full_vault}{RESET}, Item: {BOLD}{template_item}{RESET}, Field: {BOLD}{field}{RESET} ... ",
                    end="")
                value = get_1password_value(account, full_vault, template_item, field)
                if value is not None:
                    content[line_number] = content[line_number].replace(match.group(), value)
                    print(f"{GREEN}Done{RESET}")
                else:
                    success = False
                    print(f"- {RED}Error{RESET}")

        if success:
            with open(destination, 'w') as output_file:
                output_file.writelines(content)

        return success
    except Exception as e:
        print(f"\t{RED}Error: An exception occurred while processing the template: {e}{RESET}")
        return False


def process_1passwordrc_file(file_path):
    """
    Processes a 1passwordrc configuration file to retrieve and process files and templates.

    :param file_path: The path to the 1passwordrc.yml file.
    """
    with open(file_path, "r") as stream:
        config = yaml.safe_load(stream)

    for item in config["items"]:
        account = item.get("account", None)
        vault = item.get("vault", None)
        item_key = item["name"]
        item_name = item.get("item", None)
        destination = item["destination"]

        if item["type"] == "file":
            print(f"Processing {BLUE}{item_key}{RESET} ... {RESET}", end="")
            if process_file(account, vault, item_name, destination):
                print(f"{GREEN}Done{RESET}")
            else:
                print(f"- {RED}Error{RESET}")
        elif item["type"] == "template":
            template_path = item["source"]
            print(f"{BOLD}{BLUE}Processing {BLUE}{item_key}{RESET} ({BLUE}{template_path}{RESET}) ... {RESET}")
            process_template(account, vault, item_name, template_path, destination)


def main():
    current_directory = os.path.abspath(".")
    config_file = os.path.join(current_directory, "1passwordrc.yml")
    if os.path.exists(config_file):
        print(f"{BOLD}{BLUE}1passwordrc file: {config_file}{RESET}")
        process_1passwordrc_file(config_file)
    else:
        print(f"{RED}Error: No 1passwordrc.yml file found in the current directory.{RESET}")


if __name__ == "__main__":
    main()
