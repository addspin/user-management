import ldap3
import sqlite3
path_db = 'um.db'
# параметры подключения к active directory
port = 389
tls = False
server_name = 'intra.apur'
server = ldap3.Server(server_name, port=port, use_ssl=tls)
print(server)
# server = ldap3.Server('agip-dc01.intra.apur', port=389, use_ssl=False)
# user_dn = 'CN=agip-zabbix,OU=AGIP-service-accounts,OU=AGIP,DC=intra,DC=apur'
user_dn = 'CN=agip-usm,OU=AGIP-service-accounts,OU=AGIP,DC=intra,DC=apur'
user_password = 'mPg7e2p^8C'

# подключение к active directory
conn = ldap3.Connection(server,  user_dn, user_password,  auto_referrals=False)
conn.bind()

# поиск пользователей в OU

search_base = 'OU=AGIP-users,OU=AGIP,DC=intra,DC=apur'

search_filter = '(objectClass=user)'

attrs = ['displayName']
conn.search(search_base, search_filter, attributes=attrs)


# вывод найденных пользователей
conn_sql = sqlite3.connect(path_db)
cursor = conn_sql.cursor()
conn_sql.row_factory = sqlite3.Row

# for entry in conn.entries:
    # if entry.displayName != None:
    #     test = entry.displayName
# print(conn.entries[1].displayName)
test = conn.entries[1].displayName
print(test)
# str(test)
# test1 = test
cursor.execute("INSERT INTO users values (?)", (test))
conn_sql.commit()

        

# закрытие соединения

conn.unbind()
conn_sql.close()

