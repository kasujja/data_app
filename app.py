import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.subplots as sp
from plotly.subplots import make_subplots
from datetime import date
import datetime
import numpy as np
from st_aggrid import AgGrid
from collections import OrderedDict, defaultdict
from handler import Students , StudentTransactions,Transactions,Daily, Weekly,Savings,SavingTransactions,Parents,Schools,SavingBalance,ParentTransactions,ParentAccounts,SchoolPerformance
# from student_transactions import StudentTransactions

st.set_page_config(page_title='KAWU',layout='wide')
# Instantiate the required classes
@st.cache_data
def data_loader():
    handlers = {
        'students': Students(),
        'student_transactions': StudentTransactions(),
        'transactions': Transactions(),
        'daily_activity': Daily(),
        'savings': Savings(),
        'saving_transactions': SavingTransactions(),
        'parents': Parents(),
        'schools': Schools(),
        'saving_balance': SavingBalance(),
        'parent_transactions': ParentTransactions(),
        'parent_accounts': ParentAccounts(),
        'school_transactions':SchoolPerformance()
    }

    data = {key: handler.getData() for key, handler in handlers.items()}

    return data
data=data_loader()
students=data['students']
student_transactions=data['student_transactions']
transactions=data['transactions']
daily_activity=data['daily_activity']
savings=data['savings']
saving_transactions=data['saving_transactions']
parents=data['parents']
schools=data['schools']
saving_balance=data['saving_balance']
parent_transactions=data['parent_transactions']
parent_accounts=data['parent_accounts']
school_transactions=data['school_transactions']

#helper functions

def format_currency(value):
    """Format currency values"""
    return 'UGX {:,.0f}'.format(value)

merged = students.merge(student_transactions, on="studentId", how="left")

parent_accounts.rename(columns={'accBalance': 'walletBalance'}, inplace=True)
parent_accounts =( parent_accounts.merge(parents[['userId', 'phoneNumber']], on='userId', how='right')
.merge(students[['firstName', 'lastName', 'schoolId', 'userId', 'accBalance']], on='userId', how='right')
.merge(schools[['schName', 'schoolId']], on='schoolId', how='right'))
parent_accounts.rename(columns={'schName': 'school', 'accBalance': 'cardBalance', 'phoneNumber': 'parent'}, inplace=True)
parent_accounts['student'] = parent_accounts['firstName'] + ' ' + parent_accounts['lastName']
parent_accounts.drop(columns=['userId', 'schoolId', 'firstName', 'lastName'], inplace=True)
parent_accounts = parent_accounts[['parent', 'walletBalance', 'student', 'cardBalance', 'school']].reset_index(drop=True)

# Filter rows where 'walletBalance' is greater than or equal to 10000
parent_accounts = parent_accounts[parent_accounts['walletBalance'] >= 10000].sort_values('walletBalance', ascending=False, inplace=True)

st.sidebar.image('./awu.jpg',caption='')

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9=st.tabs(['OVERSIGHT','STUDENTS','STUDENT TRANSACTIONS','SAVINGS','PARENTS','SCHOOLS','AGENTS','REVENUE','FOOT PRINT'])
#Data wrangling
balance=students['accBalance'].sum()
stud=students['studentId'].nunique()
value=transactions['amount'].sum()
volume=transactions['tsnNumber'].count()
kawu=len(students[students['accBalance']<5000])
depositFilter=transactions[transactions['typeName']=='Deposit']
deposit=depositFilter['amount'].sum()
depositCount=depositFilter['tsnNumber'].count()
depositTicket=deposit/depositCount
active=student_transactions[(student_transactions['typeName']=='Deposit') | (student_transactions['typeName']=='Send')] 
# st.write(active)
active=active['studentId'].nunique()
# st.info(f'Active students{active}')
# st.title('OverAll')
studs=format_currency(stud)        
value=format_currency(value)
deposit=format_currency(deposit)       
depositTicket=format_currency(depositTicket)
# deposit=float(deposit)
cards=student_transactions[student_transactions['typeName']=='Card Activation']
cards_value=cards['amount'].sum()
cards_value=format_currency(cards_value)
send=student_transactions[student_transactions['typeName']=='Send']
send_value=send['amount'].sum()
send_value=format_currency(send_value)

