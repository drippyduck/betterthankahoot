import string, random
import pandas as pd
import xlsxwriter
import mysql.connector
import sys

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root"
)

commands = ["import","export"]

mycursor = mydb.cursor()

mycursor.execute("USE quiz;")

numbers = ["0","1","2","3","4","5","6","7","8","9"]
alphabet = list(string.ascii_uppercase)


def check_code(code):

    code=code.upper()

    mycursor.execute(f"SELECT code FROM players WHERE code = '{code}';")
    mycursor.fetchall()

    if int(mycursor.rowcount) == 0:
        return True

    return False

def generate_code():
    while True:
        code = ""
        for i in range(6):
            if random.choice("10") == "1":
                code += random.choice(numbers)
            else:
                code += random.choice(alphabet)
        
        if check_code(code):
            break
        else:
            code = ""

    return code

def leave():
    print("Usage: python $PATH$/main.py export|import $filename$.xlsx")
    exit(0)

def insert_player(first,last):
    mycursor.execute(f"INSERT INTO `players`(`first`, `last`, `code`) VALUES ('{str(first)}','{str(last)}','{str(generate_code())}');")
    mydb.commit()

def import_file(file):
    data = pd.read_excel(fr'{file}')
    df = pd.DataFrame(data, columns=['first', 'last'])

    count = 0

    while True:
        try:
            if df['first'][count] != '':
                count += 1
        except:
            break

    for i in range(count):
        insert_player(df['first'][i],df['last'][i])
        

def export_file(file):
    workbook = xlsxwriter.Workbook(f'{file}')

    worksheet = workbook.add_worksheet()

    row=0
    col=0

    worksheet.write(row, col, "first")
    worksheet.write(row, col+1, "last")
    worksheet.write(row, col+2, "code")

    row += 1
    col = 0

    mycursor.execute("SELECT * FROM players;")

    for res in mycursor.fetchall():

        worksheet.write(row, col, res[2])
        worksheet.write(row, col+1, res[3])
        worksheet.write(row, col+2, res[4])

        col = 0
        row += 1
        
    
    workbook.close()


# ALTER TABLE table_name AUTO_INCREMENT = value;
# reset inc value ( value == next value of inc )


if len(sys.argv) < 3:
    leave()
else:
    if (sys.argv[1] in commands) and ( ( len(sys.argv[2].split(".")) > 1) and (sys.argv[2].split(".")[1] == "xlsx") ):
        if(sys.argv[1] == "import"):
            import_file(sys.argv[2])
        else:
            export_file(sys.argv[2])
    else:
        leave()
