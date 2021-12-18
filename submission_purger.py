from requests.exceptions import InvalidHeader
from prawcore.exceptions import NotFound, OAuthException, RequestException, ResponseException
import yaml
import praw


# Class used to print colored text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# This function writes all the default configurations if they are not found in the config.yml file.
def write_default_configurations() -> None:
    # Checking if the file has all the configuration sections in it
    try:
        config = yaml.safe_load(open('config.yml', 'r'))
        if len(config['app-settings']) != 0 and len(config['credential-settings']) != 0:
            return
    except:
        # The file isn't created.
        print(
            f'{bcolors.WARNING}Configuration file not found. Creating one with default configurations.{bcolors.ENDC}')

    # The config is missing configurations, rewrite them
    file = open('config.yml', 'w')
    default_app_settings = {
        'app-settings': {
            'client-id': '',
            'client-secret': '',
            'user-agent': ''
        }
    }
    default_credential_settings = {
        'credential-settings': {
            'username': '',
            'password': ''
        }
    }
    default_target_settings = {'target-user': ''}
    yaml.dump(default_app_settings, file, sort_keys=False)
    yaml.dump(default_credential_settings, file, sort_keys=False)
    yaml.dump(default_target_settings, file, sort_keys=False)
    file.close()


def main() -> None:
    # Getting the script configurations and connecting to the Reddit App
    config = yaml.safe_load(open('config.yml', 'r'))
    app_settings = config['app-settings']
    credential_settings = config['credential-settings']
    reddit = praw.Reddit(client_id=app_settings['client-id'],
                         client_secret=app_settings['client-secret'],
                         user_agent=app_settings['user-agent'],
                         username=credential_settings['username'],
                         password=credential_settings['password'])
    try:
        # Checking if the app only has read permissions
        if reddit.read_only:
            print(
                f"{bcolors.FAIL}[ERROR] The script is currently running in read-only mode. Be sure to set the credential-settings in the config.yml file.{bcolors.ENDC}")
            return

        # Getting the upvote filter
        while True:
            upvote_filter = 0
            upvote_filter_input = input(
                "Delete posts that have less that the next amount of upvotes: ")
            if (not upvote_filter_input.isdigit()):
                print(
                    f"{bcolors.FAIL}The amount of upvotes must be a numeric value.{bcolors.ENDC}")
                continue

            upvote_filter = int(upvote_filter_input)
            break

        # Printing runtime information
        redittor = reddit.redditor(config['target-user'])
        print(f"{bcolors.OKBLUE}Running script for user: {redittor.name}{bcolors.ENDC}")
        # Iterating through all the redittor's post
        delete_count = 0
        for submission in redittor.submissions.new(limit=1000):
            submission_score = submission.score
            # Checking if the amount of upvotes is higher than the inputted filter
            if (submission_score > upvote_filter):
                continue

            # Deleting the submission since it doesn't have enough upvotes
            submission.delete()
            print(
                f"{bcolors.OKCYAN}Successfully deleted post '{submission.title}' with {submission_score} upvotes found in '{submission.subreddit.title}'.{bcolors.ENDC}")
            delete_count += 1

    except (InvalidHeader, ValueError):
        # User didn't provide a target-user.
        print(
            f"{bcolors.FAIL}[ERROR] Please make sure your 'target-user' is correctly set in the config.yml file.{bcolors.ENDC}")
        return
    except NotFound:
        # User didn't provide a valid target-user.
        print(f"{bcolors.FAIL}[ERROR] Target user not found.")
        return
    except (RequestException, ResponseException):
        # User didn't provide valid app settings.
        print(
            f"{bcolors.FAIL}[ERROR] Please make sure your 'app-settings' are correctly set in the config.yml file.{bcolors.ENDC}")
        return
    except OAuthException:
        print(
            f"{bcolors.FAIL}[ERROR] Check the configured credential-settings in the config.yml file.{bcolors.ENDC}")
        return

    print(f"{bcolors.OKGREEN}Execution completed. Deleted {delete_count} submissions.{bcolors.ENDC}")


if __name__ == '__main__':
    write_default_configurations()
    main()
