import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.offline as pyo
import plotly.subplots as sp
from plotly.subplots import make_subplots
from datetime import date
import datetime
from handler import Students , StudentTransactions,Transactions,Daily, Weekly,Savings,SavingTransactions,Parents,Schools,SavingBalance,ParentTransactions
# from student_transactions import StudentTransactions

st.set_page_config(page_title='KAWU',layout='wide')
# Create instances of the Students and StudentTransactions classes
student = Students()
student_transactions = StudentTransactions()
transactions=Transactions()
daily=Daily()
savings=Savings()
saving_trans=SavingTransactions()
user=Parents()
school=Schools()
schools=school.getSchools()
parent_transaction=ParentTransactions()
saved_balance=SavingBalance()

# Get the data from the classes
students = student.getStudents()
student_trans_data = student_transactions.getStudentTransactions()
trans_data=transactions.getTransactions()
daily_activity_data=daily.getActivity()
savings_data=savings.getSavings()
saving_tsn=saving_trans.getSavingTsn()
users=user.getParents()
saved_bal=saved_balance.getSavingBalance()
ptrans=parent_transaction.getParent_transactions()

merged_data = students.merge(student_trans_data, on="studentId", how="left")


from collections import OrderedDict, defaultdict
st.sidebar.image('./awu.jpg',caption='')

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9=st.tabs(['OVERSIGHT','STUDENTS','STUDENT TRANSACTIONS','SAVINGS','PARENTS','SCHOOLS','AGENTS','REVENUE','FOOT PRINT'])

with tab1:
    # st.write(dad)

    ## DataFrame mergers
    # 1. Merge the data on studentId column

    # st.write(merged_data)

    #Data wrangling
    balance=students['accBalance'].sum()
    stud=students['studentId'].nunique()
    value=trans_data['amount'].sum()
    volume=trans_data['tsnNumber'].count()
    kawu=len(students[students['accBalance']<5000])

    depositFilter=trans_data[trans_data['typeName']=='Deposit']
    deposit=depositFilter['amount'].sum()
    depositCount=depositFilter['tsnNumber'].count()
    depositTicket=deposit/depositCount
    #active students
    active=student_trans_data[(student_trans_data['typeName']=='Deposit') | (student_trans_data['typeName']=='Send')] 
    # st.write(active)
    active=active['studentId'].nunique()
    # st.info(f'Active students{active}')
    st.title('OverAll')
    #building app layout
    metrics=st.container()
    with metrics:
        bal,std,val,vol=st.columns(4)
        balance='{:,.0f}'.format(balance)
        bal.metric('Student Balance',f'UGX {balance}')
        studs='{:,.0f}'.format(stud)
        
        value='{:,.0f}'.format(value)
        deposit='{:,.0f}'.format(deposit)
        depositCount='{:,.0f}'.format(depositCount)
        depositTicket='{:,.0f}'.format(depositTicket)
        # deposit=float(deposit)
        cards=student_trans_data[student_trans_data['typeName']=='Card Activation']
        cards_value=cards['amount'].sum()
        cards_value='{:,.0f}'.format(cards_value)
        volume='{:,.0f}'.format(volume)

        send=student_trans_data[student_trans_data['typeName']=='Send']
        send_value=send['amount'].sum()
        send_value='{:,.0f}'.format(send_value)

        std.metric('Cards Sold',f'UGX {cards_value}')
        std.info(f'Mobile Money: UGX {send_value}')
        val.metric('Transaction Value',f'UGX {value}')
        val.info(f'Deposit Value: UGX {deposit}')
        bal.info(f'Avg Deposit : UGX {depositTicket}')
        vol.metric('Transaction Volume',f'{volume}')
        vol.info(f'Deposit Volume: {depositCount}')
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
            dai=merged_data.query('date==@da')
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
        daily_value='{:,.0f}'.format(daily_value)
        st.metric('transaction Value',f'UGX {daily_value}')
        sums=sums.to_dict()
        # watch1.write(sums)
        for key,value in sums.items():
            value='{:,.0f}'.format(value)
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
        with bal:
            cl=students[['gender','className','accBalance']]
            clb=px.histogram(cl, x="gender", y="accBalance", color='className',barmode='group',title='Student Balance grouped by Gender and Class')
            st.plotly_chart(clb)

    
