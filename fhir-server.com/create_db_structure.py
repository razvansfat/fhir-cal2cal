import psycopg2
import hashlib

# mysql_alchemy
# flask conectare la bd prin socket

def conn_db(db_name):
    # connection establishment
    conn = psycopg2.connect(
    database=db_name,
    	user='postgres',
    	password='1123581321',
    	host='localhost',
    	port= '5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    return cursor

def creare_bd(db_name):

    cursor = conn_db(db_name)
    nume_bd = input("Introdu numele bazei de date: ")
    db_name = nume_bd

    sql = f''' CREATE database {db_name}''';
    cursor.execute(sql)
    rez = f"Database {db_name} has been created successfully !!"
    cursor.close()

    return rez

def creare_tabele(db_name):
    cursor = conn_db(db_name)

    nume_tabela = input("Introdu numele tabelei: ")
    continua = 'D'
    campuri = ''
    while continua.upper() == 'D':
        
        nume_camp = input("Nume camp: ")
        tip_camp = input("Tip camp (integer, varchar, date, text): ")
        if tip_camp == 'varchar':
            lungime_camp = input("Lungime camp: ")
        not_null_camp = input("Not null camp?(D/N): ")
        primary_key_camp = input("Primary key camp?(D/N): ")

        campuri = campuri + nume_camp + ' '
        if tip_camp == 'varchar':
            campuri = campuri + tip_camp + '(' + lungime_camp + ')'
        else:
            campuri = campuri + tip_camp
        if not_null_camp.upper() == 'D':
            campuri = campuri + ' not null'
        if primary_key_camp.upper() == 'D':
            campuri = campuri + ' primary key'
        
        print("-----------------------------------")
        continua = input("Adaugi camp nou? D/N: ")
        print("-----------------------------------")

        if continua.upper() == 'D':
            campuri = campuri + ', '
        
    sql = f''' CREATE table {nume_tabela} ({campuri})'''
    try:
        cursor.execute(sql)
        rez = f"Table {nume_tabela} has been created successfully !!"
    except Exception as e:
        print(e)

    return rez   

def creare_secventa(db_name):
    cursor = conn_db(db_name)

    tabela_secventa = input("Alege tabela: ")
    camp_secventa = input("Alege camp: ")
    nume_secventa = input("Nume secventa: ")
    # # query to create a sequence
    sql = f''' CREATE sequence {nume_secventa} ''';
    try:
        cursor.execute(sql)
        print("Secventa creata")
    except Exception as e:
        print(e)
    
    # query to link sequence to table
    sql = f''' alter table {tabela_secventa} alter column {camp_secventa} set default nextval('{nume_secventa}') ''';
    try:
        cursor.execute(sql)
        rez = f"Secventa {nume_secventa} adaugata la tabela {tabela_secventa} pt campul {camp_secventa}"
    except Exception as e:
        print(e)
        
    return rez

def creaza_db_user(db_name):
    cursor = conn_db(db_name)
    # CREATE ROLE test WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION ENCRYPTED PASSWORD 'SCRAM-SHA-256$4096:IOXa9EuqAlaoKYz9TfYZmw==$URLU3QixMAbyV0dh4j56DeHErzPo5W7wcxp1cGB+cvI=:JmdnkX8M2b9KBl4X7AiC6wodtdYRsZy996rDzUXbJ1c=';
    # ALTER DATABASE test OWNER TO postgres;

    nume_bd = input("Introdu numele bazei de date: ")
    user_nou = input("Introdu numele adminului bazei de date: ")
    parola_noua = input("Introdu parola: ")
    encoded = parola_noua.encode()
    result = hashlib.sha256(encoded)
    print(result)

    sql = f''' CREATE ROLE {user_nou} WITH LOGIN NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION ENCRYPTED PASSWORD '{result}' ''';
    try:
        cursor.execute(sql)
        print (f"S-a creat userul {user_nou} ")
        sql = f''' ALTER DATABASE {nume_bd} OWNER TO {user_nou} ''';
        rez = f"Tabela {db_name} are userul {user_nou}"
    except Exception as e:
        print(e)

    return rez

def test_db(db_name) -> str:
    cursor = conn_db(db_name)

    sql = ''' select * from users '''
    try:
        cursor.execute(sql)
        rez = cursor.fetchall()

    except Exception as e:
        print(e)

    return rez

def main():
    db_name = ''
    db_name = input('Introdu numele bazei de date pentru creare tabele. (camp gol pentru a crea o baza de date): ')
    
    if db_name == '':
        db_name = 'postgres'

    opt_init = 0.1
    while opt_init != 0:
        optiune = int(input('Alege 1(creare BD), 2(creare tabela), 3(creaza secvente), 4(creare user DB), 5(testare db) (0 pt iesre): '))

        if optiune == 1:
            rez = creare_bd(db_name)
            db_name = rez
            print(rez)
        if optiune == 2:
            rez = creare_tabele(db_name)
            print(rez)
        if optiune == 3:
            rez = creare_secventa(db_name)
            print(rez)
        if optiune == 4:
            rez = creaza_db_user(db_name)
            print(rez)
        if optiune == 5:
            rez = test_db(db_name)
            print(rez)
        if optiune == 0:
            break

if __name__ == "__main__":
    main()
