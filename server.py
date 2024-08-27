import pandas as pd
from flask import Flask, jsonify , request
from flask_cors import CORS
import mysql.connector
import bcrypt
import jwt
from functools import wraps
app = Flask(__name__)
CORS(app)

# DATABASE CONFIG
# mysql
host = 'localhost'
user = 'admin'
password = 'root'
database='prolexbase'
#database='your_database_name'


#connecting to the database 
connection = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    charset="utf8"
)
# server utils :
def verify_if_exists(data_table,column_name,word):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {data_table} WHERE {column_name} = %s", (word,))
    result = cursor.fetchall()
    cursor.close()
    if len(result)>0:
        return result[0][0]
    return False

def get_max_id(table_name,column_name):
    cursor = connection.cursor()
    query = f"SELECT MAX({column_name}) FROM {table_name}"
    cursor.execute(query)
    max = cursor.fetchall()
    cursor.close()
    try:
        new_id = max[0][0] + 1
    except:
        new_id = 0
    return new_id

def insert_type(NUM_TYPE,FRA_TYPE,SUPERTYPE,ENG_TYPE,NOTE,table_name):
    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Sample data to insert
    data_to_insert = {
        "NUM_TYPE": NUM_TYPE,
        "FRA_TYPE": FRA_TYPE,
        "`NUM_TYPE-SUPERTYPE`": SUPERTYPE,  
        "ENG_TYPE": ENG_TYPE,
        "NOTE": NOTE,
    }

    # Build the INSERT INTO query
    insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"

    # Execute the INSERT INTO query with the data
    cursor.execute(insert_query, tuple(data_to_insert.values()))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()
def insert_existence(NUM_EXISTENCE,FRA_EXISTENCE,NOTE,ENG_EXISTENCE,table_name):
    cursor = connection.cursor()

    # Sample data to insert
    data_to_insert = {
        "NUM_EXISTENCE": NUM_EXISTENCE,
        "FRA_EXISTENCE": FRA_EXISTENCE,
        "NOTE": NOTE,
        "ENG_EXISTENCE": ENG_EXISTENCE,
    }

    # Build the INSERT INTO query
    insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"

    # Execute the INSERT INTO query with the data
    cursor.execute(insert_query, tuple(data_to_insert.values()))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()
def insert_pivot(NUM_PIVOT,NUM_TYPE,NUM_EXISTENCE,table_name):
    cursor = connection.cursor()

    # Sample data to insert
    data_to_insert = {
        "NUM_PIVOT" : NUM_PIVOT,
        "NUM_TYPE":NUM_TYPE,
        "NUM_EXISTENCE": NUM_EXISTENCE,
    }

    # Build the INSERT INTO query
    insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"

    # Execute the INSERT INTO query with the data
    cursor.execute(insert_query, tuple(data_to_insert.values()))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()
def insert_prolexeme(table_name,NUM_PROLEXEME,LABEL_PROLEXEME,NUM_PIVOT,SORT,NUM_FREQUENCY,WIKIPEDIA_LINK):
    cursor = connection.cursor()

    # Sample data to insert
    data_to_insert = {
        "NUM_PROLEXEME":NUM_PROLEXEME,
        "LABEL_PROLEXEME": LABEL_PROLEXEME,
        "NUM_PIVOT":NUM_PIVOT ,
        "SORT":SORT ,
        "NUM_FREQUENCY":NUM_FREQUENCY ,
        "WIKIPEDIA_LINK":WIKIPEDIA_LINK,
    }

    # Build the INSERT INTO query
    insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"

    # Execute the INSERT INTO query with the data
    cursor.execute(insert_query, tuple(data_to_insert.values()))

    # Commit the changes
    connection.commit()

    # Close the cursor and connection
    cursor.close()



