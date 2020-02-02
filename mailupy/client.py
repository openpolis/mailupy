import json
import requests
from .debugger import error_printer
from .exceptions import MailupyException, MailupyRequestException


class Mailupy:

    AUTH_URL = "https://services.mailup.com/Authorization/OAuth/Token"
    BASE_URL = "https://services.mailup.com/API/v1.1/Rest/ConsoleService.svc/Console"

    def __init__(self, username, password, client_id, client_secret, error_log=False):
        self._token = None
        self._mailup_user = {
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret
        }
        self._error_log = error_log
        self.login()

    def _requests_wrapper(self, typo, url, *args, **kwargs):
        try:
            if typo == 'GET':
                resp = requests.get(url, **kwargs)
            elif typo == 'POST':
                resp = requests.post(url, **kwargs)
            elif typo == 'PUT':
                resp = requests.put(url, **kwargs)
            elif typo == 'DELETE':
                resp = requests.delete(url, **kwargs)
        except Exception as ex:
            raise MailupyException(ex)
        if resp.status_code == 429:
            resp = self._requests_wrapper(typo, url, *args, **kwargs)
        if resp.status_code == 401:
            self._refresh_my_token()
            resp = self._requests_wrapper(typo, url, *args, **{**kwargs, 'headers': self._default_headers()})
        if resp.status_code >= 400:
            if self._error_log:
                error_printer(
                    self._mailup_user['username'],
                    typo, url, resp,
                    **kwargs
                )
            raise MailupyRequestException(resp)
        return resp

    def _download_all_pages(self, url, current=0, items=[], single_page=None):
        spacer = '&' if '?' in url else '?'
        items = items if current else []
        if single_page is not None:
            return self._requests_wrapper(
                'GET',
                f'{url}{spacer}pageNumber={single_page}',
                headers=self._default_headers()
            ).json()
        data = self._requests_wrapper(
            'GET',
            f'{url}{spacer}pageNumber={current}',
            headers=self._default_headers()
        ).json()
        total = data['TotalElementsCount'] // data['PageSize']
        items += data['Items']
        if total - current:
            self._download_all_pages(url, current + 1, items)
        return {'WrappedPages': total, 'Items': items}

    def _default_headers(self):
        headers = {'Content-type': 'application/json'}
        if self._token:
            headers['Authorization'] = f'Bearer {self._token}'
        return headers

    def _refresh_my_token(self):
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self._mailup_user['client_id'],
            'client_secret': self._mailup_user['client_secret'],
            'refresh_token': self._refresh_token,
        }
        resp = self._requests_wrapper(
            'POST',
            f'{self.AUTH_URL}',
            data=payload,
        )
        if resp.status_code == 200:
            self._token = resp.json()['access_token']
            self._refresh_token = resp.json()['refresh_token']
            return True
        raise MailupyRequestException(resp)

    def _build_mailup_fields(self, fields={}):
        avaiabe_fields = self.get_fields()
        mailup_fields = list()
        fields_id = dict()
        for elem in avaiabe_fields['Items']:
            fields_id[elem['Description']] = elem['Id']
        for key, value in fields.items():
            if key in fields_id.keys():
                mailup_fields.append({
                    "Description": key,
                    "Id": fields_id[key],
                    "Value": value
                })
        return mailup_fields

    def login(self):
        payload = {
            'grant_type': 'password',
            'client_id': self._mailup_user['client_id'],
            'client_secret': self._mailup_user['client_secret'],
            'username': self._mailup_user['username'],
            'password': self._mailup_user['password']
        }
        resp = self._requests_wrapper(
            'POST',
            f'{self.AUTH_URL}',
            data=payload,
        )
        if resp.status_code == 200:
            self._token = resp.json()['access_token']
            self._refresh_token = resp.json()['refresh_token']
            return True
        return False

    def get_fields(self, page=None):
        return self._download_all_pages(f'{self.BASE_URL}/Recipient/DynamicFields')

    def get_groups_from_list(self, list_id, page=None):
        return self._download_all_pages(
            f'{self.BASE_URL}/List/{list_id}/Groups',
            single_page=page
        )

    def get_users_from_list(self, list_id, page=None):
        return self._download_all_pages(
            f'{self.BASE_URL}/List/{list_id}/Recipients/EmailOptins',
            single_page=page
        )

    def get_users_from_group(self, group_id, page=None):
        return self._download_all_pages(
            f'{self.BASE_URL}/Group/{group_id}/Recipients',
            single_page=page
        )

    def get_message_by_subject(self, list_id, subject, page=None):
        return self._download_all_pages(
            f'{self.BASE_URL}/List/{list_id}/Emails?filterby="Subject.Contains(%27{subject}%27)"',
            single_page=page
        )

    def get_message_by_tags(self, list_id, tags, page=None):
        tags = ', '.join(tags)
        return self._download_all_pages(
            f'{self.BASE_URL}/List/{list_id}/Emails?tags="{tags}"',
            single_page=page
        )

    def get_or_create_group(self, list_id, group_name):
        group_list = self.get_groups_from_list(list_id)
        for group in group_list.get('Items', []):
            if group.get('Name', '') == group_name:
                return group.get('idGroup', None), False
        group = self.create_group(list_id, group_name)
        if 'idGroup' in group:
            return group['idGroup'], True
        return None, False

    def send_message(self, email, message_id):
        payload = json.dumps({
            "Email": email,
            "idMessage": message_id
        })
        resp = self._requests_wrapper(
            'POST',
            f'{self.BASE_URL}/Email/Send',
            headers=self._default_headers(),
            data=payload
        )
        if resp.status_code == 200:
            return True
        return False

    def create_group(self, list_id, group_name, notes=''):
        resp = self._requests_wrapper(
            'POST',
            f'{self.BASE_URL}/List/{list_id}/Group',
            headers=self._default_headers(),
            data=json.dumps({"Name": group_name, "Notes": notes})
        )
        return resp.json()

    def update_customer_fields(self, user_name, user_email, fields={}):
        payload = json.dumps({
            "Name": user_name,
            "Email": user_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'PUT',
            f'{self.BASE_URL}/Recipient/Detail',
            headers=self._default_headers(),
            data=payload
        )
        if resp.status_code != 200:
            return False
        return resp.json()

    def subscribe_to_list(self, list_id, user_name, user_email, fields={}):
        payload = json.dumps({
            "Name": user_name,
            "Email": user_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'POST',
            f'{self.BASE_URL}/List/{list_id}/Recipient',
            headers=self._default_headers(),
            data=payload
        )
        return resp.json()

    def subscribe_to_group(self, group_id, user_name, user_email, fields={}):
        payload = json.dumps({
            "Name": user_name,
            "Email": user_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'POST',
            f'{self.BASE_URL}/Group/{group_id}/Recipient',
            headers=self._default_headers(),
            data=payload
        )
        return resp.json()

    def unsubscribe_from_list(self, list_id, user_mailup_id):
        resp = self._requests_wrapper(
            'DELETE',
            f'{self.BASE_URL}/List/{list_id}/Unsubscribe/{user_mailup_id}',
            headers=self._default_headers(),
        )
        if resp.status_code == 200:
            return True
        return False

    def unsubscribe_from_group(self, group_id, user_mailup_id):
        resp = self._requests_wrapper(
            'DELETE',
            f'{self.BASE_URL}/Group/{group_id}/Unsubscribe/{user_mailup_id}',
            headers=self._default_headers(),
        )
        if resp.status_code == 200:
            return True
        return False

    def remove_from_list(self, list_id, user_mailup_id):
        if list_id == 'all':
            resp = self._requests_wrapper(
                'DELETE',
                f'{self.BASE_URL}/Recipients/{user_mailup_id}',
                headers=self._default_headers(),
            )
            if resp.status_code == 200:
                return True
            return False
        resp = self._requests_wrapper(
            'DELETE',
            f'{self.BASE_URL}/List/{list_id}/Recipient/{user_mailup_id}',
            headers=self._default_headers(),
        )
        if resp.status_code == 200:
            return True
        return False
