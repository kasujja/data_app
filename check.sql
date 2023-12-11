SELECT
                DISTINCT tsnNumber AS 'Transaction ID',
                tsnAmmount AS 'Transaction Amount',
                tsnCommision AS Commision,
                tsnDate AS 'Transaction Date',
                tsnDetails AS 'Transaction Details',
                status AS 'Transaction Status',
                phoneNumber AS 'Phone Number',
                userName AS 'User Name',
                typeName AS 'Transaction Type',
                NULL AS 'Student Name',
                NULL AS 'Card Number'
              FROM
                transactions
                JOIN agent_transactions USING (tsnNumber)
                JOIN parents_transactions USING (tsnNumber)
                JOIN users USING (userId)
                JOIN commision USING (tsnNumber)
                JOIN transaction_type USING (typeId)
                JOIN transaction_status USING (statusId)
              WHERE
                agent_transactions.agentId = 'K84934'
                and tsnDate >= '2023-07-10'
                
              UNION
                
SELECT
                DISTINCT tsnNumber AS 'Transaction ID',
                tsnAmmount AS 'Transaction Amount',
                tsnCommision AS Commision,
                tsnDate AS 'Transaction Date',
                tsnDetails AS 'Transaction Details',
                status AS 'Transaction Status',
                NULL AS 'Phone Number',
                NULL AS 'User Name',
                typeName AS 'Transaction Type',
                CONCAT(firstName, ' ', lastName) AS 'Student Name',
                cardNumber AS 'Card Number'
              FROM
                agent_transactions
                JOIN commision USING (tsnNumber)
                JOIN transactions USING (tsnNumber)
                JOIN transaction_type USING (typeId)
                JOIN transaction_status USING (statusId)
                JOIN student_transactions USING (tsnNumber)
                JOIN students USING (studentId)
                JOIN student_accounts USING (studentId)
                JOIN used_cards USING (cardId)
              WHERE
                agent_transactions.agentId = 'K84934'
                and tsnDate >= '2023-07-10'
               
                UNION
                
