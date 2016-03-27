from account.celerytasks import send_forgot_password_email


# TODO singleton
class CeleryManager:
    def invoke_send_forgot_password_email(self, meta):
        return send_forgot_password_email.delay(meta)


celery_client = CeleryManager()
