# mailupy

💌 Yet another [MailUp](https://www.mailup.it/) Python client

[![Latest Version](https://img.shields.io/pypi/v/mailupy.svg)](https://pypi.python.org/pypi/mailupy/)
[![codecov](https://codecov.io/gh/lotrekagency/mailupy/branch/master/graph/badge.svg)](https://codecov.io/gh/lotrekagency/mailupy)
[![Build Status](https://travis-ci.org/lotrekagency/mailupy.svg?branch=master)](https://travis-ci.org/lotrekagency/mailupy)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/lotrekagency/mailupy/blob/master/LICENSE)

## Contributing

Any help is welcome, as long as you don't break the continuous integration.
Fork the repository and open a Pull Request directly on the master branch.
A maintainer will review and integrate your changes.

Maintainers:

- [Andrea Stagi](https://github.com/astagi)
- [Edoardo Grassi](https://github.com/edoaxyz)

Contributors:

- [Fabio Piras](https://github.com/Arussil)

## Install

```sh
pip install mailupy
```

## How to use

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

## Examples

Getting information about fields, groups...

```py
for field in client.get_fields():
    print (field)
```

```py
for group in client.get_groups_from_list(1):
    print (group)
```

Getting recipients from lists using [Ordering and Filtering (Mailup Documentation)](http://help.mailup.com/display/mailupapi/Paging+and+filtering)

```py
for group in client.get_groups_from_list(
        1, filter_by='Name.Contains(\'Farm\')',
        order_by=['Name asc', 'idGroup desc']):
    print (group)
```

```py
for recipient in client.get_subscribed_recipients_from_list(
        1, filter_by='Email.Contains(\'zzz\')',
        order_by=['Email desc']):
    print (recipient['Email'])
```

Getting a subscribed recipient from a list

```py
client.get_subscribed_recipient_from_list(1, 'andrea.stagi@lotrek.it')
```

Subscribe/Unsubscribe recipient to/from lists

```py
recipient_id = client.subscribe_to_list(
  1, 'Andrea Stagi', 'stagi.andrea@gmail.com', pending=False
)

client.unsubscribe_from_list(1, recipient_id)
```

## Run tests

```sh
pip install -r requirements-dev.txt
make test
```
