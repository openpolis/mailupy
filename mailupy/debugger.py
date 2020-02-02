import datetime
import json


def error_printer(user, typo, url, resp, *args, **kwargs):
    time = datetime.datetime.now().strftime('%H:%M:%S %d-%m-%Y')
    with open("mailup_error.log", "a") as f:
        print(f"    =======================>  {time}  <=======================", file=f)
        print(f"[MAILUP USER]: {user}\n[URL]: {url}", file=f)
        print(f"[REQUEST]:\ntype =====> {typo}", file=f)
        for key, value in kwargs.items():
            print(f"{key} =====> {value}", file=f)
        print(f"[RESPONSE]:\nstatus =====> {resp.status_code}", file=f)
        try:
            print(f"error =====> {resp.json()}", file=f)
        except json.JSONDecodeError:
            print(f"error =====> NONE", file=f)
        print("    ====================>  [{-_-}] this is an error.. <====================\n\n\n", file=f)
