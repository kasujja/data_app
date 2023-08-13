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