with tab1:    
    metrics=st.container()
    with metrics:
        bal,std,val,vol=st.columns(4)
        balance=format_currency(balance)
        bal.metric('Student Balance',balance)
        std.metric('Cards Sold',cards_value)
        std.info(f'Mobile Money, {send_value}')
        val.metric('Transaction Value',value)
        val.info(f'Deposit Value,{deposit}')
        bal.info(f'Avg Deposit ,{depositTicket}')
        vol.metric('Transaction Volume',volume)
        vol.info(f'Deposit Volume, {depositCount}')
        stds,acv,dor,kaw,loaded=st.columns(5)
        stds.metric('Students',f'{studs}')
        acv.metric('Active Cards',f'{active}')
        dor.metric('Dormant Cards',f'{int(stud)-int(active)}')
        kaw.metric('In Kawu',f'{kawu}')
        loaded.metric('loaded',f'{stud-kawu}',f'{-kawu}')                                        


    st.subheader('Watch Man')
    class WatchMan(Transactions):
        dail=st.date_input("Choose a day", datetime.date(2022, 5, 13))
        
        def showdDailyAct(self):
            da=WatchMan.dail
            dai=merged.query('date==@da')
            return dai
        
    daily=WatchMan()
    dfilt=daily.showdDailyAct()
    # st.write(dfilt)

    daily_value=dfilt['amount'].sum()
    daily_volume=dfilt['tsnNumber'].count()
    sums=dfilt.groupby('typeName').sum()['amount'].sort_values(ascending=False)
    # sums=sums.reset_index()
    typeCounts=dfilt.groupby('typeName').count()['tsnNumber'].sort_values(ascending=False)
    # std=dfilt['studentId'].nunique()
    # st.write(std) 
    watch1,watch2=st.columns(2)
    with watch1:
        daily_value=format_currency(daily_value)
        st.metric('transaction Value',daily_value)
        sums=sums.to_dict()
        # watch1.write(sums)
        for key,value in sums.items():
            value=format_currency(value)
            st.info(f'{key} :: UGX  {value}')
    
    with watch2:
        watch2.metric('transaction Volume',f' {daily_volume}') 
        typeCounts=typeCounts.to_dict()
        for key,value in typeCounts.items():
            st.info(f'{key} ::  {value}')

        # watch2.write(typeCounts)
    # st.write(students)


with tab2:
    # st.sidebar.selectbox('select something',('studenst','parents','agents'))
    studets=st.container()
    with studets:
        st.subheader('STUDENTS')
        gender=students[['studentId','gender','className']].groupby(['gender']).count()
        genderBal=students[['gender','accBalance']].groupby(['gender']).sum(numeric_only=True)
        studClass=students[['studentId','className']].groupby(['className']).count()
        classBal=students[['gender','className','accBalance']].groupby(['className']).sum(numeric_only=True)
        active=len(students[students['accBalance']>0])
        # kawu=students-active
        sex,act=st.columns(2)
        clas,clasN=st.columns(2)
        
        with sex:
            gender=gender.reset_index()
            # st.write(gender)
            genx=px.pie(gender,values='studentId',names='gender',hole=0.5)
            genx.update_layout(title_text='<b>Students Distribution By Gender</b>',
                            height=300,
                            # domain=dict(x=[0.55, 1], y=[0.2, 1]),
                            showlegend=True,
                            
            )
            st.plotly_chart(genx)

        with act:
            genderBal=genderBal.reset_index()
            # st.write(genderBal)
            genb=px.pie(genderBal,values='accBalance',names='gender',hole=0.5)
            genb.update_layout(title_text='<b>Students Balance grouped by Gender</b>',
                            height=300,
                            showlegend=True,
            )
            st.plotly_chart(genb)

        with clas:
            studClass=studClass.reset_index()
            # st.write(studClass)
            cls=px.pie(studClass,values='studentId',names='className',hole=0.5)
            cls.update_layout(title_text='<b>Student Distribution by Class</b>',
                            height=300,
                            showlegend=True,
            )
            st.plotly_chart(cls)
        with clasN:
            classBal=classBal.reset_index()
            # st.write(studClass)
            clb=px.pie(classBal,values='accBalance',names='className',hole=0.5)
            clb.update_layout(title_text='<b>Students Balance by Class</b>',
                            height=300,
                            showlegend=True,
            )
            st.plotly_chart(clb)

        dist,bal=st.columns(2)
        with dist:
            gd=students[['accBalance','gender','className']]
            # gd['stdId']=gd['studentId'].count()
            # st.write(gd)
            gdc=px.histogram(gd, x="className", y="accBalance", color='gender',barmode='group',title='Student Balance by class and gender')
            st.plotly_chart(gdc)
        # with bal:
            
    
