from core.controllers.notification.notifyService import notify
from core.controllers.auth.authService import auth
from core.schemas.models import Transactions, User
from fastapi import APIRouter, HTTPException

from datetime import datetime

import sqlite3
import random

router = APIRouter()

@router.post("/userValidate")
async def create_user(user: User):
    user_data = {
        "document": user.document, 
        "email": user.email,
    }
        
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM WALLETS WHERE CPF=? OR EMAIL=?', (user_data["document"],
                                                                        user_data["email"]))
        userValidate = cursor.fetchall()
        
        if userValidate:
            raise HTTPException(status_code=400 , detail="User already exists.")

@router.post("/transaction")
async def transaction(transactions: Transactions):
    transactions_data = {
        "payer": transactions.payer, 
        "payee": transactions.payee, 
        "value": transactions.value
    }

    with sqlite3.connect("database.db") as conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM WALLETS WHERE ID=?', (transactions_data["payer"],))
            payerInformation = cursor.fetchone()
            payerBalance = payerInformation[-1]
            payerType = payerInformation[-2]
        except:
            raise HTTPException(status_code=404, detail="Paying user not found.")
            
        if float(payerBalance) < abs(float(transactions_data["value"])):
            raise  HTTPException(status_code=400, detail="Insufficient balance to make the transaction.")
        
        elif transactions_data["value"]  > float(payerBalance):
            raise  HTTPException(status_code=400, detail="The value of the transaction is greater than the balance.")

        elif transactions_data['payer'] == transactions_data['payee']:
            raise  HTTPException(status_code=400, detail="It is not possible to make a transaction to the payer itself.")

        elif payerType == 2:
            raise HTTPException(status_code=400, detail="Shopkeepers cannot make transfers.")

        else:
            generateId = ''.join(str(random.randint(0, 9)) for i in range(16))

            if auth.authenticate() == False:
                raise HTTPException(status_code=401, detail={
                    'authService': 'Unauthorized transaction',
                    'transaction': {
                        "date": datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
                        "value": str(transactions_data['value']),
                        "payer": transactions_data['payer'],
                        "payee": transactions_data['payee'],
                    }
                })
                
            elif notify.authenticate() == True:
                newPayerBalance = float(payerBalance) - float(transactions_data["value"])
            
                cursor.execute('UPDATE WALLETS SET BALANCE=BALANCE+? WHERE ID=?', (float(transactions_data['value']),
                                                                                   transactions_data['payee'],))

                cursor.execute('UPDATE WALLETS SET BALANCE=? WHERE ID=?', (newPayerBalance, transactions_data['payer']))
                cursor.execute('INSERT INTO TRANSACTIONS VALUES (?, ?, ?, ?, ?)',  
                            (generateId,
                            transactions_data['payer'],
                            transactions_data['payee'],
                            transactions_data['value'],
                            datetime.now().strftime('%d/%m/%Y, %H:%M:%S')))
                
                conn.commit()
                
                return {
                    'authService': 'Transaction approved!',
                    'notifyService': 'Notification sent!',
                    'transaction': {
                        "id": generateId,
                        "date": datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
                        "value": str(transactions_data['value']),
                        "payer": transactions_data['payer'],
                        "payee": transactions_data['payee'],
                    }
                }
                    
            else:
                raise HTTPException(status_code=401, detail={
                    'notifyService': 'Unauthorized notification',
                    'transaction': {
                        "date": datetime.now().strftime('%d/%m/%Y, %H:%M:%S'),
                        "value": str(transactions_data['value']),
                        "payer": transactions_data['payer'],
                        "payee": transactions_data['payee'],
                    }
                })
                
@router.get("/historyTransaction")
async def transaction():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TRANSACTIONS')
        
        history = cursor.fetchall()
        
        columnNames = ["id", "payer", "payee", "value", "timestamp"]
        json_data = []

        for row in history:
            row_dict = {}
            for i, value in enumerate(row):
                row_dict[columnNames[i]] = value
            json_data.append(row_dict)

        
        return json_data