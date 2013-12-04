from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context
import os



class MailingHelper():

    def __init__(self, path):
        self.mail_template_dir_path = path

    def bind_template_with_content(self, template_name, directory, content_dict):
        template = loader.get_template(template_name, directory)
        result = template.render(Context(content_dict))
        return result

    def send_html_email(self, template_name, content_dict):
        html_mail = self.bind_template_with_content(template_name, os.path.join(self.path, 'html'), content_dict)
        txt_mail = self.bind_template_with_content(template_name, os.path.join(self.path, 'txt'), content_dict)
        return (html_mail, txt_mail)



if __name__ == '__main__':
    mh = MailingHelper('./mail_templates')
    print mh.send_html_email("info", {"title":"AAAA", "body":"BBB"})