import argparse
import os
import re

import conf_diff
import psycopg2


def get_config(hostname=None, date=None):
    """
    Retrieves the configuration backup for a given hostname and date from a PostgreSQL database.

    Args:
        hostname (str): The hostname of the firewall device to retrieve the config backup for.
        date (str): The date of the config backup to retrieve in the format "YYYY-MM-DD".

    Returns:
        list: A list of tuples containing the configuration backup as a string. Each tuple represents a row from the
            "backups" table in the database that matches the specified hostname and date.
    """
    try:
        conn = psycopg2.connect(
            database="py3tftpsql",
            user="your_username",
            password="your_password",
            host="your_host",
            port=55362,
        )
    except psycopg2.Error as e:
        print("Database error:", e)
    cur = conn.cursor()
    cur.execute(
        f"SELECT config FROM backups WHERE hostname = '{hostname}' AND created_at::date = '{date}'::date;"
    )
    rows = cur.fetchall()
    return rows


def main(hostname, date1, date2):
    """
    Retrieves the configuration backups for a given hostname and two dates, extracts the config strings,
    removes sensitive information such as passwords and private keys, and compares the differences
    between the two configs. The resulting diff is printed to the console.

    Args:
        hostname (str): The hostname of the firewall device to retrieve the config backups from.
        date1 (str): The date of the first config backup to retrieve in the format "YYYY-MM-DD".
        date2 (str): The date of the second config backup to retrieve in the format "YYYY-MM-DD".
    """
    config_strings = []
    for date in [date1, date2]:
        config_data = get_config(hostname=hostname, date=date)
        config_string = config_data[0][0].replace("\\n", "\n")
        config_string = "\n".join(line.strip() for line in config_string.split("\n"))

        pattern1 = r"(?!set\s+ppk-secret\b\s+ENC\s+\S+).*$|set\s+(?:auth|proxy)-password-l\d*\s+ENC\s+\S+|set\s+certificate\s+\"-----BEGIN CERTIFICATE-----\n(?:.|\n)*?-----END CERTIFICATE-----\"|-----BEGIN (?:ENCRYPTED|OPENSSH) PRIVATE KEY-----(?:.|\n)*?-----END (?:ENCRYPTED|OPENSSH) PRIVATE KEY-----|\s*set\s+(?:private-key|ppk-secret)\s+\"-----BEGIN (?:RSA|OPENSSH) PRIVATE KEY-----\n(?:.|\n)*?-----END (?:RSA|OPENSSH) PRIVATE KEY-----\"|set\s+(?:password|proxy-password|store-passphrase)\s+ENC\s+\S+"
        pattern2 = r"^.*set\s+ppk-secret\s+ENC\s+\S+.*$"

        config_string = re.sub(pattern1, "", config_string)
        config_string = re.sub(pattern2, "", config_string, flags=re.MULTILINE)

        config_string = "\n".join(
            [line for line in config_string.split("\n") if line.strip()]
        )
        config_strings.append(config_string)

    with open(f"{hostname}-{date1}.txt", "w") as file1, open(
        f"{hostname}-{date2}.txt", "w"
    ) as file2:
        file1.write(config_strings[0])
        file2.write(config_strings[1])

    config_change = conf_diff.ConfDiff(
        f"{hostname}-{date1}.txt", f"{hostname}-{date2}.txt"
    )
    config_diff = config_change.diff()
    if config_diff is not None:
        print(config_diff)

    os.remove(f"{hostname}-{date1}.txt")
    os.remove(f"{hostname}-{date2}.txt")


if __name__ == "__main__":
    """
    Parses command-line arguments using argparse and calls the main() function to retrieve the two config backups,
    compare the differences, and print the results to the console.

    Command-line arguments:
        --hostname (str): The hostname of the firewall device to retrieve the config backups for.
        --date1 (str): The date of the first config backup to retrieve in the format "YYYY-MM-DD".
        --date2 (str): The date of the second config backup to retrieve in the format "YYYY-MM-DD".
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname", required=True, help="firewall hostname")
    parser.add_argument("--date1", required=True, help="first backup date (YYYY-MM-DD)")
    parser.add_argument(
        "--date2", required=True, help="second backup date (YYYY-MM-DD)"
    )
    args = parser.parse_args()

    main(args.hostname, args.date1, args.date2)
