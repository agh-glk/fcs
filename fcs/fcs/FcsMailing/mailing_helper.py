from django.core import mail
import os



class MailingHelper():

    def __init__(self, path):
        self.mail_template_dir_path = path

    def bind_html_template_with_content(self, template, content):
        try:
            html_template = open(os.path.join(self.mail_template_dir_path, template)).read()
        except IOError:
            raise
        html_template = html_template.format(*content)
        return html_template

if __name__ == '__main__':
    mh = MailingHelper('./templates')
    print os.path.abspath(os.path.curdir)
    print mh.bind_html_template_with_content('info.html',["AA","BB"])