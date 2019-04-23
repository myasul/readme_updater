#!/usr/bin/env python3
"""GITHUB UPDATER

Creating the description for this script is included in my TODO list.
"""

import requests
import base64
import json
import traceback
import argparse
from argparse import RawTextHelpFormatter
from configparser import ConfigParser, NoSectionError, NoOptionError
from subprocess import call
from grip import export

# TODO :: Handle all the following scenarios
# 1. Invalid repository
# 2. Invalid username
# 3. Invalid sha and path

# CONSTANTS
GITHUB_SECTION = 'GITHUB'
API_URL = 'https://api.github.com'
ACCEPT = 'application/vnd.github.v3+json'


class ReadMeUpdater:
    def __init__(self, config, repository):
        self._config = config
        self._repository = repository

    def pull_latest_readme(self):
        headers = self._get_authorization_headers()
        github_readme_url = ('{api_url}/repos/{username}/' +
                             '{repository}/readme').format(
            api_url=API_URL,
            username=self._get_config('username'),
            repository=self._repository)

        resp = requests.get(github_readme_url, headers=headers)
        resp_dict = resp.json()

        # Always update SHA and path of the README file
        self._update_config(
            'readme_sha', resp_dict.get('sha'))

        self._update_config(
            'readme_path', resp_dict.get('path'))

        if resp_dict.get('content'):
            readme = base64.b64decode(resp_dict.get('content'))
            with open(self._build_filename('md'), 'w+', encoding='utf-8') as md:
                md.write(readme.decode())

    def push_updated_readme(self):
        # TODO :: Add a way to authenticate user

        if not self._config.get('GITHUB', 'readme_sha'):
            # TODO :: Add SHA validation
            pass

        try:
            with open(self._build_filename('md'), "r") as readme_file:

                content = readme_file.read()

                if isinstance(content, str):
                    content = content.encode()

                content = base64.b64encode(content).decode()

                headers = self._get_authorization_headers()

                params = {
                    'message': 'Update README.md',
                    'content': content,
                    'sha': self._config.get('GITHUB', 'readme_sha'),
                    'branch': 'master',
                    'committer': {
                        'name': 'Matthew Yasul',
                        'email': 'yasulmatthew@gmail.com'
                    },
                    'author': {
                        'name': 'Matthew Yasul',
                        'email': 'yasulmatthew@gmail.com'
                    },
                }

                path = self._get_config('readme_path')

                github_update_url = ('{api_url}/repos/{username}/' +
                                     '{repository}/contents/{path}').format(
                    api_url=API_URL,
                    username=self._get_config('username'),
                    repository=self._repository,
                    path=path)

                resp = requests.put(github_update_url,
                                    data=json.dumps(params), headers=headers)

                if resp.status_code != 200:
                    # TODO :: Add validation
                    return

                resp_json = resp.json()
                self._update_config(
                    'readme_sha', resp_json.get('content').get('sha'))

        except IOError:
            print("ERROR!")
            traceback.print_exc()
            # TODO :: Add error handling
            pass

    def generate_preview(self):
        self._generate_html()
        self._generate_pdf()

    def _generate_html(self):
        # TODO :: Add File Error Handling
        export(path=self._build_filename('md'),
               out_filename=self._build_filename('html'))

    def _generate_pdf(self):
        # TODO :: Add in README.md to install wkthmtopdf
        call([
            'wkhtmltopdf',
            '-q',
            '--title', self._build_filename('md'),
            self._build_filename('html'),
            self._build_filename('pdf')
        ])

    def _build_filename(self, file_type):
        identier = "{}_{}".format(
            self._get_config('username'),
            self._repository
        )

        if file_type == 'md':
            return '{}_README.md'.format(identier)
        elif file_type == 'html':
            return '{}_README_preview.html'.format(identier)
        elif file_type == "pdf":
            return '{}_README_preview.pdf'.format(identier)
        else:
            # TODO Add invalid file typ error
            return ""

    def _update_config(self, option, value):
        try:
            self._config.set(GITHUB_SECTION, option, value)
        except (NoSectionError, NoOptionError) as e:
            # TODO :: Add more logic
            pass
        else:
            with open('config.ini', 'w') as configfile:
                self._config.write(configfile)

    def _get_config(self, option):
        try:
            return self._config.get(GITHUB_SECTION, option)
        except (NoSectionError, NoOptionError) as e:
            # TODO :: Add more logic
            pass

    def _get_authorization_headers(self):
        return {
            'Accept': ACCEPT,
            'Authorization': "token " + self._get_config('access_token'),
            'User-Agent': self._get_config('username')
        }


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter
    )

    repository_help = 'The name of the repository where the README.md is located.'
    parser.add_argument(
        'repository',
        type=str,
        default='',
        help=repository_help
    )

    action_help = 'Actions that the script can perform. Specifying "pull"'\
                ' would extract the README.md file from the specified'\
                ' repository on GitHub. Specifying "push" would push the'\
                ' local README.md file to GitHub if there are any changes.'\
                ' Specifying "preview" would generate an html and pdf file' \
                ' from the README.md so that the user can have an idea of' \
                ' what it will look like in GitHub.'
    parser.add_argument(
        'action',
        type=str,
        default='pull',
        choices=['push', 'pull', 'preview'],
        help=action_help
    )

    args = parser.parse_args()

    config = ConfigParser()
    config.read('config.ini')
    readme = ReadMeUpdater(config, args.repository)

    if args.action == 'pull':
        readme.pull_latest_readme()
        readme.generate_preview()
    elif args.action == 'push':
        readme.push_updated_readme()
        readme.generate_preview()
    elif args.action == 'preview':
        readme.generate_preview()

if __name__ == '__main__':
    main()