with tab3:
    st.title('Transactions')
    class Years():
        yaz=st.multiselect(
            'choose year',
            options=transactions['year'].unique()
        )

        def filter_year(self):
            time=Years.yaz
            filts=transactions.query('year==@time')
            return filts
        
    filter=Years()
    transactions=filter.filter_year()
    trns=st.container()
    with trns:
        # balance=students['accBalance'].sum(numeric_only=True)
        # stud=students['studentId'].nunique()
        yearlyDeposit=transactions[transactions['typeName']=='Deposit']
        yearlySend=transactions[transactions['typeName']=='Send']

        yearlyDeposit=yearlyDeposit['amount'].sum()
        yearlySend=yearlySend['amount'].sum()
        sendPerc=(yearlySend/yearlyDeposit)*100
        trust=yearlyDeposit+yearlySend   
        yearlyDeposit=format_currency(yearlyDeposit)    
        yearlySend=format_currency(yearlySend)
        trust=format_currency(trust) 
        value=transactions['amount'].sum(numeric_only=True)
        volume=transactions['tsnNumber'].count()
        av=value/volume
        

        #building app layout
        metriz=st.container()
        with metriz:
            bal,val,vol,tic=st.columns(4)
            # balance=format_currency(balance)
            # bal.metric('Student Balance',{balance})
            # studs=format_currency(stud)
            # std.metric('Students',f'{studs})
            value=format_currency(value)
            av=format_currency(av)
            val.metric('Transaction Value',value)
            bal.metric('Active Accounts',f'{00000}')
            vol.metric('Transaction Volume',volume)
            tic.metric('Avg Ticket',av)
            bal.info(f'Deposits {yearlyDeposit}')
            val.info(f'Send  {yearlySend}')
            vol.info(f'Trust:  {trust}')
            tic.info(f' {sendPerc} %')

        lin,linn=st.columns(2)
        with linn:

            smnt = px.histogram(transactions, x='month', y='amount', color='typeName', title='Total Monthly Transactions grouped by transaction type ' ,text_auto='.2s'
                )

            smnt.update_layout(
                barmode='group',
                height=500,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )
            # add a pie chart subplot for the transaction type breakdown
            smnt.add_trace(go.Pie(
                labels=transactions['typeName'],
                values=transactions['amount'],
                hole=.4,    
                # marker_colors=['#1a5ba6', '#00BFFF'],
                domain=dict(x=[0.55, 1], y=[0.5, 1]),
                texttemplate='%{percent}<br>%{label}',
            ))
            st.plotly_chart(smnt)

            stns = px.histogram(merged, x='typeName', y='amount', color='gender', title='Transactions types grouped by gender' ,text_auto='.2s'
                )

            stns.update_layout(
                barmode='group',
                height=500,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )
            pie_chart=go.Pie(
                values=merged['amount'],
                labels=merged['gender'],
                hole=.4,
                domain=dict(x=[0.55, 1], y=[0.2, 1]),
                texttemplate='%{percent}<br>%{label}'
                        
            )
            # st.plotly_chart(genx)
            stns.add_trace(pie_chart)
            st.plotly_chart(stns)

            cgtns = px.histogram(merged, x='className', y='amount', color='gender', title='Transactions by gender and class' ,text_auto='.2s'
                )

            cgtns.update_layout(
                barmode='group',
                height=500,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(cgtns)

        
        with lin:
            cumx=px.bar(transactions, x="month", y="amount",title='Total Monthly Transactions')
            cumx.update_layout(
                height=500
            )
            st.plotly_chart(cumx) 
            
            ctns = px.histogram(merged, x='className', y='amount', color='typeName', title='Transactions types grouped by class ' ,text_auto='.2s'
                )

            ctns.update_layout(
                barmode='group',
                height=500,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(ctns)
            
            genc=merged[['className','amount']].groupby(['className']).sum()
            genc=genc.reset_index()
            # st.write(genc)
            genm=px.pie(genc,values='amount',names='className',hole=0.5)
            genm.update_layout(title_text='<b>transactions By className</b>',
                        height=400,
                        # domain=dict(x=[0.55, 1], y=[0.2, 1]),
                        showlegend=True,
                        
            )
            st.plotly_chart(genm)

    genderTns,classTns=st.columns(2)
    # with genderTns:
        

    # with classTns:
    
    #######################################################
    transactions['month2']=transactions['month']
            
    class Monthly(Transactions):
        def __init__(self, transactions, month):
            super().__init__()
            self.transactions=transactions
            self.month = month
        
        def showMonthlyAct(self):
            mntly=st.multiselect("Choose a Month",options=transactions[self.month].unique(), key=f"{self.month}-multiselect")
            mont=transactions.query(f'{self.month}==@mntly')
            return mont

    # create two Monthly objects with different month values
    monthly1 = Monthly(transactions,"month")
    monthly2 = Monthly(transactions,"month2")

    st.title('Monthly Comparison')
    month1, month2 = st.columns(2)

    with month1:
        
        mfilt1 = monthly1.showMonthlyAct()
        st.write(mfilt1['amount'].sum())
        st.write(mfilt1['tsnNumber'].count())
        mfilt1=mfilt1.groupby('typeName').agg({'amount': 'sum', 'tsnNumber': 'count'}).sort_values(by='amount',ascending=False)
        mfilt1=mfilt1.to_dict()
        for key, value in mfilt1.items():
            for k, v in value.items():
                if k == 'tsnNumber':
                    st.info(f'{k}: {v}')
                else:
                    v = format_currency(v)
                    st.info(f'{k}: {v}')
            

    with month2:
        
        mfilt2 = monthly2.showMonthlyAct()
        st.write(mfilt2['amount'].sum())
        st.write(mfilt2['tsnNumber'].count())
        mfilt2=mfilt2.groupby('typeName').agg({'amount': 'sum', 'tsnNumber': 'count'}).sort_values(by='amount',ascending=False)
        mfilt2=mfilt2.to_dict()
        for key, value in mfilt2.items():
            for k,v in value.items():
                v=format_currency(v)
                st.info(f'{k }: : {v}') 
    #######################################################

    week=Weekly()
    weekly=week.getData()


with tab4:
    st.title('Savings')
    
    # st.write(savings)
    saved=savings['savings'].sum()
    savers=savings['accounts'].sum()
    interest=savings['interest'].sum()
    opening_revenue=savers*2000
    saved=format_currency(saved)
    interest=format_currency(interest)
    opening_revenue=format_currency(opening_revenue)
    savedeposit=saving_transactions[saving_transactions['typeId']==1]
    sav=savedeposit['amount'].sum()
    sCounts=savedeposit['counts'].count()
    sav=format_currency(sav)

    metric1,metric2,metric3,metric4,metric5=st.columns(5)
    metric6,metric7=st.columns(2)
    save1,save2=st.columns(2)
    save=go.Figure(go.Bar(x=savings['savings'],y=savings['school'],orientation='h',text=savings['savings'],textposition='inside'))
    save.update_layout(title='Savings Balance per school',xaxis_title='Savings',yaxis_title='Schools')
    savings=savings.sort_values('accounts',ascending=False)
    act=go.Figure(go.Bar(x=savings['accounts'],y=savings['school'],orientation='h',text=savings['accounts'],textposition='inside'))
    act.update_layout(title='Savings Accounts per school',xaxis_title='Saving Accounts',yaxis_title='Schools')

    metric1.metric('Saving Balance',saved)
    metric2.metric('savings Value',sav)
    metric3.metric('saving accounts',f'{savers}')
    metric4.metric('savings Volume',f'{sCounts}')
    metric5.metric('Total Interest',interest)
    metric6.metric('Opening Revenue',opening_revenue)
    
    save1.plotly_chart(save)
    save2.plotly_chart(act)
    # st.write(sav)
    # st.write(saving_transactions)
    cl_savings=saving_transactions.groupby('class').sum()['amount']
    count_savings=saving_transactions.groupby('class').count()['counts']
    leaders=saving_transactions[saving_transactions['typeId']==1]
    leaders=leaders.groupby('student').agg({'amount': 'sum', 'counts': 'count','class':'first','school':'first'})
    leaders=leaders.reset_index().sort_values('amount',ascending=False)
    gnd=saving_transactions.groupby('gender').agg({'amount': 'sum', 'counts': 'count'})
    leader1,leader2=st.columns(2)       

    with leader1:
        st.subheader('School Balance Leader Board')
        class Leader():
            lead=st.multiselect(
                'Choose School',
                options=saving_balance['school'].unique()
            )

            def filter_school(self):
                leads=Leader.lead
                leads=saving_balance.query('school==@leads')
                return leads
            
            def filter_tns(self):
                tleads=Leader.leadc
                tleads=leaders.query('school=@tleads')
                return tleads
    
        leadership=Leader()
        lid=leadership.filter_school()
        # st.write(lid)
        # lid=lid[['student','balance','interest','class']]
        saving_bal=lid['balance'].sum()
        saving_min = lid[lid['balance'] > 0]['balance'].min()
        saving_max=lid['balance'].max()
        saving_acc=lid['student'].count()
        saving_interest=lid['interest'].sum()
        account_opening=saving_acc*2000
        saving_min=format_currency(saving_min)
        saving_max=format_currency(saving_max)
        saving_bal=format_currency(saving_bal)
        saving_interest=format_currency(saving_interest)
        account_opening=format_currency(account_opening)
        # saving_vol=lid['counts'].sum()
        
        # met1,llead=st.columns([2,3])
        
        st.metric('Balance',saving_bal)
        # met2.metric('Volume',f'{saving_vol})
        st.metric('Max',saving_max)
        st.metric('Min',saving_min)
        st.metric('interest',saving_interest)
        st.metric('Account Opening',account_opening)
       
        # st.subheader('General Balance Leader Board')
        # st.write(saving_balance.head(8))
    
    with leader2:
                
        savings_acc,savings_vol=st.columns(2)
        savings_acc.metric('Accounts',f'{saving_acc}')
        # savings_vol.metric('Volume',f'{saving_vol}')
        lid.drop(columns='school',inplace=True)
        lid.reset_index(drop=True, inplace=True)
        st.write(lid.head(10))
        # st.subheader('General Transaction Leader Board')
        # st.write(leaders.head(8))

    l1,l2=st.columns(2)    
    with l1:
        st.subheader('General Balance Leader Board')
        st.write(saving_balance.head(10))
        
    with l2:
        st.subheader('General Transaction Leader Board')
        st.write(leaders)#.head(8))
        
        
        # llead.write(tlid) 
   
    gnd=gnd.reset_index()
    # st.write(gnd)
    gndx=px.pie(gnd,values='amount',names='gender',hole=0.5)
    gndx.update_layout(title_text='<b>Savings Distribution By Gender</b>',
                            height=300,
                            # domain=dict(x=[0.55, 1], y=[0.2, 1]),
                            showlegend=True,            
     )
    save1.plotly_chart(gndx)
    cl_savings=cl_savings.reset_index()
    cl_sav=px.pie(cl_savings,values='amount',names='class',hole=0.5)
    cl_sav.update_layout(title_text='<b>Savings Distribution by Class</b>',
                        height=300,
                        showlegend=True,)
    save2.plotly_chart(cl_sav)
   
    # st.write(cl_savings)

    # st.write(count_savings)

with tab5:
    # st.write(parents)
    # st.write(parent_accounts)
    noApp=parents[parents['pinCode']=='00000']
    app=parents[parents['pinCode']!='00000']
    noApp=noApp['userId'].count()
    app=app['userId'].count()

    # st.info(noApp)
    # st.info(app)

    p1,p2,p3,p4=st.columns(4)
    p1.metric('Without App',f'{noApp}')
    p2.metric('With App',f'{app}')

    st.subheader('parent transactions')

    # st.write(parent_transactions)
    # parent_transactions['amount']=parent_transactions['amount'].astype(int)
    send=parent_transactions['amount'].sum()
    sendCount=parent_transactions['id'].count()
    # st.info(send)
    # st.info(sendCount)

    p3.metric('Deposit Value',send)
    p4.metric('Send Volume',f'{sendCount}')

    dailySend=parent_transactions.groupby('date').agg({'amount': 'sum', 'id': 'count'})
    dailySend=dailySend.reset_index()

    # st.write(dailySend)
    
    userSend=parent_transactions.groupby('userId').agg({'amount': 'sum', 'id': 'count','date':'max'}).sort_values(by='amount',ascending=False)
    userSend=userSend.reset_index()
    user_send_count=userSend['userId'].count()

    # st.write(userSend)

    userSend['date']=pd.to_datetime(userSend['date'])
    active_parents=userSend[(userSend['amount']>=10000) & (userSend['date']>'2023-01-01')]
    active_parents_count=active_parents['userId'].count()
    # st.write(active_parents)
    frozen=active_parents[(active_parents['date']>='2023-01-01') & (active_parents['date']<='2023-04-30')]
    frozen=frozen.merge(parents[['userId','phoneNumber']],on='userId',how='left')
    frozen_count=frozen['userId'].count()
    frozen=frozen.merge(students[['userId','schoolId']],on='userId',how='left')
    frozen=frozen.merge(schools[['schoolId','schName']],on='schoolId',how='left')

    # churn_parents=userSend[userSend['date']<'2023-01-01']
    # churn_parents_details=churn_parents.merge(parents,on="userId", how="left")
    # churn_parents_details=churn_parents_details.merge(students,on='userId',how='left')
    # churn_parents_details=churn_parents_details.fillna('o')
    # churn_parents_details=churn_parents_details[(churn_parents_details['studentId']!='o')&(churn_parents_details['schoolId']!=5)]
    # churn_parents_details=churn_parents_details[['phoneNumber','amount','userName','firstName','lastName','className','schoolId','accBalance','date']]
    # churn_parents_details=churn_parents_details.merge(schools[['schoolId','schName']],on='schoolId',how='left').reset_index()
    # churn_parents_details=churn_parents_details.drop(columns=['index'])
    # churn_parents_count=churn_parents_details['phoneNumber'].nunique()
    # p3.metric("parents' Churn",f"{churn_parents_count}")
    # p3.info(f'frozen:{frozen_count}')

    # frozen_origin=frozen.groupby('schName').count()['userId']
    # churn_parents_details_origin=churn_parents_details.groupby('schName').count()['phoneNumber']
    
    
    # Filter userSend based on the 'date' column
    churn_parents = userSend[userSend['date'] < '2023-01-01']

    # Merge parents and students data into churn_parents
    churn_parents_details = churn_parents.merge(parents, on="userId", how="left")
    churn_parents_details = churn_parents_details.merge(students, on='userId', how='left')

    # Fill NaN values with appropriate defaults
    churn_parents_details = churn_parents_details.fillna('NA')

    # Filter out rows where 'studentId' is 'NA' or 'schoolId' is 5
    churn_parents_details = churn_parents_details[(churn_parents_details['studentId'] != 'NA') & (churn_parents_details['schoolId'] != 5)]

    # Select the required columns
    churn_parents_details = churn_parents_details[['phoneNumber', 'amount', 'userName', 'firstName', 'lastName', 'className', 'schoolId', 'accBalance', 'date']]

    # Merge with the 'schools' dataframe to include school names
    churn_parents_details = churn_parents_details.merge(schools[['schoolId', 'schName']], on='schoolId', how='left')

    # Count unique phone numbers
    churn_parents_count = churn_parents_details['phoneNumber'].nunique()

    # Use p3 to display the metric and info
    p3.metric("Parents' Churn", f"{churn_parents_count}")
    p3.info(f'Frozen: {frozen_count}')

    # Group and count data by 'schName' in both 'frozen' and 'churn_parents_details'
    frozen_origin = frozen['userId'].groupby(frozen['schName']).count()
    churn_parents_details_origin = churn_parents_details['phoneNumber'].groupby(churn_parents_details['schName']).count()


    pmf=active_parents[(active_parents['id']>=10)&(active_parents['amount']>=50000)]
    pmf_value=pmf['amount'].sum()
    pmf_count=pmf['userId'].count()
    pmf=pmf.merge(parents[['userId','phoneNumber']],on='userId',how='left')
    # pmf=pmf.merge(schools[['schoolId','schName']],on='schoolId',how='left')
    p1.metric('Current Active Parents',f'{int(active_parents_count)-int(frozen_count)}')
    p1.info(f'actives { active_parents_count}')
    p1.info(user_send_count)
    p2.metric('PMF',f'{pmf_count}')
    p2.info(pmf_value)

    # st.write(active_parents)

    week=Weekly()
    weekly=week.getData()

    daily_send,weekly_send,monthly_send=st.tabs(['DAILY','WEEKLY','MONTHLY'])
    with weekly_send:
        st.subheader('WEEKLY')

        # st.write(weekly)

        weekly['Week'] = pd.to_datetime(weekly['Week'].astype(str).str[:4] + '0101', format='%Y%m%d') + pd.to_timedelta((weekly['Week'].astype(str).str[4:].astype(int) - 1) * 7, unit='d')
        weekly['Week'] = weekly['Week'].dt.strftime('%Y-W%U')

        # create bar chart
        bar_chart = go.Bar(x=weekly['Week'], y=weekly['Amount'], name='Amount', marker=dict(color='#1a5ba6'))

        # create line chart
        line_chart = go.Scatter(x=weekly['Week'], y=weekly['Volume'], name='Volume', yaxis='y2', mode='lines+markers', line=dict(color='green'))

        # create layout for charts
        layout = go.Layout(title='Weekly Send Transaction Volume and Amount', xaxis=dict(title='Week',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='Amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        # create figure
        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    with daily_send:
        st.subheader('DAILY')

        # create bar chart
        bar_chart = go.Bar(x=dailySend['date'], y=dailySend['amount'], name='amount', marker=dict(color='#1a5ba6'))

        # create line chart
        line_chart = go.Scatter(x=dailySend['date'], y=dailySend['id'], name='Volume', yaxis='y2', mode='lines', line=dict(color='green'))

        # create layout for charts
        layout = go.Layout(title='Daily Send Transaction Volume and Amount', xaxis=dict(title='Date',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        # create figure
        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(
            plot_bgcolor='white',
            autosize=False,  # Disable autosize
            width=1000,  # Set the width
            height=500  # Set the height                          
                        )
        # Create an empty frame for the animation
        # Set up animation frames
        frames = [go.Frame(data=[go.Bar(x=dailySend['date'][:i+1], y=dailySend['amount'][:i+1])]) for i in range(len(dailySend))]
        # fram = [go.Frame(data=[go.Scatter(x=dailySend['date'][:i+1], y=dailySend['id'][:i+1])]) for i in range(len(dailySend))]

        # Add frames to figure
        fig.frames = frames
        # fig.frames = fram
        # Set animation options
        animation_options = dict(frame=dict(duration=400, redraw=True), fromcurrent=True)

        # Animate the figure
        fig.update_layout(updatemenus=[dict(type='buttons', buttons=[dict(label='Play', method='animate', args=[None, animation_options])])])

        # Render the animated chart using Streamlit
        st.plotly_chart(fig)

        # st.plotly_chart(fig)

    with monthly_send:
        # st.write(parent_transactions)  
        monthly_send=parent_transactions.groupby(['month','years']).agg({'amount':'sum','id':'count'}).reset_index().sort_values(by='month',ascending=True)
      
        # st.write(monthly_send)
        class SendYears():
            send_yaz=st.selectbox(
                'choose year',
                options=monthly_send['years'].unique()
            )

            def filter_years(self):
                time=SendYears.send_yaz
                ptrans=monthly_send.query('years==@time')
                return ptrans
        
        filter=SendYears()
        monthly_send=filter.filter_years()

        st.subheader('MONTHLY')
        monthly_send['month'] = monthly_send['month'] + ' ' + monthly_send['years'].astype(str)

        # Convert the combined 'month' column to a datetime object
        monthly_send['month'] = pd.to_datetime(monthly_send['month'], format='%B %Y')

        # create bar chart
        bar_chart = go.Bar(x=monthly_send['month'], 
                           y=monthly_send['amount'], 
                           name='amount', marker=dict(color='#1a5ba6'))

        # create line chart
        line_chart = go.Scatter(x=monthly_send['month'], 
                                y=monthly_send['id'], 
                                name='Volume', yaxis='y2',
                                mode='lines+markers', 
                                line=dict(color='green'))
        
        xaxis_labels = monthly_send['month'].dt.strftime('%b %Y')
        xaxis = dict(title='Date', tickangle=-90, showgrid=True, gridcolor='lightgray', gridwidth=1, tickvals=monthly_send['month'], ticktext=xaxis_labels)

        # create layout for charts
        layout = go.Layout(title='Monthly Send Transaction Volume and Amount',                             
                            xaxis=xaxis ,                           
                            yaxis=dict(title='amount'), 
                            yaxis2=dict(title='Volume', overlaying='y', side='right'))

        # create figure
        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    st.info('churn parents 2022')
    st.write(churn_parents_details)
    st.write(churn_parents_details_origin.sort_values(ascending=False))

    st.info('Top Parents')
    st.write(pmf)

    st.info('parents churn 2023')
    st.write(frozen)
    st.write(frozen_origin.sort_values(ascending=False))
    st.subheader('Pending Send')
    st.write(parent_accounts)

with tab6:
    schools.rename(columns={'rgnName':'region','dstName':'district','schName':'school'},inplace=True)
    regions = schools.groupby(['region', 'district']).agg({'schCode':'count','school': list}).reset_index()
 # st.title("Schools Count by Region and District")    
    selected_region = st.selectbox("Select Region", regions['region'].unique())
    filtered_df = regions[regions['region'] == selected_region]
    num_districts = len(filtered_df['district'].unique())
    num_schools=filtered_df['schCode'].sum()
    st.write(f"{num_districts} Districts in {selected_region} and {num_schools} Schools")
    selected_district = st.selectbox("Select District", filtered_df['district'].unique())
    result_df = filtered_df[filtered_df['district'] == selected_district]
    st.write(f"{result_df['schCode'].values[0]} schools in {selected_district}")
    selected_school = st.selectbox("Select School", result_df['school'].values[0])

    # Display the list of schCode values for the selected school
    st.write(result_df['school'].values[0])
    st.write(regions)
    # st.write(schools)
    st.write(school_transactions)
    df = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

    st.map(df)
    
    

import pydeck as pdk

# chart_data = pd.DataFrame(
#    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#    columns=['lat', 'lon'])

# st.pydeck_chart(pdk.Deck(
#     map_style=None,
#     initial_view_state=pdk.ViewState(
#         latitude=1.3733, 
#         longitude=32.2903,
#         zoom=11,
#         pitch=50,
#     ),
#     layers=[
#         pdk.Layer(
#            'HexagonLayer',
#            data=chart_data,
#            get_position='[lon, lat]',
#            radius=200,
#            elevation_scale=4,
#            elevation_range=[0, 1000],
#            pickable=True,
#            extruded=True,
#         ),
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=chart_data,
#             get_position='[lon, lat]',
#             get_color='[200, 30, 0, 160]',
#             get_radius=200,
#         ),
#     ],
# ))

 
 
 