# ROUTING :
def generate_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password_hash(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_token(user_id):
    return jwt.encode({'user_id': user_id}, 'super-secret', algorithm='HS256')

# ------ REGISTER :
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    hashed_password = generate_password_hash(password)
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
    cursor.close()
    connection.commit()
    return jsonify({'message': 'User registered successfully'})
# ------ LOGIN :
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()
    cursor.close()
    if user and check_password_hash(password, user[2]):
        token = jwt.encode({'user_id': user[0]}, 'super-secret', algorithm='HS256')
        return jsonify({'message':'welcome','token':token})
    else:
        return jsonify({'error': 'Invalid username or password'}), 401  
# ------ TOKEN :
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.json['token']
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        decoded_token = jwt.decode(token, 'super-secret', algorithms=['HS256'])
        if not decoded_token:
            return jsonify({'error': 'Invalid token'}), 401

        return f(decoded_token, *args, **kwargs)
    return decorated_function


# show all types :

@app.route('/gettypes', methods=['Get'])
def gettypes():
    query = f"select FRA_TYPE from type"
    cursor = connection.cursor()
    cursor.execute(query)
    types = cursor.fetchall()
    return jsonify({'types':types})\
    
# show all existences :

@app.route('/getexistance', methods=['Get'])
def getexistance():
    query = f"select FRA_EXISTENCE from existence"
    cursor = connection.cursor()
    cursor.execute(query)
    existences = cursor.fetchall()
    return jsonify({'existences':existences})


# show all pivots :

@app.route('/getpivots', methods=['Get'])
def getpivots():
    query = f"select NUM_PIVOT from pivot"
    cursor = connection.cursor()
    cursor.execute(query)
    items = cursor.fetchall()
    pivots=[]
    for t in items:
        pivots.append(t[0])
    return jsonify({'pivots':pivots})



# ------ RECHERCHE PROLEXEME :
@app.route('/find', methods=['POST'])
def find_one():
    word=request.json['word'].lower()
    langue=request.json['language']
    cursor = connection.cursor()
    query = f"SELECT pro.NUM_PROLEXEME ,pro.LABEL_PROLEXEME ,pro.NUM_FREQUENCY ,pro.WIKIPEDIA_LINK ,type.FRA_TYPE ,existence.FRA_EXISTENCE ,pro.NUM_PIVOT FROM prolexeme_{langue} AS pro ,pivot , type ,existence WHERE pivot.NUM_EXISTENCE=existence.NUM_EXISTENCE AND pivot.NUM_TYPE=type.NUM_TYPE AND pivot.NUM_PIVOT=pro.NUM_PIVOT AND BINARY LOWER(pro.LABEL_PROLEXEME) = %s "
    cursor.execute(query, (word,))
    results = cursor.fetchall()
    cursor.close()
    num_prolexeme=results[0][0]
    cursor = connection.cursor()
    query = f"SELECT NOTORITY , YEAR FROM notority_{langue}  WHERE NUM_PROLEXEME= %s"
    cursor.execute(query, (num_prolexeme,))
    noto = cursor.fetchall()
    notority=[]
    for item in noto:
        one_notority={'year':item[1], 'noto':item[0]}
        notority.append(one_notority)
    cursor.close()

    num_pivot=results[0][6]
    cursor = connection.cursor()
    query = f"SELECT pro.label_prolexeme FROM synonymy as syn , prolexeme_{langue} AS pro WHERE (pro.num_pivot = syn.`NUM_PIVOT-SYNONYMOUS`  and syn.`NUM_PIVOT-CANONICAL`= %s) or (pro.num_pivot = syn.`NUM_PIVOT-CANONICAL` and syn.`NUM_PIVOT-SYNONYMOUS`=  %s) "
    cursor.execute(query, (num_pivot,num_pivot))
    synonym = cursor.fetchall()
    cursor.close()

    cursor = connection.cursor()
    cursor.execute(f"select prolexeme_{langue}.label_prolexeme from pivot , Meronymy , prolexeme_{langue} where Meronymy.`NUM_PIVOT-HOLONYMOUS`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = Meronymy.`NUM_PIVOT-MERONYMOUS`", (num_pivot,))
    meronymy = cursor.fetchall()
    if len(meronymy) == 0:
        cursor = connection.cursor()
        cursor.execute(f"select prolexeme_{langue}.label_prolexeme from pivot , Meronymy , prolexeme_{langue} where Meronymy.`NUM_PIVOT-MERONYMOUS`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = Meronymy.`NUM_PIVOT-HOLONYMOUS`", (num_pivot,))
        meronymy = cursor.fetchall()
        if len(meronymy) == 0:
            meronymy=''

    cursor = connection.cursor()
    cursor.execute(f"select prolexeme_{langue}.label_prolexeme from pivot , accessibility , prolexeme_{langue} where accessibility.`NUM_PIVOT-ARGUMENT1`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = accessibility.`NUM_PIVOT-ARGUMENT2`", (num_pivot,))
    accessibility = cursor.fetchall()
    if len(accessibility) == 0:
        cursor = connection.cursor()
        cursor.execute(f"select prolexeme_{langue}.label_prolexeme from pivot , accessibility , prolexeme_{langue} where accessibility.`NUM_PIVOT-ARGUMENT2`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = accessibility.`NUM_PIVOT-ARGUMENT1`", (num_pivot,))
        accessibility = cursor.fetchall()
        if len(accessibility) == 0:
            accessibility=''

    response={'results':results,'notority':notority ,'synonymy':synonym ,'meronymy':meronymy ,'accessibility':accessibility}
    return jsonify(response)

# ------ RECHERCHE AVAN :
@app.route('/find_adv', methods=['POST'])
def find_adv():
    cursor = connection.cursor()
    langue=request.json['language']
    first_letter=request.json['first'].lower()
    last_letter=request.json['last'].lower()
    middle=request.json['middle'].lower()
    typeprolexeme = request.json['type']
    query = f"SELECT * FROM prolexeme_{langue} as prolexeme , pivot , type  WHERE lower(prolexeme.LABEL_PROLEXEME) LIKE binary '{first_letter}%{middle}%{last_letter}' and prolexeme.NUM_PIVOT = pivot.NUM_PIVOT and pivot.NUM_TYPE = type.NUM_TYPE and type.FRA_TYPE = %s"
    cursor.execute(query,(typeprolexeme,))
    results = cursor.fetchall()
    cursor.close()

    
    response={'results':results}
    return jsonify(response)

# ------ TOP NOTORIETE :
@app.route('/topnotority', methods=['POST'])
def topnotority():
    cursor = connection.cursor()
    langue = request.json['language']
    year = request.json['year']
    limit = request.json['limit']
    type_val = request.json['type'] 
    frequency = request.json['frequency']
    query = f"""
        SELECT p.LABEL_PROLEXEME , n.NOTORITY 
        FROM Notority_{langue} AS n, prolexeme_{langue} AS p, pivot, type 
        WHERE n.year = %s 
            AND n.NUM_PROLEXEME = p.NUM_PROLEXEME 
            AND p.NUM_PIVOT = pivot.NUM_PIVOT 
            AND pivot.NUM_TYPE = type.NUM_TYPE 
            AND type.FRA_TYPE = %s  and n.NOTORITY= %s
        ORDER BY n.NOTORITY 
        LIMIT %s
    """
    cursor.execute(query, (year, type_val,frequency, limit))
    results = cursor.fetchall()
    cursor.close()
    response={'results':results}
    return jsonify(response)


# ------ AJOUTER A PARTIR D UN FICHIER :
@app.route('/upload', methods=['POST'])
@token_required
def upload_file(token):
    cursor = connection.cursor()
    file = request.files['file']
    df = pd.read_excel(file)

    for line in range(len(df)):
        data = df.iloc[line]
        table_name = f"prolexeme_{data['langue']}"
        # Verify if the prolexeme already exists
        if verify_if_exists(table_name, 'LABEL_PROLEXEME', data['prolexeme']):
            continue
        # Prepare related data
        numero_pivot = str(data['num_pivot'])
        type_id = verify_if_exists('type', 'FRA_TYPE', data['type'])
        existance_id = verify_if_exists('existence', 'FRA_EXISTENCE', data['existance'])
        # Check if the pivot exists
        if not verify_if_exists('pivot', 'num_pivot', numero_pivot):
            cursor.execute("INSERT INTO pivot (num_type, NUM_EXISTENCE) VALUES (%s, %s)", (type_id, existance_id))
            connection.commit()
            cursor.execute("SELECT MAX(NUM_PIVOT) FROM pivot")
            numero_pivot = cursor.fetchone()[0]
        else:
            cursor.execute("SELECT NUM_PIVOT FROM pivot WHERE num_pivot = %s", (numero_pivot,))
            numero_pivot = cursor.fetchone()[0]
        # Prepare new prolexeme data
        new_id = get_max_id(table_name, 'NUM_PROLEXEME')
        data_to_insert = {
            "LABEL_PROLEXEME": data['prolexeme'],
            "NUM_PIVOT": int(numero_pivot),
            "SORT": 1,
            "NUM_FREQUENCY": int(data['notorite']),
            "WIKIPEDIA_LINK": data['source'],
        }

        # Insert into prolexeme table
        try:
            insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"
            cursor.execute(insert_query, tuple(data_to_insert.values()))
            connection.commit()
        except mysql.connector.IntegrityError as e:
            continue

        # Insert into staging table
        try:
            staging_table = f"stg_{table_name}"
            insert_query = f"INSERT INTO {staging_table} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"
            cursor.execute(insert_query, tuple(data_to_insert.values()))
            connection.commit()
        except mysql.connector.IntegrityError as e:
            continue

    cursor.close()
    connection.close()

    return jsonify({'data': 'your_data'})

# ------ AJOUTER PROLEXEME :
@app.route('/add', methods=['POST'])
@token_required
def add(token):
    cursor = connection.cursor()
    data=request.json
    table_name = f"prolexeme_{data['langue']}"
    exister=verify_if_exists(table_name,'LABEL_PROLEXEME',data['prolexeme'])
    if exister :
        return jsonify({'message':'this element exists'})
    numero_pivot= data['Num_pivot']
    type_id =verify_if_exists('type','FRA_TYPE',data['Type'])
    existance_id = verify_if_exists('existence','FRA_EXISTENCE',data['Existance'])
    cursor = connection.cursor()
    cursor.execute("Select max(num_prolexeme) from prolexeme_fra")
    new_id= cursor.fetchone()[0] + 1
    cursor.close()
    if verify_if_exists('pivot', 'num_pivot' ,numero_pivot)== False:
        cursor= connection.cursor()
        cursor.execute("insert into pivot (num_type,NUM_EXISTENCE) values (%s,%s)",(type_id,existance_id))
        cursor.close()
        connection.commit()
        cursor = connection.cursor()
        cursor.execute("Select max(num_pivot) from pivot")
        numero_pivot= cursor.fetchone()[0]
        cursor.close()

    data_to_insert = {
    "NUM_PROLEXEME":new_id,
    "LABEL_PROLEXEME": data['prolexeme'],
    "NUM_PIVOT": int(numero_pivot),
    "SORT":1 ,
    "NUM_FREQUENCY":int(data['Notorite']) ,
    "WIKIPEDIA_LINK":data['source'],}
    cursor = connection.cursor()
    insert_query = f"INSERT INTO {table_name} ({', '.join(data_to_insert.keys())}) VALUES ({', '.join(['%s'] * len(data_to_insert))})"
    cursor.execute(insert_query, tuple(data_to_insert.values()))
    cursor.close()
    connection.commit()
    response={'message':'added successfully'}
    return jsonify(response)

# ------ GET PROLEXEME :
@app.route('/getprolexeme', methods=['POST'])
@token_required
def getprolexeme(token):
    cursor = connection.cursor()
    data=request.json
    table_name = f"prolexeme_{data['langue']}"
    cursor = connection.cursor()
    cursor.execute(f"select * from {table_name} where binary lower(label_prolexeme)= %s" ,(data['prolexeme'].lower(),)) 
    res = cursor.fetchall()
    cursor.close()
    if len(res)==0:
        exister = False
    else: 
        exister=res[0][0]
    if exister :
        cursor = connection.cursor()
        if data['langue'] == 'fra':
            cursor.execute(f'''
    SELECT * 
    FROM {table_name} AS prolexeme
    LEFT JOIN pivot ON prolexeme.num_pivot = pivot.num_pivot
    LEFT JOIN type ON pivot.NUM_TYPE = type.NUM_TYPE
    LEFT JOIN existence ON pivot.NUM_EXISTENCE = existence.NUM_EXISTENCE
    LEFT JOIN prolexeme_arb AS prolexeme_a ON pivot.num_pivot = prolexeme_a.num_pivot
    LEFT JOIN prolexeme_eng AS prolexeme_b ON pivot.num_pivot = prolexeme_b.num_pivot
    WHERE prolexeme.num_prolexeme = {exister}
''')
        elif data['langue']== 'eng':
            cursor.execute(f'''
    SELECT * 
    FROM {table_name} AS prolexeme
    LEFT JOIN pivot ON prolexeme.num_pivot = pivot.num_pivot
    LEFT JOIN type ON pivot.NUM_TYPE = type.NUM_TYPE
    LEFT JOIN existence ON pivot.NUM_EXISTENCE = existence.NUM_EXISTENCE
    LEFT JOIN prolexeme_fra AS prolexeme_a ON pivot.num_pivot = prolexeme_a.num_pivot
    LEFT JOIN prolexeme_arb AS prolexeme_b ON pivot.num_pivot = prolexeme_b.num_pivot
    WHERE prolexeme.num_prolexeme = {exister}
''')

        else:
            cursor.execute(f'''
    SELECT * 
    FROM {table_name} AS prolexeme
    LEFT JOIN pivot ON prolexeme.num_pivot = pivot.num_pivot
    LEFT JOIN type ON pivot.NUM_TYPE = type.NUM_TYPE
    LEFT JOIN existence ON pivot.NUM_EXISTENCE = existence.NUM_EXISTENCE
    LEFT JOIN prolexeme_fra AS prolexeme_a ON pivot.num_pivot = prolexeme_a.num_pivot
    LEFT JOIN prolexeme_eng AS prolexeme_b ON pivot.num_pivot = prolexeme_b.num_pivot
    WHERE prolexeme.num_prolexeme = {exister}
''')

        
        res =cursor.fetchone()
        return jsonify({'res':res})
    response={'message':'added successfully'}
    return jsonify(response)


##################### delete 
@app.route('/deleteprolexeme', methods=['POST'])
@token_required
def deleteProlexeme(token):
    data = request.json
    cursor = connection.cursor()

    cursor.execute(f"delete from prolexeme_{data['langue']} where label_prolexeme='{data['prolexeme']}'")
    cursor.close()
    connection.commit()

    return jsonify({'msg':'prolexeme deleted'})


#################### update prolexeme :
@app.route('/updateprolexeme', methods=['POST'])
@token_required
def updateProlexeme(token):
    data = request.json
    cursor = connection.cursor()
    b_type=verify_if_exists('type','FRA_TYPE',data['type'])
    b_existance=verify_if_exists('existence','FRA_EXISTENCE',data['existance'])
    if b_type and b_existance:
        cursor.execute(f"UPDATE pivot SET NUM_TYPE = %s , NUM_EXISTENCE = %s WHERE num_pivot = %s",(b_type,b_existance, data['num_pivot']))

    cursor.execute(f"UPDATE prolexeme_{data['langue']} SET NUM_FREQUENCY = %s , label_prolexeme = %s ,WIKIPEDIA_LINK=%s WHERE num_prolexeme = %s",(data['notoriete'],data['prolexeme'] ,data['source'], data['num_prolexeme']))
    cursor.close()
    connection.commit()

    return jsonify({'msg':'prolexeme deleted'})

@app.route('/getpivot',methods=['POST'])
@token_required
def getpivot(token):
    data = request.json
    cursor = connection.cursor()
    cursor.execute('''
    SELECT *
    FROM pivot
    LEFT JOIN type ON type.num_type = pivot.num_type
    LEFT JOIN existence ON existence.num_existence = pivot.num_existence
    LEFT JOIN prolexeme_arb ON prolexeme_arb.num_pivot = pivot.num_pivot
    LEFT JOIN prolexeme_fra ON prolexeme_fra.num_pivot = pivot.num_pivot
    LEFT JOIN prolexeme_eng ON prolexeme_eng.num_pivot = pivot.num_pivot
    WHERE pivot.num_pivot = %s
''', (data['numpivot'],))
    res = cursor.fetchone()
    langue=data['langue']
    num_pivot=data['numpivot']

    cursor = connection.cursor()
    cursor.execute(f"select * from pivot , Meronymy , prolexeme_{langue} where Meronymy.`NUM_PIVOT-HOLONYMOUS`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = Meronymy.`NUM_PIVOT-MERONYMOUS`", (data['numpivot'],))
    meronymy = cursor.fetchall()
    if len(meronymy) == 0:
        cursor = connection.cursor()
        cursor.execute(f"select * from pivot , Meronymy , prolexeme_{langue} where Meronymy.`NUM_PIVOT-MERONYMOUS`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = Meronymy.`NUM_PIVOT-HOLONYMOUS`", (data['numpivot'],))
        meronymy = cursor.fetchall()
        if len(meronymy) == 0:
            meronymy=''

    
    cursor = connection.cursor()
    #select * from pivot , synonymy , prolexeme_fra where synonymy.`NUM_PIVOT-SYNONYMOUS`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_fra.num_pivot = synonymy.`NUM_PIVOT-CANONICAL`"
    query = f"SELECT pro.label_prolexeme FROM synonymy as syn , prolexeme_{langue} AS pro WHERE (pro.num_pivot = syn.`NUM_PIVOT-SYNONYMOUS`  and syn.`NUM_PIVOT-CANONICAL`= %s) or (pro.num_pivot = syn.`NUM_PIVOT-CANONICAL` and syn.`NUM_PIVOT-SYNONYMOUS`=  %s) "
    cursor.execute(query, (num_pivot,num_pivot))
    synonym = cursor.fetchall()
    cursor.close()



    cursor = connection.cursor()
    cursor.execute(f"select * from pivot , accessibility , prolexeme_{langue} where accessibility.`NUM_PIVOT-ARGUMENT1`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = accessibility.`NUM_PIVOT-ARGUMENT2`", (data['numpivot'],))
    accessibility = cursor.fetchall()
    if len(accessibility) == 0:
        cursor = connection.cursor()
        cursor.execute(f"select * from pivot , accessibility , prolexeme_{langue} where accessibility.`NUM_PIVOT-ARGUMENT2`= pivot.num_pivot and pivot.num_pivot=%s and prolexeme_{langue}.num_pivot = accessibility.`NUM_PIVOT-ARGUMENT1`", (data['numpivot'],))
        accessibility = cursor.fetchall()
        if len(accessibility) == 0:
            accessibility=''

    return jsonify({'res':res ,'synonym':synonym ,'meronymy':meronymy ,'accessibility':accessibility})



@app.route('/addpivot',methods=['POST'])
@token_required
def addpivot(token):
    data = request.json
    type_id =verify_if_exists('type','FRA_TYPE',data['type'])
    existance_id = verify_if_exists('existence','FRA_EXISTENCE',data['existance'])
    if type_id and existance_id:
        cursor= connection.cursor()
        cursor.execute('insert into pivot (NUM_TYPE,NUM_EXISTENCE) values (%s , %s)',(type_id,existance_id))
        cursor.execute('select max(num_pivot) from pivot')
        max_pivot= cursor.fetchone()
        cursor.close()
        connection.commit()
        return jsonify({'message':f"Vous avez créé un nouveau pivot --- {max_pivot[0]}"})
    
    return jsonify({'message':'Verifiez le type et l existance '})





@app.route('/updatepivot',methods=['POST'])
@token_required
def updatepivot(token):
    data = request.json
    type_id =verify_if_exists('type','FRA_TYPE',data['type'])
    existance_id = verify_if_exists('existence','FRA_EXISTENCE',data['existance'])
    pivot_id = verify_if_exists('pivot','NUM_PIVOT',data['numpivot'])
    if type_id and existance_id and pivot_id:
        cursor= connection.cursor()
        cursor.execute('update pivot set NUM_TYPE=%s ,NUM_EXISTENCE=%s where NUM_PIVOT =%s ',(type_id,existance_id,pivot_id))
        cursor.close()
        connection.commit()
        return jsonify({'message':f"Vous avez modifié un nouveau pivot "})
    
    return jsonify({'message':'Verifiez le type et l existance '})

    
############################################# Relation : 

@app.route('/ajouter',methods=['POST'])
@token_required
def ajouter(token):
    data = request.json
    cursor= connection.cursor()
    if data['synonymy']==True:
        cursor.execute("insert into synonymy (`NUM_PIVOT-CANONICAL`, `NUM_PIVOT-SYNONYMOUS`,`NUM_DIASYSTEM`) values (%s,%s,2)",(data['numpivot'],data['newpivot']))
    if data['meronymy']==True:
        cursor.execute("insert into meronymy (`NUM_PIVOT-HOLONYMOUS`, `NUM_PIVOT-MERONYMOUS`) values (%s,%s)",(data['numpivot'],data['newpivot']))
    if data['accessibility']==True:
        cursor.execute("insert into accessibility (`NUM_PIVOT-ARGUMENT1`, `NUM_PIVOT-ARGUMENT2`,`NUM_SUBJECT_FILE`) values (%s,%s,4)",(data['numpivot'],data['newpivot']))
    cursor.close()
    connection.commit()
    return jsonify({'message':'relation added successfully'})


################################### Alias

@app.route('/getalias',methods=['POST'])
@token_required
def getalias(token):
    cursor = connection.cursor()
    prolexeme=request.json['prolexeme'].lower()
    langue = request.json['langue']
    cursor.execute(f"select * from prolexeme_{langue} , alias_{langue} where prolexeme_{langue}.num_pivot=alias_{langue}.num_pivot and binary lower(prolexeme_{langue}.LABEL_PROLEXEME) = %s" ,(prolexeme,))
    res = cursor.fetchall()
    return jsonify({'res':res})


@app.route('/ajouteralias',methods=['POST'])
@token_required
def ajouteralias(token):
    cursor = connection.cursor()
    prolexeme=request.json['prolexeme']
    langue = request.json['langue']
    cursor.execute(f"select * from prolexeme_{langue}  where prolexeme_{langue}.LABEL_PROLEXEME = %s" ,(prolexeme,))
    prolexeme_details = cursor.fetchone()
    num_pivot = prolexeme_details[2]
    cursor.execute(f'insert into alias_{langue} (LABEL_ALIAS,NUM_PIVOT,NUM_ALIAS_CATEGORY) values (%s,%s,4)',(request.json['alias'],num_pivot))
    cursor.close()
    connection.commit()
    return jsonify({'res':prolexeme_details})

@app.route('/modifieralias',methods=['POST'])
@token_required
def modifieralias(token):
    cursor = connection.cursor()
    langue = request.json['langue']
    cursor.execute(f'update alias_{langue} set LABEL_ALIAS= %s where NUM_alias= %s ',(request.json['alias'],request.json['id_alias']))
    cursor.close()
    connection.commit()
    return jsonify({'res':'update'})

#deletealias

@app.route('/deletealias',methods=['POST'])
@token_required
def deletealias(token):
    cursor = connection.cursor()
    langue = request.json['langue']
    cursor.execute(f'delete from alias_{langue} where NUM_alias= %s ',(request.json['id_alias'],))
    cursor.close()
    connection.commit()
    return jsonify({'res':'alias deleted'})




################################## derive
@app.route('/getderive',methods=['POST'])
@token_required
def getderive(token):
    cursor = connection.cursor()
    prolexeme=request.json['prolexeme'].lower()
    langue = request.json['langue']
    cursor.execute(f"select * from prolexeme_{langue} , derivative_{langue} where prolexeme_{langue}.num_pivot=derivative_{langue}.num_pivot and binary lower(prolexeme_{langue}.LABEL_PROLEXEME) = %s" ,(prolexeme,))
    res = cursor.fetchall()
    return jsonify({'res':res})


@app.route('/ajouterderive',methods=['POST'])
@token_required
def ajouterderive(token):
    cursor = connection.cursor()
    prolexeme=request.json['prolexeme']
    langue = request.json['langue']
    cursor.execute(f"select * from prolexeme_{langue}  where prolexeme_{langue}.LABEL_PROLEXEME = %s" ,(prolexeme,))
    prolexeme_details = cursor.fetchone()
    num_pivot = prolexeme_details[2]
    cursor.execute(f'insert into derivative_{langue} (LABEL_DERIVATIVE,NUM_PIVOT,NUM_DERIVATIVE_CATEGORY) values (%s,%s,4)',(request.json['derive'],num_pivot))
    cursor.close()
    connection.commit()
    return jsonify({'res':prolexeme_details})

@app.route('/modifierderive',methods=['POST'])
@token_required
def modifierderive(token):
    cursor = connection.cursor()
    langue = request.json['langue']
    cursor.execute(f'update derivative_{langue} set LABEL_DERIVATIVE= %s where NUM_DERIVATIVE= %s ',(request.json['derive'],request.json['id_derive']))
    cursor.close()
    connection.commit()
    return jsonify({'res':'update'})

#deletealias

@app.route('/deletederive',methods=['POST'])
@token_required
def deletederive(token):
    cursor = connection.cursor()
    langue = request.json['langue']
    cursor.execute(f'delete from derivative_{langue} where NUM_DERIVATIVE= %s ',(request.json['id_derive'],))
    cursor.close()
    connection.commit()
    return jsonify({'res':'derive deleted'})

if __name__ == '__main__':
    app.run(debug=True)