with tab3:
    st.title('Transactions')
    class Years():
        yaz=st.multiselect(
            'choose year',
            options=trans_data['year'].unique()
        )

        def filter_year(self):
            time=Years.yaz
            filts=trans_data.query('year==@time')
            return filts
        
    filter=Years()
    trans_data=filter.filter_year()
    trns=st.container()
    with trns:
        # balance=students['accBalance'].sum(numeric_only=True)
        # stud=students['studentId'].nunique()
        yearlyDeposit=trans_data[trans_data['typeName']=='Deposit']
        yearlySend=trans_data[trans_data['typeName']=='Send']

        yearlyDeposit=yearlyDeposit['amount'].sum()
        yearlySend=yearlySend['amount'].sum()

        sendPerc=(yearlySend/yearlyDeposit)*100
        trust=yearlyDeposit+yearlySend
        


        yearlyDeposit='{:,.0f}'.format(yearlyDeposit)    
        yearlySend='{:,.0f}'.format(yearlySend)
        sendPerc='{:,.0f}'.format(sendPerc)
        trust='{:,.0f}'.format(trust)

        value=trans_data['amount'].sum(numeric_only=True)
        volume=trans_data['tsnNumber'].count()
        av=value/volume
        

        #building app layout
        metriz=st.container()
        with metriz:
            bal,val,vol,tic=st.columns(4)
            # balance='{:,.0f}'.format(balance)
            # bal.metric('Student Balance',f'UGX {balance}')
            # studs='{:,.0f}'.format(stud)
            # std.metric('Students',f'{studs}')
            value='{:,.0f}'.format(value)
            volume='{:,.0f}'.format(volume)
            av='{:,.0f}'.format(av)
            val.metric('Transaction Value',f'UGX {value}')
            bal.metric('Active Accounts',f'{00000}')
            vol.metric('Transaction Volume',f'{volume}')
            tic.metric('Avg Ticket',f'UGX {av}')
            bal.info(f'deposits UGX {yearlyDeposit}')
            val.info(f'Send UGX {yearlySend}')
            vol.info(f'trust: UGX {trust}')
            tic.info(f' {sendPerc} %')

        lin,linn=st.columns(2)

        tns=px.pie(trans_data,values='amount',names='typeName',hole=.5)
        tns.update_layout(title_text='<b>Transactions Grouped By Type</b>',
                            height=500,
                            showlegend=True,
            )
        st.plotly_chart(tns)

        with linn:

            ln=px.histogram(trans_data, x="month", y="amount", color='typeName',barmode='group')#,animation_frame='date',animation_group='typeName')
            st.plotly_chart(ln)

            stns = px.histogram(merged_data, x='typeName', y='amount', color='gender', title='Transactions types grouped by gender' ,text_auto='.2s'
                )

            stns.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(stns)


            ctns = px.histogram(merged_data, x='typeName', y='amount', color='className', title='Transactions types grouped by class' ,text_auto='.2s'
                )

            ctns.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(ctns)

            cgtns = px.histogram(merged_data, x='className', y='amount', color='gender', title='Transactions by gender and class' ,text_auto='.2s'
                )

            cgtns.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(cgtns)

        
        with lin:

            trans_data['cum']=trans_data['amount'].cumsum()
            cumx=px.histogram(trans_data, x="month", y="cum", color='typeName',barmode='group')
            st.plotly_chart(cumx)



            stns = px.histogram(merged_data, x='gender', y='amount', color='typeName', title='Total Monthly Transactions ' ,text_auto='.2s'
                )

            stns.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(stns)


            ctns = px.histogram(merged_data, x='className', y='amount', color='typeName', title='Transactions types grouped by class ' ,text_auto='.2s'
                )

            ctns.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )

            st.plotly_chart(ctns)

            smnt = px.histogram(trans_data, x='month', y='amount', color='typeName', title='Total Monthly Transactions ' ,text_auto='.2s'
                )

            smnt.update_layout(
                barmode='group',
                height=600,
                plot_bgcolor='#f2f2f2',
                legend=dict(title='Transaction Type'),
                # xaxis_tickangle=0,
                yaxis=dict(title='Transaction Amount'),
                yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
            )
            # add a pie chart subplot for the transaction type breakdown
            smnt.add_trace(go.Pie(
                labels=trans_data['typeName'],
                values=trans_data['amount'],
                hole=.4,    
                # marker_colors=['#1a5ba6', '#00BFFF'],
                domain=dict(x=[0.55, 1], y=[0.5, 1]),
                texttemplate='%{percent}<br>%{label}',
            ))
            # trans_data['Number']=trans_data.groupby('month')
            # smnt.add_trace(go.Pie(
            #     labels=trans_data['typeName'],
            #     values=trans_data['tsnNumber'],
            #     hole=.4,
            #     title='Transaction Type Value',
            #     # marker_colors=['#1a5ba6', '#00BFFF'],
            #     domain=dict(x=[0, 0.3], y=[0.5, 1]),
            #     textfont=dict(size=12),
            #     texttemplate='%{percent}<br>%{label}',
            # ))
            st.plotly_chart(smnt)

    genderTns,classTns=st.columns(2)
    with genderTns:
        gend=merged_data[['studentId','gender','className','amount']].groupby(['gender']).count()
        gend=gend.reset_index()
        # st.write(gender)
        genx=px.pie(gend,values='studentId',names='gender',hole=0.5)
        genx.update_layout(title_text='<b>transactions By Gender</b>',
                        height=400,
                        # domain=dict(x=[0.55, 1], y=[0.2, 1]),
                        showlegend=True,
                        
        )
        st.plotly_chart(genx)

    with classTns:
        genc=merged_data[['className','amount']].groupby(['className']).sum()
        genc=genc.reset_index()
        # st.write(genc)
        genm=px.pie(genc,values='amount',names='className',hole=0.5)
        genm.update_layout(title_text='<b>transactions By className</b>',
                        height=400,
                        # domain=dict(x=[0.55, 1], y=[0.2, 1]),
                        showlegend=True,
                        
        )
        st.plotly_chart(genm)


    #######################################################
    trans_data['month2']=trans_data['month']
            
    class Monthly(Transactions):
        def __init__(self, trans_data, month):
            super().__init__()
            self.trans_data=trans_data
            self.month = month
        
        def showMonthlyAct(self):
            mntly=st.multiselect("Choose a Month",options=trans_data[self.month].unique(), key=f"{self.month}-multiselect")
            mont=trans_data.query(f'{self.month}==@mntly')
            return mont

    # create two Monthly objects with different month values
    monthly1 = Monthly(trans_data,"month")
    monthly2 = Monthly(trans_data,"month2")

    st.title('Monthly Comparison')
    month1, month2 = st.columns(2)

    with month1:
        
        mfilt1 = monthly1.showMonthlyAct()
        st.write(mfilt1['amount'].sum())
        st.write(mfilt1['tsnNumber'].count())
        mfilt1=mfilt1.groupby('typeName').agg({'amount': 'sum', 'tsnNumber': 'count'}).sort_values(by='amount',ascending=False)
        mfilt1=mfilt1.to_dict()
        for key, value in mfilt1.items():
            # st.info(value)
            for k,v in value.items():
                v='{:,.0f}'.format(v)
                st.info(f'{k }: : UGX {v}')
        

    with month2:
        
        mfilt2 = monthly2.showMonthlyAct()
        st.write(mfilt2['amount'].sum())
        st.write(mfilt2['tsnNumber'].count())
        mfilt2=mfilt2.groupby('typeName').agg({'amount': 'sum', 'tsnNumber': 'count'}).sort_values(by='amount',ascending=False)
        mfilt2=mfilt2.to_dict()
        for key, value in mfilt2.items():
            for k,v in value.items():
                v='{:,.0f}'.format(v)
                st.info(f'{k }: : UGX {v}')
        


    #######################################################

    week=Weekly()
    weekly=week.getWeekly()


