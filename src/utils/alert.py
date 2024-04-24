from ..utils.slack_utils import upload_file_to_slack

class AlertHelper():

    def __init__(self, error_helper, stub_name, docker_name) -> None:
        self.error_helper = error_helper
        self.stub_name = stub_name
        self.docker_name = docker_name

    def init_slack(self, token, channel_id):
        self.slack_token = token
        self.slack_channel_id = channel_id

    def get_fmtd_error_msg(self, error_code):
        error_msg = self.error_helper.get_error_message(error_code)
        return f'Alert: {error_msg}. Stub: {self.stub_name}. Docker image: {self.docker_name}'

    def alert_on_slack(self, error_code, file_payload=""):
        fmtd_error_msg = self.get_fmtd_error_msg(error_code)
        response = upload_file_to_slack(
            self.slack_channel_id,
            self.slack_token,
            fmtd_error_msg,
            {'file': file_payload}
        )
        return response.status_code