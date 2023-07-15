from db import Database
import pandas as pd
import traceback
import logging
from config import DB_URI

class Handles:
    def __init__(self):
        self.db = Database(DB_URI)
        self.acc="SET sql_mode=(select replace(@@sql_mode,'ONLY_FULL_GROUP_BY',''))"
        self.db.engine.execute(self.acc)
        

class Students:
    def __init__(self):
        try:
            self.db = Database(DB_URI)
            self.students = '''select studentId, date(regDate) regDate, firstName, lastName, gender, userId,
                                     schoolId, className, accBalance from students inner join student_accounts 
                                     using(studentId) inner join classes using(classId)'''
            self.students = pd.read_sql(self.students, self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in Students init method: {}".format(e))

    def getStudents(self):
        return self.students

class Transactions:
    def __init__(self):
        try:
            self.db = Database(DB_URI)
            self.students_transactions='''select tsnNumber, tsnAmmount amount, monthname(tsnDate) month,
                                          year(tsnDate) year,date(tsnDate)date, typeName from transactions inner
                                          join transaction_type using(typeId);'''
            self.students_transactions=pd.read_sql(self.students_transactions,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in Students init method: {}".format(e))
    
    def getTransactions(self):
        return self.students_transactions

    
class StudentTransactions:
    def __init__(self):
        try:
            self.db = Database(DB_URI)
            self.transactions_query = '''select tsnNumber, tsnAmmount amount, date(tsnDate)date, typeName,studentId
                                         from transactions full join student_transactions using(tsnNumber) 
                                         natural join transaction_type '''
            self.transactions = pd.read_sql(self.transactions_query, self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in StudentTransactions init method: {}".format(e))

    def getStudentTransactions(self):
        return self.transactions
    
class Savings:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.student_savings='select * from saving_accounts'
            self.student_savings=pd.read_sql(self.student_savings,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in StudentTransactions init method: {}".format(e))

    def getSavings(self):
        return self.student_savings
    
class Daily:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.daily_activity='''select sum(tsnAmmount) amount,count(tsnNumber) counts,
                                    max(tsnAmmount)max,min(tsnAmmount)min,typeName from transactions natural join 
                                    transaction_type where date(tsnDate)=curdate()-1 group by typeId;'''
            self.daily_activity=pd.read_sql(self.daily_activity,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in daily_activity init method: {}".format(e))

    def getActivity(self):
        return self.daily_activity
    

class Weekly:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.weekly_activity='''SELECT COUNT(tsnNumber) Volume,SUM(tsnAmmount) Amount,YEARWEEK(tsnDate) Week
                                    FROM transactions INNER JOIN parents_transactions USING (tsnNumber) WHERE
                                    typeId=3 and  tsnDate > "2022-05-12" GROUP BY YEARWEEK(tsnDate);'''
            self.weekly_activity=pd.read_sql(self.weekly_activity,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in weekly_activity init method:{}".format(e))


            # select count(tsnNumber) Volume,sum(tsnAmmount) Amount,yearweek(tsnDate)
            # Week from transactions inner join parents_transactions
            # using (tsnNumber) where  typeId=3 and tsnDate>"2022-05-01" group by yearweek(tsnDate);'


    
    def getWeekly(self):
        return self.weekly_activity

    
class SavingTransactions:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.saving_transactions='''select students.studentId,savings_transactions.tsnNumber counts,tsnDetails,tsnDate,
                                        tsnAmmount amount,typeId,concat(firstName," ",lastName) student,gender,className class,
                                        schName school from savings_transactions natural join student_transactions left join 
                                        students using(studentId) natural join classes natural join schools;'''
            self.saving_transactions=pd.read_sql(self.saving_transactions,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in SavingTransactions init method: {}".format(e))

    
    def getSavingTsn(self):
        return self.saving_transactions           

class SavingBalance:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.saving_balance='''SELECT CONCAT(firstName, ' ', lastName) student,balance,interest, schName school,
                                    className class FROM savings_accounts INNER JOIN students USING (studentId) NATURAL
                                    JOIN schools LEFT JOIN classes USING (classId) ORDER BY balance DESC;'''
            self.saving_balance=pd.read_sql(self.saving_balance,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in SavingBalance init method: {}".format(e))

    def getSavingBalance(self):
        return self.saving_balance
    
class Savings:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.savings='''SELECT  SUM(balance) savings, COUNT(studentId) accounts,schName school
                            FROM  savings_accounts INNER JOIN students USING (studentId) NATURAL JOIN
                            schools GROUP BY schoolId ORDER BY savings DESC;'''
            self.savings=pd.read_sql(self.savings,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in Savings init method: {}".format(e))
    
    def getSavings(self):
        return self.savings
    


class Parents:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.parents='''select userId,regDate,phoneNumber,lastLogin,pinCode,userName from users;'''
                                # natural join schools inner join districts using(dstId);'''
            self.parents=pd.read_sql(self.parents,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error('Error in parents init method:{}'.format(e))
    
    def getParents(self):
        return self.parents
    
class ParentAccounts:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.parent_accounts='''select userId,accBalance from parent_accounts;'''
            self.parent_accounts=pd.read_sql(self.parent_accounts,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error('Error in p_acount init method:{}'.format(e))
    
    def getParentAccounts(self):
        return self.parent_accounts
    
class ParentTransactions:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.parent_transactions='''select tsnNumber id,tsnAmmount amount,date(tsnDate) date,monthname(tsndate) month,year(tsnDate) years, hour(tsnDate) hour,userId from transactions inner join 
                                            parents_transactions using(tsnNumber) where date(tsnDate)>'2022-05-12' and statusId=1 and typeId=3;'''
            self.parent_transactions=pd.read_sql(self.parent_transactions,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error('Error in parent transactions init method{}'.format(e))
    
    def getParent_transactions(self):
        return self.parent_transactions

class Schools:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.schools='''select schoolId,schCode,schName,dstName,rgnName from schools 
                            natural join districts natural join regions'''
            self.schools=pd.read_sql(self.schools,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error('Error in schools init method:{}'.format(e))
    
    def getSchools(self):
        return self.schools
    

    