with tab4:
    st.title('Savings')
    
    # st.write(savings_data)
    saved=savings_data['savings'].sum()
    savers=savings_data['accounts'].sum()
    saved='{:,.0f}'.format(saved)

    savedeposit=saving_tsn[saving_tsn['typeId']==1]
    sav=savedeposit['amount'].sum()
    sCounts=savedeposit['counts'].count()
    sav='{:,.0f}'.format(sav)

    metric1,metric2,metric3,metric4=st.columns(4)
    save1,save2=st.columns(2)
    save=go.Figure(go.Bar(x=savings_data['savings'],y=savings_data['school'],orientation='h',text=savings_data['savings'],textposition='inside'))
    save.update_layout(title='Savings Balance per school',xaxis_title='Savings',yaxis_title='Schools')
    savings_data=savings_data.sort_values('accounts',ascending=False)
    act=go.Figure(go.Bar(x=savings_data['accounts'],y=savings_data['school'],orientation='h',text=savings_data['accounts'],textposition='inside'))
    act.update_layout(title='Savings Accounts per school',xaxis_title='Saving Accounts',yaxis_title='Schools')

    metric1.metric('Saving Balance',f'UGX {saved}')
    metric2.metric('savings Value',f'UGX {sav}')
    metric3.metric('saving accounts',f'{savers}')
    metric4.metric('savings Volume',f'{sCounts}')
    save1.plotly_chart(save)
    save2.plotly_chart(act)
    # st.write(sav)
    # st.write(saving_tsn)
    cl_savings=saving_tsn.groupby('class').sum()['amount']
    count_savings=saving_tsn.groupby('class').count()['counts']
    leaders=saving_tsn[saving_tsn['typeId']==1]
    leaders=leaders.groupby('student').agg({'amount': 'sum', 'counts': 'count','class':'first','school':'first'})
    leaders=leaders.reset_index().sort_values('amount',ascending=False)
    gnd=saving_tsn.groupby('gender').agg({'amount': 'sum', 'counts': 'count'})
    leader1,leader2=st.columns(2)
    with leader1:
        st.subheader('General Balance Leader Board')
        st.write(saved_bal.head(8))
        st.subheader('General Transaction Leader Board')
        st.write(leaders.head(8))

        
    with leader2:
        st.subheader('School Balance Leader Board')
        class Leader():
            lead=st.multiselect(
                'Choose School',
                options=saved_bal['school'].unique()
            )

            def filter_school(self):
                leads=Leader.lead
                leads=saved_bal.query('school==@leads')
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
        saving_min=lid['balance'].min()
        saving_min='{:,.0f}'.format(saving_min)
        saving_max=lid['balance'].max()
        saving_max='{:,.0f}'.format(saving_max)
        saving_bal='{:,.0f}'.format(saving_bal)
        # saving_vol=lid['counts'].sum()
        saving_acc=lid['student'].count()
        met1,met2,llead=st.columns([2,1,3])
        met1.metric('Balance',f'UGX {saving_bal}')
        # met2.metric('Volume',f'{saving_vol}')
        met1.metric('Min',f'UGX {saving_min}')
        met1.metric('Max',f'UGX {saving_max}')
        met2.metric('Accounts',f'{saving_acc}')
        llead.write(lid.head(5))

        st.subheader('School Balance Leader Board')
        # llead.write(tlid)

    # st.write(saving_tsn)


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
    # st.write(users)
    noApp=users[users['pinCode']=='00000']
    app=users[users['pinCode']!='00000']
    noApp=noApp['userId'].count()
    app=app['userId'].count()

    # st.info(noApp)
    # st.info(app)

    p1,p2,p3,p4=st.columns(4)
    p1.metric('Without App',f'{noApp}')
    p2.metric('With App',f'{app}')

    st.subheader('parent transactions')

    # st.write(ptrans)
    # ptrans['amount']=ptrans['amount'].astype(int)
    send=ptrans['amount'].sum()
    sendCount=ptrans['id'].count()
    # st.info(send)
    # st.info(sendCount)

    p3.metric('Send Value',f'UGX {send}')
    p4.metric('Send Volume',f'{sendCount}')

    dailySend=ptrans.groupby('date').agg({'amount': 'sum', 'id': 'count'})
    dailySend=dailySend.reset_index()

    # st.write(dailySend)
    
    userSend=ptrans.groupby('userId').agg({'amount': 'sum', 'id': 'count','date':'max'}).sort_values(by='amount',ascending=False)
    userSend=userSend.reset_index()
    user_send_count=userSend['userId'].count()

    # st.write(userSend)

    userSend['date']=pd.to_datetime(userSend['date'])
    active_parents=userSend[(userSend['amount']>=10000) & (userSend['date']>'2023-01-01')]
    active_parents_count=active_parents['userId'].count()
    # st.write(active_parents)
    frozen=active_parents[(active_parents['date']>='2023-01-01') & (active_parents['date']<='2023-04-30')]
    frozen=frozen.merge(users[['userId','phoneNumber']],on='userId',how='left')
    frozen_count=frozen['userId'].count()
    
    

    churn_parents=userSend[userSend['date']<'2023-01-01']
    churn_parents_details=churn_parents.merge(users,on="userId", how="left")
    churn_parents_details=churn_parents_details.merge(students,on='userId',how='left')
    churn_parents_details=churn_parents_details.fillna('o')
    churn_parents_details=churn_parents_details[(churn_parents_details['studentId']!='o')&(churn_parents_details['schoolId']!=5)]
    churn_parents_details=churn_parents_details[['phoneNumber','amount','userName','firstName','lastName','className','schoolId','accBalance','date']]
    churn_parents_details=churn_parents_details.merge(schools[['schoolId','schName']],on='schoolId',how='left').reset_index()
    churn_parents_details=churn_parents_details.drop(columns=['schoolId','index'])
    churn_parents_count=churn_parents_details['phoneNumber'].nunique()
    p3.metric("parents' Churn",f"{churn_parents_count}")
    p3.info(f'frozen:{frozen_count}')

    

    pmf=active_parents[(active_parents['id']>=10)&(active_parents['amount']>=50000)]
    pmf_value=pmf['amount'].sum()
    pmf_count=pmf['userId'].count()
    pmf=pmf.merge(users[['userId','phoneNumber']],on='userId',how='left')
    
    
    p1.metric('Current Active Parents',f'{int(active_parents_count)-int(frozen_count)}')
    p1.info(f'actives { active_parents_count}')
    p1.info(user_send_count)
    p2.metric('PMF',f'{pmf_count}')
    p2.info(pmf_value)

    # st.write(active_parents)

    week=Weekly()
    weekly=week.getWeekly()

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
        line_chart = go.Scatter(x=dailySend['date'], y=dailySend['id'], name='Volume', yaxis='y2', mode='lines+markers', line=dict(color='green'))

        # create layout for charts
        layout = go.Layout(title='Daily Send Transaction Volume and Amount', xaxis=dict(title='Date',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        # create figure
        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    with monthly_send:
        # st.write(ptrans)
        
        
        monthly_send=ptrans.groupby(['month','years']).agg({'amount':'sum','id':'count'}).reset_index().sort_values(by='month',ascending=True)
        # st.write(monthly_send)
        class SendYears():
            send_yaz=st.selectbox(
                'choose year',
                options=monthly_send['years'].unique()
            )

            def filter_years(self):
                time=SendYears.send_yaz
                ptrans_data=monthly_send.query('years==@time')
                return ptrans_data
        
        filter=SendYears()
        monthly_send_data=filter.filter_years()

        st.subheader('MONTHLY')

        # create bar chart
        bar_chart = go.Bar(x=monthly_send_data['month'], y=monthly_send_data['amount'], name='amount', marker=dict(color='#1a5ba6'))

        # create line chart
        line_chart = go.Scatter(x=monthly_send_data['month'], y=monthly_send_data['id'], name='Volume', yaxis='y2', mode='lines+markers', line=dict(color='green'))

        # create layout for charts
        layout = go.Layout(title='Monthly Send Transaction Volume and Amount', xaxis=dict(title='Date',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        # create figure
        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    st.info('churn parents 2022')
    st.write(churn_parents_details)

    st.info('Top Parents')
    st.write(pmf)

    st.info('parents churn 2023')
    st.write(frozen)





with tab6:
    st.write(schools)
 