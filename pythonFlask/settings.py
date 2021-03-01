import configparser


conf = configparser.ConfigParser()
conf.read('settings.ini')

access_token = conf['qiita']['access_token']

port = conf['web']['port']
ip = conf['web']['ip']

db_name = conf['db']['name']
db_driver = conf['db']['driver']
