#!/usr/bin/env python3
import requests
import base64
from configparser import ConfigParser, NoSectionError
from subprocess import call
from grip import export


class ReadMeUpdater:
    def __init__(self, config):
        self._config = config
        self._username = config.get('GITHUB', 'USERNAME')
        self._repository = config.get('GITHUB', 'REPOSITORY')
        self._api_url = config.get('GITHUB', 'API_URL')
        self._accept = config.get('GITHUB', 'ACCEPT')

    def pull_latest_readme(self):
        headers = {'Accept': self._accept}
        github_readme_url = ("{api_url}/repos/{username}/" +
                             "{repository}/readme").format(
            api_url=self._api_url,
            username=self._username,
            repository=self._repository)

        resp = requests.get(github_readme_url, headers=headers)
        resp_dict = resp.json()

        if resp_dict.get('content'):
            readme = base64.b64decode(resp_dict.get('content'))
            filename = "{}_{}_README.md".format(
                self._username,
                self._repository
            )
            with open(filename, "w+", encoding="utf-8") as md:
                md.write(readme.decode())

    def push_updated_readme(self):
        pass

    def generate_preview(self):
        readme_filename = "{}_{}_README.md".format(
            self._username,
            self._repository
        )

        preview_filename = "{}_{}_README_preview.pdf".format(
            self._username,
            self._repository
        )

        html_filename = "{}_{}_README_preview.html".format(
            self._username,
            self._repository
        )
        self._generate_html(readme_filename, html_filename)
        self._generate_pdf(preview_filename, html_filename, readme_filename)

    def _generate_html(self, readme_filename, html_filename):
        # TODO :: Add File Error Handling
        export(path=readme_filename, out_filename=html_filename)

    def _generate_pdf(self, preview_filename, html_filename, readme_filename):
        # TODO :: Add in README.md to install wkthmtopdf
        call([
            "wkhtmltopdf",
            "-q",
            "--title", readme_filename,
            html_filename,
            preview_filename
        ])

    def update_config_file(self, section, option, value):
        try:
            with open("config.ini", "w") as configfile:
                self._config.write(configfile)
        except NoSectionError:
            # TODO :: Add more logic
            pass


def main():
    config = ConfigParser()
    config.read('config.ini')
    readme = ReadMeUpdater(config)
    readme.pull_latest_readme()
    readme.generate_preview()


if __name__ == "__main__":
    main()
