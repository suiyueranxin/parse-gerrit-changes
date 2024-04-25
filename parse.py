from requests.auth import HTTPBasicAuth
from pygerrit2.rest import GerritRestAPI
from jira import JIRA
import re
import csv
import sys
import urllib3
import requests


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
gerrit_rest = None
jira_rest = None


def init_rest_src(usr, pwd):
    global gerrit_rest
    gerrit_auth = generate_auth_for_gerrit(usr, pwd)
    gerrit_rest = GerritRestAPI(url='https://git.wdf.sap.corp', auth=gerrit_auth, verify=False)

    global jira_rest
    jira_auth = generate_auth_for_jira(usr, pwd)
    jira_rest = JIRA(server='https://sapjira.wdf.sap.corp', basic_auth=jira_auth, options={'verify': False})


# parse gerrit items to json
def parse_gerrit_records_to_json(gerrit_query):
    dic = {}
    try:
        changes = gerrit_rest.get('/changes/?O=81&S=0&q='+gerrit_query)
        for change in changes:
            dic[change['_number']] = {
                'number': change['_number'],
                'subject': change['subject'],
                'change_id': change['change_id']
            }
            print_process()
    except requests.exceptions.HTTPError as err:
        print('Fail! User name or password is incorrect.')
    return dic


def get_issue_id_by_git_number(git_number):
    change = gerrit_rest.get('/changes/orca_cloud~{number}/detail?O=556714'.format(number=git_number))
    revision = change['current_revision']
    message = change['revisions'][revision]['commit']['message']
    issue_id = re.search('FPA[0-9]+-[0-9]+', message).group(0)
    return issue_id


def get_project_by_issue_id(issue_id):
    issue = jira_rest.issue(issue_id, fields='project')
    return (issue.fields.project.key, issue.fields.project.name)


def parse_to_list(gerrit_query):
    result = []
    print('parse gerrit records')
    gerrit_json = parse_gerrit_records_to_json(gerrit_query)
    print('\nparse jira')
    for number in gerrit_json:
        issue_id = get_issue_id_by_git_number(number)
        project = get_project_by_issue_id(issue_id)
        result.append({
            'number': number,
            'subject': gerrit_json[number]['subject'],
            'issue_id': issue_id,
            'project_id': project[0],
            'project_name': project[1]
        })
        print_process()
    return result


def write_list_to_csv(list_obj, csv_path):
    with open(csv_path, 'w', encoding='utf-8', newline='') as f_csv:
        csv_writer = csv.writer(f_csv)
        has_header = False
        for item in list_obj:
            if not has_header:
                csv_writer.writerow(item.keys())
                has_header = True
            csv_writer.writerow(item.values())
            print_process()


def parse(csv_path, gerrit_query, usr, pwd):
    init_rest_src(usr, pwd)

    print('Start to parse')
    result = parse_to_list(gerrit_query)
    print('\nFinish. Total is ' + str(len(result)))

    print('\nStart to write csv')
    write_list_to_csv(result, csv_path)
    print('\nSuccess!')


def generate_auth_for_gerrit(usr, pwd):
    return HTTPBasicAuth(usr.lower(), pwd)


def generate_auth_for_jira(usr, pwd):
    return (usr.upper(), pwd)


def print_process():
    sys.stdout.write(".")
    sys.stdout.flush()


def main():
    # sys.args: query, inumber, ipwd
    if len(sys.argv) == 4:
        parse('./gerrit_to_project.csv', sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        parse(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print('Fail! Please input parameters: %query% %usr% %pwd%')

# debug data
# query = 'project%3Aorca_cloud%20branch%3Arel-1.0-2020.02%20status%3Amerged%20after%3A2020-03-16'
# git_number = '4631204'
# issue_id = 'FPA33-8366'
# parse_gerrit_records_to_json(query);
# get_issue_id_by_git_number(git_number)
# get_project_by_issue_id(issue_id)
# parse(query, './gerrit_to_project.csv', 'I068096', '010101Lx')

main()
