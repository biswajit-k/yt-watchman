import datetime
import smtplib
from jinja2 import Template

from email.message import EmailMessage
from thread_safe_utils import run_in_thread
from youtube.env_details import env_details

"""
user mail components-, people - histories, this is sent to [email]

logo
starting line
<list of people>
    [this mail comes from(people)]
    <list of histories>
        (history image, video_title, channel_title, channel_logo, video_description)

[this mail is sent to (user email)]
closing line

*thumbnail_url, video_title, *channel_logo_url, channel_title, *video_description

 """

class EmailService:

    @classmethod
    def generate_owner_history(cls, username, history_list):
        history_template = """
        <table cellpadding="0" cellspacing="0" role="none">
            <tr>
            <td>
                <p style="display: inline-block; padding-top: 16px; padding-bottom: 16px">Videos from the mailing list of</p>
                <p style="display: inline-block; padding-left: 4px; font-weight: 600; color: #ef4444">{{ username }}</p>
                <p style="display: inline-block;">,</p>
            </td>
            </tr>
        {% for history in history_list %}
            <table style="margin-left: 16px; margin-right: 16px; margin-bottom: 24px; width: 100%" cellpadding="0" cellspacing="0" role="none">
                <tr>
                    <td style="height: 113px; width: 200px; padding-right: 24px; vertical-align: middle">
                    <img src="{{ history.thumbnail_url }}" alt="thumbnail" width="200" height="113" style="max-width: 100%; vertical-align: middle; line-height: 1; height: 113px; width: 200px;">
                    </td>
                    <td>
                    <table cellpadding="0" cellspacing="0" role="none">
                        <tr>
                        <td>
                            <a class="hover-text-red-500" href="{{ history.video_link }}" style="color: #1e293b; text-decoration: none">
                            {{ history.video_title }}
                            </a>
                        </td>
                        </tr>
                        <tr>
                        <td>
                            <p style="margin: 8px 0 0; font-size: 12px">{{ history.channel_title }}</p>
                        </td>
                        </tr>
                        <tr>
                        <td>
                            <p style="margin: 8px 0 0; font-size: 12px;">
                            {{ history.video_description[:50] }}...
                            </p>
                        </td>
                        </tr>
                        <tr>
                        <td style="margin: 8px 0 0; display: inline-block; border-radius: 2px; background-color: #e5e7eb; padding: 0.1rem 4px; font-size: 0.64rem; font-weight: 600">
                            {{ history.tag }}
                        </td>
                        </tr>
                    </table>
                    </td>
                </tr>
            </table>
            {% if loop.index0 < history_list|length - 1 %}
                <tr>
                    <td>
                        <p style="margin: 0 0 12px; height: 1px; background-color: #e2e8f0"></p>
                    </td>
                </tr>
            {% endif %}
        {% endfor %}
        </div>
        """

        template = Template(history_template)
        data = {
            'history_list': history_list,
            'username': username,
        }
        return template.render(data)


    @classmethod
    def generate_history_html_body(cls, recipient_email, mailinglist_owners):
        body_template = """
        <html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
            <head>
            <meta charset="utf-8">
            <meta name="x-apple-disable-message-reformatting">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
            <meta name="color-scheme" content="light dark">
            <meta name="supported-color-schemes" content="light dark">
            <!--[if mso]>
            <noscript>
                <xml>
                <o:OfficeDocumentSettings xmlns:o="urn:schemas-microsoft-com:office:office">
                    <o:PixelsPerInch>96</o:PixelsPerInch>
                </o:OfficeDocumentSettings>
                </xml>
            </noscript>
            <style>
                td,th,div,p,a,h1,h2,h3,h4,h5,h6 {font-family: "Segoe UI", sans-serif; mso-line-height-rule: exactly;}
            </style>
            <![endif]-->
            <style>
                .hover-text-red-500:hover {
                color: #ef4444 !important
                }
                .hover-important-text-decoration-underline:hover {
                text-decoration: underline !important
                }
            </style>
            </head>
            <body style="margin: 0; width: 100%; padding: 0; -webkit-font-smoothing: antialiased; word-break: break-word">
            <div role="article" aria-roledescription="email" aria-label lang="en">
                <div style="background-color: #e2e8f0; padding-top: 80px; padding-bottom: 80px; font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; font-size: 16px">
                <table align="center" cellpadding="0" cellspacing="0" role="none">
                    <tr style="background-color: #fff">
                        <td style="margin: 40px 0 0; width: 600px; max-width: 100%; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 40px 40px 0">
                            <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
                                <tr>
                                    <td>
                                        <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
                                            <tr>
                                                <td></td>
                                                <td align="end">
                                                    <img src="https://i.ibb.co/vY4qZn2/logo.jpg" alt="logo" width="300" style="max-width: 100%; vertical-align: middle; line-height: 1; width: 300px">
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 16px">
                                                    We have found videos that match your recommendation.
                                                </td>
                                            </tr>
                                            {% for username, history_list in mailinglist_owners.items() %}
                                                {{ generate_owner_history(username, history_list) }}
                                            {% endfor %}
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="width: 680px; background-color: #fff">
                                        <table align="center" style="width: 680px; background-color: #fff;" cellpadding="0" cellspacing="0" role="none">
                                            <tr>
                                                <td align="center">
                                                    <p style="margin: 32px 0 0; font-size: 14px">
                                                    This mail was sent to
                                                    <a class="hover-important-text-decoration-underline" href="mailto:{{ recipient_email }}" style="color: #2563eb; text-decoration: none">{{ recipient_email }}</a>
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="center" style="font-size: 14px;">
                                                    <a class="hover-important-text-decoration-underline" href style="color: #2563eb; text-decoration: none;">Privacy Policy</a> |
                                                    <a class="hover-important-text-decoration-underline" href style="color: #2563eb; text-decoration: none;">Manage Settings</a> |
                                                    <a class="hover-important-text-decoration-underline" href style="color: #2563eb; text-decoration: none;">Unsubscribe</a>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td align="center" style="font-size: 14px;">
                                                    <p style="margin-top: 40px; padding-left: 40px; padding-right: 40px; padding-bottom: 32px">
                                                    Copyright &copy; 2008-2024, YT-Watchman LLC. "YT-Watchman" and logo are
                                                    registered trademarks of YT-Watchman LLC.
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </body>
</html>

        """
        template = Template(body_template)
        data = {
            'generate_owner_history': cls.generate_owner_history,
            'recipient_email': recipient_email,
            'mailinglist_owners': mailinglist_owners,
        }
        return template.render(data)

    @classmethod
    def generate_comment_html_body(cls, user_email, history):
        body_template = """
        <!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml">
<head>
  <meta charset="utf-8">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="format-detection" content="telephone=no, date=no, address=no, email=no, url=no">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <!--[if mso]>
  <noscript>
    <xml>
      <o:OfficeDocumentSettings xmlns:o="urn:schemas-microsoft-com:office:office">
        <o:PixelsPerInch>96</o:PixelsPerInch>
      </o:OfficeDocumentSettings>
    </xml>
  </noscript>
  <style>
    td,th,div,p,a,h1,h2,h3,h4,h5,h6 {font-family: "Segoe UI", sans-serif; mso-line-height-rule: exactly;}
  </style>
  <![endif]-->
  <style>
    .hover-important-text-decoration-underline:hover {
      text-decoration: underline !important
    }
  </style>
</head>
<body style="margin: 0; width: 100%; padding: 0; -webkit-font-smoothing: antialiased; word-break: break-word">
  <div role="article" aria-roledescription="email" aria-label lang="en">
    <div style="background-color: #e2e8f0; padding-top: 80px; padding-bottom: 80px; font-family: ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; font-size: 16px">
      <table align="center" cellpadding="0" cellspacing="0" role="none">
        <tr style="background-color: #fff">
          <td style="margin: 40px 0 0; width: 600px; max-width: 100%; border-top-left-radius: 8px; border-top-right-radius: 8px; padding: 40px 40px 0">
            <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td></td>
                <td align="end">
                  <img src="https://i.ibb.co/vY4qZn2/logo.jpg" alt="logo" style="max-width: 100%; vertical-align: middle; line-height: 1; width: 200px">
                </td>
              </tr>
            </table>
            <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td>
                  <p style="margin: 48px 0 8px">Hi Subscriber,</p>
                  <p style="margin: 0; display: inline-block">Comment made on your behalf on the video </p>
                  <span style="margin: 0; font-weight: 600; color: #ef4444">{{ history.video_title }}</span>
                  <p style="margin-top: 8px">The details are below-</p>
                </td>
              </tr>
            </table>
            <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td align="center" style="margin: 48px 0">
                  <div style="margin-right: 16px; display: inline-block; height: 64px; width: 64px; border-radius: 9999px; background-color: #dc2626; text-align: center; font-size: 30px; font-weight: 600; color: #fff">
                    <span style="vertical-align: middle">{{ user_email[0] }}</span>
                  </div>
                  <div style="margin: 0 16px 0 0; display: inline-block; font-size: 14px; color: #000">
                    you commented:
                    <span style="font-size: 16px; font-style: italic">"{{history.comment[:20]}}..."</span>
                    <p style="text-align: left; font-size: .84rem; color: #6b7280">In
                      <span style="font-weight: 600;">{{(current_time - history.found_at).total_seconds()}}  seconds</span>
                    </p>
                  </div>
                  <img src="{{ history.thumbnail_url }}" alt="video" style="max-width: 100%; vertical-align: middle; line-height: 1; height: 96px">
                  <p style="margin: 32px 0; padding-right: 96px; text-align: right">
                    <a href="{{ history.comment_link }}" class="hover-important-text-decoration-underline" style="font-size: 0.96rem; font-weight: 600; color: #ef4444; text-decoration: none">
                      SHOW COMMENT
                    </a>
                  </p>
                </td>
              </tr>
            </table>
            <table style="width: 100%;" cellpadding="0" cellspacing="0" role="none">
              <tr>
                <td>
                  <p>Sit back, relax and let the watchman work for you,</p>
                  <p style="font-style: italic;">YT Watchman</p>
                </td>
              </tr>
              <tr>
                <td>
                  <p style="margin: 20px 0 0; height: 1px; background-color: #e2e8f0; padding: 0"></p>
                </td>
              </tr>
              <tr>
                <td>
                  <p style="margin-bottom: 4px; text-align: center">
                    This mail was sent to
                    <a class="hover-important-text-decoration-underline" " href=" mailto:{{ user_email }}" style="color: #2563eb; text-decoration: none">{{ user_email }}</a>
                  </p>
                  <p style="margin: 0; text-align: center; font-size: 14px;">
                    <a class="hover-important-text-decoration-underline" " href style=" color: #2563eb; text-decoration: none;">Privacy Policy</a> |
                    <a class="hover-important-text-decoration-underline" " href style=" color: #2563eb; text-decoration: none;">Manage Settings</a> |
                    <a class="hover-important-text-decoration-underline" " href style=" color: #2563eb; text-decoration: none;">Unsubscribe</a>
                  </p>
                  <p style="margin: 40px 0 0; padding: 0 40px 40px; text-align: center; font-size: 14px">
                    Copyright &copy; 2008-2024, YT-Watchman LLC. "YT-Watchman" and logo are
                    registered trademarks of YT-Watchman LLC.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
  </div>
</body>
</html>
        """
        template = Template(body_template)
        data = {
            'history': history,
            'current_time': datetime.datetime.now(datetime.UTC),
            'user_email': user_email,
        }
        return template.render(data)

    @classmethod
    def send_history_mail(cls, recipient_history):
        for recipient_email, mailinglist_owners in recipient_history.items():
            subject = "Youtube Watchman | Video detected!"
            html_body = cls.generate_history_html_body(recipient_email, mailinglist_owners)
            cls.send_mail(recipient_email, subject, html_body)
            print(f"{recipient_email} done!")

    @classmethod
    def send_comment_mail(cls, email, history):
        subject = "Youtube Watchman | Comment made on video sucessfully!"
        html_body = cls.generate_comment_html_body(email, history)
        print("starting mail send function")
        cls.send_mail(email, subject, html_body)

    @classmethod
    @run_in_thread
    def send_mail(cls, to, subject, content):

        SENDER_MAIL = env_details['SENDER_EMAIL']
        SENDER_PASS = env_details['SENDER_PASS']
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_MAIL
        msg['To'] = to
        msg.set_content(content, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(SENDER_MAIL, SENDER_PASS)
            smtp.send_message(msg)

        print("mail sent!")
