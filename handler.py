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
            logging.error(f"Error in Students init method: {e}")

    def getData(self):
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
    
    def getData(self):
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

    def getData(self):
        return self.transactions
    
# class Savings:
#     def __init__(self):
#         try:
#             self.db=Database(DB_URI)
#             self.student_savings='select * from saving_accounts'
#             self.student_savings=pd.read_sql(self.student_savings,self.db.engine)
#         except Exception as e:
#             traceback.print_exc()
#             logging.error("Error in StudentTransactions init method: {}".format(e))

#     def getSavings(self):
#         return self.student_savings
    
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

    def getData(self):
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


    
    def getData(self):
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

    
    def getData(self):
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

    def getData(self):
        return self.saving_balance
    
class Savings:
    def __init__(self):
        try:
            self.db=Database(DB_URI)
            self.savings='''SELECT  SUM(balance) savings,sum(interest) interest, COUNT(studentId) accounts,schName school
                            FROM  savings_accounts INNER JOIN students USING (studentId) NATURAL JOIN
                            schools GROUP BY schoolId ORDER BY savings DESC;'''
            self.savings=pd.read_sql(self.savings,self.db.engine)
        except Exception as e:
            traceback.print_exc()
            logging.error("Error in Savings init method: {}".format(e))
    
    def getData(self):
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
    
    def getData(self):
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
    
    def getData(self):
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
    
    def getData(self):
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
    
    def getData(self):
        return self.schools
    
class SchoolPerformance:
    def __init__(self):
        try:
            self.db = Database(DB_URI)
            self.school_transactions ="""WITH SchoolTransactionData AS (
                                                SELECT
                                                    s.schoolId,
                                                    s.schName school,
                                                    COUNT(t.tsnNumber) AS transactions,
                                                    FORMAT(SUM(t.tsnAmmount), 0) AS Amount,
                                                    format(SUM(CASE WHEN tt.typeName = 'Withdraw' THEN t.tsnAmmount ELSE 0 END),0) AS Withdraw,
                                                    format(SUM(CASE WHEN tt.typeName = 'Send' THEN t.tsnAmmount ELSE 0 END),0) AS Send,
                                                    format(SUM(CASE WHEN tt.typeName = 'Payment' THEN t.tsnAmmount ELSE 0 END),0) AS Payment,
                                                    format(SUM(CASE WHEN tt.typeName = 'Deposit' THEN t.tsnAmmount ELSE 0 END),0) AS Deposit,
                                                    format(SUM(CASE WHEN tt.typeName = 'Card Replacement' THEN t.tsnAmmount ELSE 0 END),0) AS CardReplacement,
                                                    format(SUM(CASE WHEN tt.typeName = 'Card Activation' THEN t.tsnAmmount ELSE 0 END),0) AS CardActivation
                                                FROM
                                                    schools s
                                                    LEFT JOIN students stu ON s.schoolId = stu.schoolId
                                                    LEFT JOIN student_transactions st ON stu.studentId = st.studentId
                                                    LEFT JOIN transactions t ON st.tsnNumber = t.tsnNumber
                                                    LEFT JOIN transaction_type tt ON t.typeId = tt.typeId
                                                WHERE s.schoolId IS NOT NULL
                                                GROUP BY s.schoolId
                                            ),
                                            StudentCounts AS (
                                                SELECT
                                                    s.schoolId,
                                                    COUNT(DISTINCT stu.studentId) AS TotalStudents,
                                                    COUNT(DISTINCT CASE WHEN u.pinCode != '00000' THEN stu.studentId END) AS ActiveStudents
                                                FROM
                                                    schools s
                                                    LEFT JOIN students stu ON s.schoolId = stu.schoolId
                                                    LEFT JOIN users u ON stu.userId = u.userId
                                                WHERE s.schoolId IS NOT NULL
                                                GROUP BY s.schoolId
                                            ),
                                            ParentCounts AS (
                                                SELECT
                                                    s.schoolId,
                                                    COUNT(DISTINCT CASE WHEN u.pinCode != '00000' THEN u.userId END) AS ParentApps
                                                FROM
                                                    schools s
                                                    LEFT JOIN students stu ON s.schoolId = stu.schoolId
                                                    LEFT JOIN users u ON stu.userId = u.userId
                                                WHERE s.schoolId IS NOT NULL
                                                GROUP BY s.schoolId
                                            )
                                            SELECT
                                                std.schoolId,
                                                school,
                                                transactions,
                                                Amount,
                                                Withdraw,
                                                Send,
                                                Payment,
                                                Deposit,
                                                CardReplacement,
                                                CardActivation,
                                                TotalStudents,
                                                ActiveStudents,
                                                ParentApps
                                            FROM SchoolTransactionData std
                                            LEFT JOIN StudentCounts sc ON std.schoolId = sc.schoolId
                                            LEFT JOIN ParentCounts pc ON std.schoolId = pc.schoolId
                                            ORDER BY transactions DESC, Amount DESC;"""
                                                                        
            self.school_transactions=pd.read_sql(self.school_transactions,self.db.engine)
        except Exception as e:
            logging.error(f'Error in school Performance init method:{e}')
            traceback.print_exc()
    
    def getData(self):
        return self.school_transactions
    
# SELECT 
#     FORMAT(mainAcc.main, 2) CardBalance,
#     FORMAT(saved.saving, 2) Savings,
#     FORMAT(MoMo.momo, 2) SchoolMoMo,
#     mainAcc.school
# FROM
#     (SELECT 
#         SUM(accBalance) main, schName school
#     FROM
#         student_accounts
#     JOIN students USING (studentId)
#     JOIN schools USING (schoolId)
#     GROUP BY schoolId) mainAcc
#         JOIN
#     (SELECT 
#         SUM(balance) saving, schName school
#     FROM
#         savings_accounts
#     JOIN students USING (studentId)
#     JOIN schools USING (schoolId)
#     GROUP BY schoolId) saved ON mainAcc.school = saved.school
#         JOIN
#     (SELECT 
#         balance momo, schName school
#     FROM
#         school_momo_accounts
#     JOIN schools USING (schoolId)) MoMo ON mainAcc.school = MoMo.school
# ORDER BY mainAcc.main DESC;

# select studentId, count(studentId) from student_accounts group by studentId having count(studentId)>1

# SELECT                                                                 
#     studentId, COUNT(studentId)
# FROM
#     student_accounts
# GROUP BY studentId
# HAVING COUNT(studentId) > 1;






