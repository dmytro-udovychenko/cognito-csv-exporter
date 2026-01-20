import argparse
import boto3
import json
from colorama import Fore


def iter_map_rows(file_path):
    with open(file_path, 'r', encoding='utf-8') as file_obj:
        header = file_obj.readline()
        if not header:
            return
        for line in file_obj:
            line = line.strip('\n')
            if not line:
                continue
            yield line.split(',')


def get_user_by_email(client, user_pool_id, email_value):
    if not email_value:
        return None
    response = client.list_users(
        UserPoolId=user_pool_id,
        Filter='email = "{}"'.format(email_value)
    )
    users = response.get('Users', [])
    if not users:
        return None
    return users[0]


def get_attribute(user, attribute_name):
    for attr in user.get('Attributes', []):
        if attr.get('Name') == attribute_name:
            return attr.get('Value', '')
    return ''


def parse_identities(raw_identities):
    if not raw_identities:
        return []
    try:
        identities = json.loads(raw_identities)
        if isinstance(identities, dict):
            return [identities]
        if isinstance(identities, list):
            return identities
    except (TypeError, ValueError):
        return []
    return []


def is_already_linked(identities, provider_name, provider_user_id):
    for identity in identities:
        if identity.get('providerName') != provider_name:
            continue
        if identity.get('userId') == provider_user_id:
            return True
    return False


def link_provider(
    client,
    user_pool_id,
    destination_sub,
    provider_name,
    provider_user_id
):
    client.admin_link_provider_for_user(
        UserPoolId=user_pool_id,
        DestinationUser={
            'ProviderName': 'Cognito',
            'ProviderAttributeName': 'Cognito_Subject',
            'ProviderAttributeValue': destination_sub
        },
        SourceUser={
            'ProviderName': provider_name,
            'ProviderAttributeName': 'Cognito_Subject',
            'ProviderAttributeValue': provider_user_id
        }
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            'Link federated IdP users to Cognito users using '
            'a mapping CSV'
        )
    )
    parser.add_argument(
        '--user-pool-id',
        type=str,
        required=True,
        help='The user pool ID'
    )
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='The user pool region'
    )
    parser.add_argument(
        '--profile',
        type=str,
        default='',
        help='The aws profile'
    )
    parser.add_argument(
        '--map-file',
        type=str,
        required=True,
        help='Federated mapping CSV file'
    )
    parser.add_argument(
        '--conflicts-file',
        type=str,
        default='',
        help='Write conflicts CSV'
    )
    args = parser.parse_args()

    if args.profile:
        session = boto3.Session(profile_name=args.profile)
        client = session.client('cognito-idp', args.region)
    else:
        client = boto3.client('cognito-idp', args.region)

    linked = 0
    skipped = 0
    already_linked = 0
    conflicts = 0
    already_linked_error = "SourceUser is already linked to DestinationUser"
    merge_conflict_error = "Merging is not currently supported"

    conflicts_file = None
    if args.conflicts_file:
        conflicts_file = open(args.conflicts_file, 'w', encoding='utf-8')
        conflicts_file.write(
            'provider_name,provider_user_id,email,cognito_username\n'
        )

    for row in iter_map_rows(args.map_file):
        if len(row) < 4:
            skipped += 1
            continue

        cognito_username = row[0].strip()
        email = row[1].strip()
        provider_name = row[2].strip()
        provider_user_id = row[3].strip()

        if not provider_name or not provider_user_id:
            skipped += 1
            continue

        user = get_user_by_email(client, args.user_pool_id, email)
        if not user:
            print(Fore.YELLOW + "SKIP: user not found for email: {}".format(
                email
            ))
            skipped += 1
            continue

        destination_sub = get_attribute(user, 'sub')
        if not destination_sub:
            print(Fore.YELLOW + "SKIP: missing sub for email: {}".format(
                email
            ))
            skipped += 1
            continue

        identities = parse_identities(get_attribute(user, 'identities'))
        if is_already_linked(identities, provider_name, provider_user_id):
            print(Fore.CYAN + "INFO: already linked for email {} ({})".format(
                email, provider_name
            ))
            already_linked += 1
            continue

        try:
            link_provider(
                client,
                args.user_pool_id,
                destination_sub,
                provider_name,
                provider_user_id
            )
            linked += 1
        except client.exceptions.ClientError as err:
            error_message = err.response["Error"]["Message"]
            if already_linked_error in error_message:
                info_message = "INFO: already linked for email {} ({})".format(
                    email, provider_name
                )
                print(Fore.CYAN + info_message)
                already_linked += 1
                continue
            if merge_conflict_error in error_message:
                print(Fore.YELLOW + "CONFLICT: {} ({})".format(
                    email, provider_name
                ))
                conflicts += 1
                if conflicts_file:
                    conflicts_file.write("{},{},{},{}\n".format(
                        provider_name,
                        provider_user_id,
                        email,
                        cognito_username
                    ))
                continue
            print(Fore.RED + "ERROR: link failed for email {} ({}): {}".format(
                email, provider_name, error_message
            ))
            skipped += 1

    if conflicts_file:
        conflicts_file.close()

    done_message = (
        "DONE: linked={}, already_linked={}, "
        "conflicts={}, skipped={}".format(
            linked,
            already_linked,
            conflicts,
            skipped
        )
    )
    print(Fore.GREEN + done_message)


if __name__ == '__main__':
    main()
