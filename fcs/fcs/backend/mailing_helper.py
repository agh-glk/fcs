from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template
import os



class MailingHelper():

    def __init__(self, path):
        self.mail_template_dir_path = path

    @staticmethod
    def _bind_template_with_content(template_path, content_dict):
        with open(template_path) as _template_file:
            _template = Template(_template_file.read())
        result = _template.render(Context(content_dict))
        return result

    def send_html_email(self, subject, template_name, content_dict, sender, receivers):
        _path = os.path.join(self.mail_template_dir_path, 'html', template_name+'.html')
        _html_mail = self._bind_template_with_content(_path, content_dict)
        _path = os.path.join(self.mail_template_dir_path, 'txt', template_name+'.txt')
        _txt_mail = self._bind_template_with_content(_path, content_dict)
        _message = EmailMultiAlternatives(subject, _txt_mail, sender, receivers)
        _message.attach_alternative(_html_mail, "text/html")
        _message.send()


if __name__ == '__main__':
    mh = MailingHelper('./manager/backend/mail_templates')
    print mh.send_html_email("info", {"title":"AAAA", "body":"BBB"})