SELECT
                DISTINCT tsnNumber AS 'Transaction ID',
                tsnAmmount AS 'Transaction Amount',
                tsnCommision AS Commision,
                tsnDate AS 'Transaction Date',
                tsnDetails AS 'Transaction Details',
                status AS 'Transaction Status',
                NULL AS 'Phone Number',
                NULL AS 'User Name',
                typeName AS 'Transaction Type',
                CONCAT(firstName, ' ', lastName) AS 'Student Name',
                cardNumber AS 'Card Number'
              FROM
                agent_transactions
                JOIN commision USING (tsnNumber)
                JOIN savings_transactions USING (tsnNumber)
                JOIN transaction_type USING (typeId)
                JOIN transaction_status USING (statusId)
                JOIN student_transactions USING (tsnNumber)
                JOIN students USING (studentId)
                JOIN student_accounts USING (studentId)
                JOIN used_cards USING (cardId)
              WHERE
                agent_transactions.agentId = 'K84934' and tsnNumber not in ( SELECT
                    DISTINCT tsnNumber
                  FROM
                    agent_transactions
                    JOIN transactions USING (tsnNumber)
                  WHERE
                    agent_transactions.agentId = 'K84934'
                and tsnDate >= '2023-07-10'



    SELECT
    tsnNumber  'Transaction ID', tsnAmmount  'Transaction Amount',
    tsnCommision  Commision,tsnDate  'Transaction Date',
    tsnDetails  'Transaction Details',status  'Transaction Status',
    phoneNumber  'Phone Number',userName  'User Name',
    typeName  'Transaction Type',CONCAT(firstName, ' ', lastName)  'Student Name',
    cardNumber  'Card Number'
FROM
    transactions
    JOIN agent_transactions USING (tsnNumber)
    JOIN commision USING (tsnNumber)
    JOIN transaction_type USING (typeId)
    JOIN transaction_status USING (statusId)
    LEFT JOIN parents_transactions USING (tsnNumber)
    LEFT JOIN users USING (userId)
    LEFT JOIN student_transactions USING (tsnNumber)
    LEFT JOIN students USING (studentId)
    LEFT JOIN student_accounts USING (studentId)
    LEFT JOIN used_cards USING (cardId)
WHERE
    agent_transactions.agentId = 'K84934'
                and tsnDate >= '2023-07-10'





SELECT
    COUNT(t.tsnNumber) AS transactions,
    COUNT(DISTINCT st.studentId) AS Students,
    FORMAT(SUM(t.tsnAmmount), 0) AS Amount,
    sc.schName AS school,
    COUNT(distinct st.studentId) AS activeStudents,
    format(SUM(CASE WHEN tt.typeName = 'Withdraw' THEN t.tsnAmmount ELSE 0 END),0) AS Withdraw,
    format(SUM(CASE WHEN tt.typeName = 'Send' THEN t.tsnAmmount ELSE 0 END),0) AS Send,
    format(SUM(CASE WHEN tt.typeName = 'Payment' THEN t.tsnAmmount ELSE 0 END),0) AS Payment,
    format(SUM(CASE WHEN tt.typeName = 'Deposit' THEN t.tsnAmmount ELSE 0 END),0) AS Deposit,
    format(SUM(CASE WHEN tt.typeName = 'Card Replacement' THEN t.tsnAmmount ELSE 0 END),0) AS CardReplacement,
    format(SUM(CASE WHEN tt.typeName = 'Card Activation' THEN t.tsnAmmount ELSE 0 END),0) AS CardActivation
FROM
    transactions t
        INNER JOIN student_transactions st ON t.tsnNumber = st.tsnNumber
        INNER JOIN students s ON st.studentId = s.studentId
        INNER JOIN schools sc ON s.schoolId = sc.schoolId
        INNER JOIN transaction_type tt ON t.typeId = tt.typeId
GROUP BY sc.schoolId
ORDER BY transactions DESC, Amount DESC;
select * from schools;

SELECT 
    distinct phoneNumber Parent,
    CONCAT(firstName, ' ', lastName) student,
    classId class, 
    CASE
        WHEN users.pinCode = '00000' THEN 'No App'
        ELSE 'App Installed'
    END AS appStatus ,
    case when tsnNumber is not null then 'Sent' else 'No send' end as transactions
FROM
    users
        INNER JOIN
    students USING (userId)
    left outer join parents_transactions using(userId)
WHERE
    schoolId = 80
ORDER BY classId ASC;




WITH SchoolTransactionData AS (
    SELECT
        s.schoolId,
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
ORDER BY transactions DESC, Amount DESC;


with saving_deposits as (
select sum(tsnAmmount) depo,agentId from agent_transactions inner join savings_transactions using(tsnNumber) where typeId =1 and statusId=1 and month(tsnDate)>6 group by agentId ),
savings_withdraw as (
select sum(tsnAmmount) witd,agentId from agent_transactions inner join savings_transactions using(tsnNumber) where typeId =2 and statusId=1 and month(tsnDate)>6 group by agentId )
select agentId,depo,witd,format((depo-witd),0) saving from saving_deposits full join savings_withdraw using(agentId) order by depo desc;






select studentId from deleted_students;
select userId from user_login;
select userId,count(userId) from user_login group by userId having count(userId)<2;
SELECT 
    studentId, COUNT(studentId)
FROM
    student_accounts
GROUP BY studentId
HAVING COUNT(studentId) > 1;
select tsnNumber,count(tsnNumber) from transactions group by tsnNumber having count(tsnNumber)>1;
select userId from user_login;
select userId,count(userId) from parent_accounts group by userId having count(userId)>1;

select userId,count(userId) from users group by userId having count(userId)>1;
select studentId from students where userId='15c525bc-8d47-4848-8129-518bd5fcaff9';
select * from parent_accounts where userId='22dae9ae-05fd-48c3-85cd-07f0b93eaaed';


select userId,studentId from parent_accounts inner join students using(userId);

select * from parent_accounts;
select * from users;

select * from parent_accounts where userId in (select count(userId) from parent_accounts group by userId having count(userId) >1);
select studentId,count(studentId) from student_accounts group by studentId having count(studentId) >1;

select sa.*,count(sa.cardId) as dup from student_accounts sa group by sa.cardId having count(sa.cardId)>1;

WITH UserCounts AS (
  SELECT userId, COUNT(*) count FROM parent_accounts GROUP BY userId HAVING COUNT(*) > 1
)
SELECT pa.*, concat(firstName,' ',lastName) student,schoolId,date(s.regDate) registered,u.phoneNumber ,uc.count userCount
FROM parent_accounts pa JOIN UserCounts uc using(userId) inner join students s using(userId) inner join users u using(userId) order by registered desc;

select count(studentId) from student_accounts where studentId='39affd7d-861e-4dab-89d8-daeaed202561';

select date(regDate) from users where userId in ('fa513fc2-be8c-4a00-b258-27f7933f1960','cb5e4d04-f2fc-4248-812a-b4bf05a79fdf','724cd1c6-9504-4fde-98b9-9c6510de8a54');

SET SQL_SAFE_UPDATES = 0;

WITH Duplicates AS (
  SELECT userId, 
         ROW_NUMBER() OVER (PARTITION BY userId ORDER BY (SELECT NULL)) AS rn
  FROM parent_accounts
  GROUP BY userId
  HAVING COUNT(userId) > 1
)
select userId FROM parent_accounts
WHERE userId IN (SELECT userId FROM Duplicates WHERE rn > 1);

SELECT userId, 
         ROW_NUMBER() OVER (PARTITION BY userId ORDER BY (SELECT NULL)) AS rn
  FROM parent_accounts
  GROUP BY userId
  HAVING COUNT(userId) > 1;




WITH UserCounts AS (
  SELECT userId, COUNT(*) AS count
  FROM parent_accounts
  GROUP BY userId
  HAVING COUNT(*) > 1
)
SELECT 
  pa.*,
  CONCAT_WS(' ', s.firstName, s.lastName) AS student,
  s.schoolId,
  DATE(s.regDate) AS registered,
  u.phoneNumber,
  uc.count AS userCount
FROM parent_accounts AS pa
JOIN UserCounts AS uc USING (userId)
INNER JOIN students AS s USING (userId)
INNER JOIN users AS u USING (userId)
ORDER BY registered DESC;

select userId, count(userId) from parent_accounts group by userId having count(userId)>1;

DELETE FROM parent_accounts
WHERE (userId, pAccId) NOT IN (
  SELECT userId, MIN(pAccId) 
  FROM parent_accounts 
  GROUP BY userId
);
CREATE TEMPORARY TABLE temp_keep_rows AS
SELECT *
FROM parent_accounts
GROUP BY userId;

DELETE FROM parent_accounts;

INSERT INTO parent_accounts
SELECT pa.*
FROM temp_keep_rows pa;


select count(*) from parent_accounts;
DELETE pa1
FROM parent_accounts pa1
JOIN parent_accounts pa2
  ON pa1.userId = pa2.userId
  AND pa1.pAccId> pa2.pAccId;

select count(*) from temp_keep_rows;


select * from parent_accounts where userId in ('36cccba2-8a04-47a7-aa04-d114d75e729e','1a5e0c6e-447a-4ced-9df0-e477ae044b02','678fd48e-a52d-44cc-b16e-b0414f8e170f');

drop temporary table temp_keep_rows;


