import os
import csv
import hashlib
import base64


outputfile = "output.ldif"
existingGroupe =[]
existingUsers = []
default_gids_start = 1000
default_uids_start = 5000

def getgroupentity(Row):
    global default_gids_start
    inside =0
    gnumber = default_gids_start
    for elem in existingGroupe:
        if Row[1] in elem:
            inside = 1
            gnumber = elem[2]

    if inside == 0:
            existingGroupe.append([Row[0],Row[1], gnumber])
            default_gids_start += 1
    else:
        existingGroupe.append([Row[0], Row[1], gnumber])


def getGid(login):
    for elem in existingGroupe:
        if elem[0] == login:
            return elem[2]
    return None


def insertUsers(Row,file):
    global default_uids_start
    hash = hashlib.sha1(bytes(Row[3],"utf-8"))
    hash = hash.digest()

    hash = base64.b64encode(hash).decode()

    str = f"""
dn: uid={Row[2]},ou=People,dc=ansible,dc=fr
objectclass: top
objectclass: inetOrgPerson
objectclass: person
objectclass: organizationalPerson
objectclass: posixAccount
objectclass: shadowAccount"""
    try:
        Row[1].encode("ascii")
        Row[0].encode("ascii")

    except UnicodeEncodeError:
        fullname = Row[1] +" "+Row[0]
        fullname = base64.b64encode(fullname.encode("utf-8")).decode("ascii")
        Row[1] = base64.b64encode(Row[1].encode("utf-8")).decode("ascii")
        Row[0] = base64.b64encode(Row[0].encode("utf-8")).decode("ascii")

        str += f"""
cn:: {fullname}
sn:: {Row[0]}
givenName:: {Row[1]}"""
    else:
        str += f"""
cn: {Row[1]} {Row[0]}
sn: {Row[0]}
givenName: {Row[1]}"""
    str += f"""
uid: {Row[2]}
userpassword: {{SHA}}{hash}
loginshell: /bin/bash
gidnumber: {getGid(Row[2])}
uidnumber: {default_uids_start}
homeDirectory: /home/{Row[2]}\n
"""

    file.write(str)
    default_uids_start += 1

def insertGroupes(file):
    for elem in existingGroupe:

        str = """dn: cn={},ou=Group,dc=ansible,dc=fr
cn: {}
objectclass: posixGroup
objectclass: top
gidnumber: {}\n
""".format(elem[0],elem[0],elem[2])
        file.write(str)



def main():
    try:
        elems = os.listdir("./csvfiles")
    except FileNotFoundError:
        print("All CSV files should be inside the ./csvfiles folder, current location{}".format(os.getcwd()))
    else:

        file = open(outputfile, "a")
        file.seek(0)
        file.truncate()
        for elem in elems:
            with open("./csvfiles/" + elem, "r") as csvfile:
                ptr = csv.reader(csvfile, delimiter=';')
                row = next(ptr)

                if "Group" in row:
                    for row in ptr:
                        getgroupentity(row)
                    insertGroupes(file)
                else:
                    for row in ptr:
                        insertUsers(row,file)



if "__main__" == __name__:
    main()
