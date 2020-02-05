# mailupy

💌 Yet another [MailUp](https://www.mailup.it/) Python client

[![Latest Version](https://img.shields.io/pypi/v/mailupy.svg)](https://pypi.python.org/pypi/mailupy/)
[![codecov](https://codecov.io/gh/lotrekagency/mailupy/branch/master/graph/badge.svg)](https://codecov.io/gh/lotrekagency/mailupy)
[![Build Status](https://travis-ci.org/lotrekagency/mailupy.svg?branch=master)](https://travis-ci.org/lotrekagency/mailupy)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/lotrekagency/mailupy/blob/master/LICENSE)

## Install

TODO

## Usage

Import Mailupy and instantiate the client

```py
from mailupy import Mailupy

client = Mailupy(
    'm00000',
    'm@1lUPf4k3',
    '8123dbff-d12c-4e3d-a55e-23a8c5a303f8',
    '16cadddf-a145-45db-9347-a5ab51ac223d'
)
```

Use the client to get information

```py
    for field in client.get_fields():
        print (field)
```

```py
    for group in client.get_groups_from_list(1):
        print (group)
```

Getting users from lists using [Ordering and Filtering (Mailup Documentation)](http://help.mailup.com/display/mailupapi/Paging+and+filtering)

```py
    for group in client.get_groups_from_list(
          1, filter_by='Name.Contains(\'Farm\')',
          order_by=['Name asc', 'idGroup desc']):
        print (group)
```

```py
    for user in client.get_subscribed_users_from_list(
          1, filter_by='Email.Contains(\'zzz\')',
          order_by=['Email desc']):
        print (user['Email'])
```

Getting a subscribed user from a list

```py
    print (client.get_subscribed_user_from_list(1, 'andrea.stagi@lotrek.it'))
```

## Run tests

```sh
pip install -r requirements-dev.txt
make test
```
