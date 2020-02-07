import json
import urllib

from .exceptions import MailupyException, MailupyRequestException
from .utils import type_to_request_function


class Mailupy:

    AUTH_URL = "https://services.mailup.com/Authorization/OAuth/Token"
    BASE_URL = "https://services.mailup.com/API/v1.1/Rest/ConsoleService.svc/Console"

    def __init__(self, username, password, client_id, client_secret):
        self._filters = {}
        self._token = None
        self._mailup_user = {
            'username': username,
            'password': password,
            'client_id': client_id,
            'client_secret': client_secret
        }
        self.login()

    def _requests_wrapper(self, req_type, url, *args, **kwargs):
        try:
            resp = type_to_request_function[req_type](url, **kwargs)
        except Exception as ex:
            raise MailupyException(ex)
        if resp.status_code == 429:
            resp = self._requests_wrapper(req_type, url, *args, **kwargs)
        if resp.status_code == 401:
            self._refresh_my_token()
            resp = self._requests_wrapper(
                req_type, url, *args, **{**kwargs, 'headers': self._default_headers()}
            )
        if resp.status_code >= 400:
            raise MailupyRequestException(resp)
        return resp

    def _download_all_pages(self, url):
        total = 1
        current = 0
        spacer = '&' if '?' in url else '?'
        is_paginated = True
        while total - current and is_paginated:
            data = self._requests_wrapper(
                'GET',
                f'{url}{spacer}pageNumber={current}',
                headers=self._default_headers()
            ).json()
            total = data['TotalElementsCount'] // data['PageSize']
            is_paginated = data['IsPaginated']
            for item in data['Items']:
                yield item
            current = current + 1

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
        mailup_fields = list()
        fields_id = dict()
        for elem in self.get_fields():
            fields_id[elem['Description']] = elem['Id']
        for key, value in fields.items():
            if key in fields_id.keys():
                mailup_fields.append({
                    "Description": key,
                    "Id": fields_id[key],
                    "Value": value
                })
        return mailup_fields

    def _parse_filter_ordering(self, **filter_ordering):
        if 'order_by' in filter_ordering:
            filter_ordering['order_by'] = ';'.join([el for el in filter_ordering['order_by']])
        query = '&'.join([
            '{0}={1}'.format(k.replace('_', ''), urllib.parse.quote_plus(v)) for k, v in filter_ordering.items()
        ])
        return query

    def _build_url(self, url, query_parameters=None):
        if query_parameters:
            return f'{self.BASE_URL}{url}?{query_parameters}'
        return f'{self.BASE_URL}{url}'

    def _get_recipients_from_generic_list(self, list_type, list_id, **filter_ordering):
        query = self._parse_filter_ordering(**filter_ordering)
        return self._download_all_pages(
            self._build_url(f'/List/{list_id}/Recipients/{list_type}', query)
        )

    def _get_recipient_from_generic_list(self, list_type, list_id, recipient_email):
        query = self._parse_filter_ordering(filter_by=f"Email=='{recipient_email}'")
        resp = self._requests_wrapper(
            'GET',
            self._build_url(f'/List/{list_id}/Recipients/{list_type}', query),
            headers=self._default_headers()
        )
        if resp.json()['Items']:
            return resp.json()['Items'][0]
        else:
            return None

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

    def get_fields(self, **filter_ordering):
        query = self._parse_filter_ordering(**filter_ordering)
        return self._download_all_pages(
            self._build_url(f'/Recipient/DynamicFields', query)
        )

    def get_groups_from_list(self, list_id, **filter_ordering):
        query = self._parse_filter_ordering(**filter_ordering)
        return self._download_all_pages(
            self._build_url(f'/List/{list_id}/Groups', query)
        )

    def get_recipients_from_list(self, list_id, **filter_ordering):
        return self._get_recipients_from_generic_list('EmailOptins', list_id, **filter_ordering)

    def get_subscribed_recipients_from_list(self, list_id, **filter_ordering):
        return self._get_recipients_from_generic_list('Subscribed', list_id, **filter_ordering)

    def get_unsubscribed_recipients_from_list(self, list_id, **filter_ordering):
        return self._get_recipients_from_generic_list('Unsubscribed', list_id, **filter_ordering)

    def get_recipient_from_list(self, list_id, recipient_email):
        return self._get_recipient_from_generic_list('EmailOptins', list_id, recipient_email)

    def get_subscribed_recipient_from_list(self, list_id, recipient_email):
        return self._get_recipient_from_generic_list('Subscribed', list_id, recipient_email)

    def get_unsubscribed_recipient_from_list(self, list_id, recipient_email):
        return self._get_recipient_from_generic_list('Unsubscribed', list_id, recipient_email)

    def get_recipients_from_group(self, group_id, **filter_ordering):
        query = self._parse_filter_ordering(**filter_ordering)
        return self._download_all_pages(
            self._build_url(f'/Group/{group_id}/Recipients', query)
        )

    def get_recipient_from_group(self, group_id, recipient_email):
        query = self._parse_filter_ordering(filter_by=f"Email=='{recipient_email}'")
        resp = self._requests_wrapper(
            'GET',
            self._build_url(f'/Group/{group_id}/Recipients', query),
            headers=self._default_headers()
        )
        if resp.json()['Items']:
            return resp.json()['Items'][0]
        else:
            return None

    def get_messages_from_list(self, list_id, tags=[], **filter_ordering):
        filter_ordering['tags'] = ','.join(tags)
        query = self._parse_filter_ordering(**filter_ordering)
        return self._download_all_pages(
            self._build_url(f'/List/{list_id}/Emails', query)
        )

    def get_or_create_group(self, list_id, group_name):
        for group in self.get_groups_from_list(list_id).get('Items', []):
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
        self._requests_wrapper(
            'POST',
            self._build_url('/Email/Send'),
            headers=self._default_headers(),
            data=payload
        )
        return True

    def create_group(self, list_id, group_name, notes=''):
        resp = self._requests_wrapper(
            'POST',
            self._build_url(f'/List/{list_id}/Group'),
            headers=self._default_headers(),
            data=json.dumps({"Name": group_name, "Notes": notes})
        )
        return resp.json()

    def update_customer_fields(self, recipient_name, recipient_email, fields={}):
        payload = json.dumps({
            "Name": recipient_name,
            "Email": recipient_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'PUT',
            self._build_url('/Recipient/Detail'),
            headers=self._default_headers(),
            data=payload
        )
        return resp.json()

    def subscribe_to_list(self, list_id, recipient_name, recipient_email, fields={}):
        payload = json.dumps({
            "Name": recipient_name,
            "Email": recipient_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'POST',
            self._build_url(f'/List/{list_id}/Recipient'),
            headers=self._default_headers(),
            data=payload
        )
        return resp.json()

    def subscribe_to_group(self, group_id, recipient_name, recipient_email, fields={}):
        payload = json.dumps({
            "Name": recipient_name,
            "Email": recipient_email,
            "Fields": self._build_mailup_fields(fields)
        })
        resp = self._requests_wrapper(
            'POST',
            self._build_url(f'/Group/{group_id}/Recipient'),
            headers=self._default_headers(),
            data=payload
        )
        return resp.json()

    def unsubscribe_from_list(self, list_id, recipient_mailup_id):
        self._requests_wrapper(
            'DELETE',
            self._build_url(f'/List/{list_id}/Unsubscribe/{recipient_mailup_id}'),
            headers=self._default_headers(),
        )
        return True

    def unsubscribe_from_group(self, group_id, recipient_mailup_id):
        self._requests_wrapper(
            'DELETE',
            self._build_url(f'/Group/{group_id}/Unsubscribe/{recipient_mailup_id}'),
            headers=self._default_headers(),
        )
        return True

    def remove_from_list(self, list_id, recipient_mailup_id):
        if list_id == 'all':
            self._requests_wrapper(
                'DELETE',
                self._build_url(f'/Recipients/{recipient_mailup_id}'),
                headers=self._default_headers(),
            )
        else:
            self._requests_wrapper(
                'DELETE',
                self._build_url(f'/List/{list_id}/Recipient/{recipient_mailup_id}'),
                headers=self._default_headers(),
            )
        return True
