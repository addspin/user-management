
import ldap3
# параметры подключения к active directory
server = ldap3.Server('agip-ald01.agip.intra', port=389, use_ssl=False)
user_dn = 'uid=agip-usm,ou=AGIP-service-accounts,dc=agip,dc=intra'
user_password = 'mPg7e2p^8C'

# подключение к active directory
conn = ldap3.Connection(server,  user_dn, user_password,  auto_referrals=False)

conn.bind()
attrs = ['displayName']
search_base = 'dc=agip,dc=intra'
search_filter = '(objectClass=person)'

conn.search(search_base, search_filter, attributes=attrs)
for entry in conn.entries:
    if entry.displayName != None:
        print(entry.displayName)

# закрытие соединения
conn.unbind()
