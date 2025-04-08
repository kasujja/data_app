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
from handler import (
    Students, StudentTransactions, Transactions, Daily, Weekly, Savings,
    SavingTransactions, Parents, Schools, SavingBalance, ParentTransactions,
    ParentAccounts, SchoolPerformance
)
import uuid

st.set_page_config(page_title='KAWU', layout='wide')

# Cache the data loading
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
        'school_transactions': SchoolPerformance(),
    }
    return {key: handler.getData() for key, handler in handlers.items()}

# Cache common calculations
@st.cache_data
def calculate_metrics(data):
    metrics = {
        'balance': data['students']['accBalance'].sum(),
        'student_count': data['students']['studentId'].nunique(),
        'transaction_value': data['transactions']['amount'].sum(),
        'transaction_volume': data['transactions']['tsnNumber'].count(),
        'kawu_count': len(data['students'][data['students']['accBalance'] < 5000]),
        'deposit_data': data['transactions'][data['transactions']['typeName'] == 'Deposit'],
    }
    
    metrics['deposit_sum'] = metrics['deposit_data']['amount'].sum()
    metrics['deposit_count'] = metrics['deposit_data']['tsnNumber'].count()
    metrics['deposit_ticket'] = metrics['deposit_sum'] / metrics['deposit_count'] if metrics['deposit_count'] > 0 else 0
    
    return metrics

class YearSelector:
    """Reusable year selection component"""
    def __init__(self, data, year_column='year', key_prefix=''):
        self.data = data
        self.year_column = year_column
        self.key = f"{key_prefix}_year_selector_{uuid.uuid4()}"
        self.years = sorted(data[year_column].unique())
    
    @staticmethod
    @st.cache_data
    def _filter_data(selected_years, data, year_column):
        """Cache the date filtering without using self"""
        if not selected_years:
            return pd.DataFrame()  # Return empty DataFrame if no years selected
        return data[data[year_column].isin(selected_years)].copy()
    
    def select_years(self, default_all=False):
        selected_years = st.multiselect(
            'Select Year(s)',
            options=self.years,
            default=self.years if default_all else None,
            key=self.key
        )
        
        # Debug information
        st.write(f"Selected years: {selected_years}")
        st.write(f"Data shape before filtering: {self.data.shape}")
        
        filtered_data = self._filter_data(selected_years, self.data, self.year_column)
        
        # Debug information
        st.write(f"Data shape after filtering: {filtered_data.shape}")
        
        return filtered_data

# Cache transaction metrics
@st.cache_data
def calculate_transaction_metrics(transactions):
    deposit_filter = transactions[transactions['typeName'] == 'Deposit']
    cards = transactions[transactions['typeName'] == 'Card Activation']
    send = transactions[transactions['typeName'] == 'Send']
    
    metrics = {
        'deposit_sum': deposit_filter['amount'].sum(),
        'deposit_count': deposit_filter['tsnNumber'].count(),
        'cards_value': cards['amount'].sum(),
        'send_value': send['amount'].sum()
    }
    
    metrics['deposit_ticket'] = metrics['deposit_sum'] / metrics['deposit_count'] if metrics['deposit_count'] > 0 else 0
    
    return metrics

# Load data once
data = data_loader()
metrics = calculate_metrics(data)

students = data['students']
student_transactions = data['student_transactions']
transactions = data['transactions']
daily_activity = data['daily_activity']
savings = data['savings']
saving_transactions = data['saving_transactions']
parents = data['parents']
schools = data['schools']
saving_balance = data['saving_balance']
parent_transactions = data['parent_transactions']
parent_accounts = data['parent_accounts']
school_transactions = data['school_transactions']

def format_currency(value):
    """Format currency values"""
    return 'UGX {:,.0f}'.format(value)

# Cache the merged dataframe
@st.cache_data
def get_merged_data(students, student_transactions):
    return students.merge(student_transactions, on="studentId", how="left")

merged = get_merged_data(data['students'], data['student_transactions'])

# Cache parent account processing
@st.cache_data
def process_parent_accounts(parent_accounts, parents, students, schools):
    parent_accounts = parent_accounts.copy()
    parent_accounts.rename(columns={'accBalance': 'walletBalance'}, inplace=True)
    
    parent_accounts = (
        parent_accounts.merge(parents[['userId', 'phoneNumber']], on='userId', how='right')
        .merge(students[['firstName', 'lastName', 'schoolId', 'userId', 'accBalance']], on='userId', how='right')
        .merge(schools[['schName', 'schoolId']], on='schoolId', how='right')
    )
    
    parent_accounts.rename(columns={
        'schName': 'school', 
        'accBalance': 'cardBalance', 
        'phoneNumber': 'parent'
    }, inplace=True)
    
    parent_accounts['student'] = parent_accounts['firstName'] + ' ' + parent_accounts['lastName']
    parent_accounts.drop(columns=['userId', 'schoolId', 'firstName', 'lastName'], inplace=True)
    parent_accounts = parent_accounts[['parent', 'walletBalance', 'student', 'cardBalance', 'school']]
    
    return parent_accounts[parent_accounts['walletBalance'] >= 10000].sort_values('walletBalance', ascending=False)

parent_accounts = process_parent_accounts(data['parent_accounts'], data['parents'], data['students'], data['schools'])

st.sidebar.image('./awu.jpg', caption='')

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    'OVERSIGHT', 'STUDENTS', 'STUDENT TRANSACTIONS', 'SAVINGS', 'PARENTS', 
    'SCHOOLS', 'AGENTS', 'REVENUE', 'FOOT PRINT'
])

# Data wrangling
balance = students['accBalance'].sum()
stud = students['studentId'].nunique()
value = transactions['amount'].sum()
volume = transactions['tsnNumber'].count()
kawu = len(students[students['accBalance'] < 5000])
depositFilter = transactions[transactions['typeName'] == 'Deposit']
deposit = depositFilter['amount'].sum()
depositCount = depositFilter['tsnNumber'].count()
depositTicket = deposit / depositCount if depositCount > 0 else 0
active = student_transactions[(student_transactions['typeName'] == 'Deposit') | (student_transactions['typeName'] == 'Send')]
active = active['studentId'].nunique()

studs = format_currency(stud)        
value = format_currency(value)
deposit = format_currency(deposit)       
depositTicket = format_currency(depositTicket)
cards = transactions[transactions['typeName'] == 'Card Activation']
cards_value = cards['amount'].sum()
cards_value = format_currency(cards_value)
send = transactions[transactions['typeName'] == 'Send']
send_value = send['amount'].sum()
send_value = format_currency(send_value)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_and_process_transactions(transactions):
    """Cache transaction data processing"""
    return {
        'deposit': transactions[transactions['typeName'] == 'Deposit'],
        'send': transactions[transactions['typeName'] == 'Send'],
        'cards': transactions[transactions['typeName'] == 'Card Activation']
    }

@st.cache_data
def process_monthly_data(transactions):
    """Cache monthly aggregations"""
    return transactions.groupby(['month', 'years']).agg({
        'amount': 'sum',
        'id': 'count'
    }).reset_index()

# Modify the Monthly class to use cached data
class Monthly(Transactions):
    def __init__(self, transactions, month):
        super().__init__()
        self.transactions = transactions
        self.month = month
        self._process_dates()
    
    @staticmethod
    @st.cache_data
    def _process_date_data(transactions, month):
        """Cache the date processing without using self"""
        if 'year' in transactions.columns:
            full_date = (transactions[month] + ' ' + 
                        transactions['year'].astype(str))
        else:
            full_date = transactions[month]
        return full_date, full_date.unique()
    
    def _process_dates(self):
        """Process dates using the cached static method"""
        self.transactions['full_date'], self.month_options = self._process_date_data(
            self.transactions, 
            self.month
        )
    
    def showMonthlyAct(self):
        mntly = st.multiselect(
            "Choose a Month", 
            options=self.month_options,
            key=f"{self.month}-multiselect"
        )
        return self.transactions[self.transactions['full_date'].isin(mntly)]

# Cache expensive dataframe operations
@st.cache_data
def get_filtered_transactions(transactions, years):
    """Cache year filtering"""
    if not years:
        return transactions.copy()
    return transactions[transactions['year'].isin(years)].copy()

# Modify the Years class to use cached filtering
class Years:
    def __init__(self, datas):
        self.datas = datas
        self.years = sorted(datas['year'].unique())
        
    def filter_year(self):
        years = st.multiselect(
            'Choose year',
            options=self.years,
            key=f"year_select_{id(self.datas)}"
        )
        return get_filtered_transactions(self.datas, years)

# Ensure 'month2' column is created
transactions['month2'] = transactions['month']

# create two Monthly objects with different month values
monthly1 = Monthly(transactions, "month")
monthly2 = Monthly(transactions, "month2")

with tab1:    
    # Use cached transaction metrics
    trans_metrics = calculate_transaction_metrics(transactions)
    
    metrics_container = st.container()
    with metrics_container:
        bal, std, val, vol = st.columns(4)
        
        # Use pre-calculated metrics
        bal.metric('Student Balance', format_currency(metrics['balance']))
        std.metric('Cards Sold', format_currency(trans_metrics['cards_value']))
        std.info(f'Mobile Money, {format_currency(trans_metrics["send_value"])}')
        val.metric('Transaction Value', format_currency(metrics["transaction_value"]))
        val.info(f'Deposit Value, {format_currency(trans_metrics["deposit_sum"])}')
        bal.info(f'Avg Deposit, {format_currency(trans_metrics["deposit_ticket"])}')
        vol.metric('Transaction Volume', metrics["transaction_volume"])
        vol.info(f'Deposit Volume, {trans_metrics["deposit_count"]}')
        
        stds, acv, dor, kaw, loaded = st.columns(5)
        active_count = len(student_transactions[(student_transactions['typeName'].isin(['Deposit', 'Send'])) & 
                                                 (student_transactions['studentId'].isin(['studentId']).unique())])
        
        stds.metric('Students', format_currency(metrics['student_count']))
        acv.metric('Active Cards', str(active_count))
        dor.metric('Dormant Cards', str(metrics['student_count'] - active_count))
        kaw.metric('In Kawu', str(metrics['kawu_count']))
        loaded.metric('loaded', str(metrics['student_count'] - metrics['kawu_count']), str(-metrics['kawu_count']))

    @st.cache_data
    def prepare_plot_data(transactions, group_by):
        """Cache plot data aggregations"""
        return transactions.groupby(group_by).agg({
            'Amount': 'sum',
            'transactions': 'count'
        }).reset_index()

    st.title('Monthly Comparison')
    month1, month2 = st.columns(2)

    with month1:
        mfilt1 = monthly1.showMonthlyAct()
        if not mfilt1.empty:
            # Create bar chart for transaction types
            fig1 = px.bar(mfilt1, 
                        x='typeName', 
                        y='amount',
                        title='Transaction Types by Amount',
                        text_auto='.2s')
            fig1.update_layout(
                height=400,
                xaxis_title='Transaction Type',
                yaxis_title='Amount (UGX)'
            )
            st.plotly_chart(fig1)

            # Create pie chart for transaction distribution
            fig2 = px.pie(mfilt1, 
                        values='amount', 
                        names='typeName',
                        title='Transaction Distribution',
                        hole=0.4)
            fig2.update_layout(height=400)
            st.plotly_chart(fig2)

            # Display summary metrics
            total_amount = format_currency(mfilt1['amount'].sum())
            total_volume = mfilt1['tsnNumber'].count()
            st.metric("Total Amount", total_amount)
            st.metric("Total Transactions", total_volume)

    with month2:
        mfilt2 = monthly2.showMonthlyAct()
        if not mfilt2.empty:
            # Create bar chart for transaction types
            fig3 = px.bar(mfilt2, 
                        x='typeName', 
                        y='amount',
                        title='Transaction Types by Amount',
                        text_auto='.2s')
            fig3.update_layout(
                height=400,
                xaxis_title='Transaction Type',
                yaxis_title='Amount (UGX)'
            )
            st.plotly_chart(fig3)

            # Create pie chart for transaction distribution
            fig4 = px.pie(mfilt2, 
                        values='amount', 
                        names='typeName',
                        title='Transaction Distribution',
                        hole=0.4)
            fig4.update_layout(height=400)
            st.plotly_chart(fig4)

            # Display summary metrics
            total_amount = format_currency(mfilt2['amount'].sum())
            total_volume = mfilt2['tsnNumber'].count()
            st.metric("Total Amount", total_amount)
            st.metric("Total Transactions", total_volume)

    #######################################################

week = Weekly()
weekly = week.getData()

# Cache student metrics
@st.cache_data
def calculate_student_metrics(students):
    return {
        'gender_dist': students[['studentId', 'gender', 'className']].groupby(['gender']).count(),
        'gender_balance': students[['gender', 'accBalance']].groupby(['gender']).sum(),
        'class_dist': students[['studentId', 'className']].groupby(['className']).count(),
        'class_balance': students[['className', 'accBalance']].groupby(['className']).sum()
    }

with tab2:
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
    st.subheader("Transactions Analysis")
    
    # Ensure the 'date' column is in datetime format
    transactions['date'] = pd.to_datetime(transactions['date'], errors='coerce')

    # Calculate total transactions per day
    daily_totals = transactions.groupby('date')['amount'].sum().reset_index()

    # Calculate total transactions per week
    transactions['week'] = transactions['date'].dt.to_period('W').apply(lambda r: r.start_time)  # Convert date to week period
    weekly_totals = transactions.groupby('week')['amount'].sum().reset_index()

    # Calculate total transactions per month
    transactions['month'] = transactions['date'].dt.to_period('M').apply(lambda r: r.start_time)  # Convert date to month period
    monthly_totals = transactions.groupby('month')['amount'].sum().reset_index()

    # Create tabs for daily, weekly, and monthly charts
    daily_tab, weekly_tab, monthly_tab = st.tabs(['Daily Transactions', 'Weekly Transactions', 'Monthly Transactions'])

    with daily_tab:
        # Create a bar chart for total daily transactions
        daily_bar_chart = px.bar(daily_totals, 
                                  x='date', 
                                  y='amount', 
                                  title='Total Daily Transactions',
                                  text_auto='.2s',
                                #   name='Daily Transactions'  # Set name for legend
                                 )
        daily_bar_chart.update_layout(
            height=500,
            plot_bgcolor='#f2f2f2',
            yaxis=dict(title='Transaction Amount'),
        )

        # Create a line chart for total daily transactions in green
        daily_line_chart = px.line(daily_totals, 
                                    x='date', 
                                    y='amount', 
                                    markers=False,
                                    line_shape='linear',
                                    # name='Daily Trend'  # Set name for legend
                                   )
        daily_line_chart.update_traces(line=dict(color='green'))  # Set line color to green

        # Add the line chart to the bar chart
        daily_bar_chart.add_trace(daily_line_chart.data[0])  # Add the line trace from the line chart

        # Update layout for the combined chart
        daily_bar_chart.update_layout(
            title='Total Daily Transactions',
            yaxis=dict(title='Transaction Amount'),
            legend=dict(title='Select View')  # Add legend title
        )

        # Display the combined chart
        st.plotly_chart(daily_bar_chart)

    with weekly_tab:
        # Create a bar chart for total weekly transactions
        weekly_bar_chart = px.bar(weekly_totals, 
                                   x='week', 
                                   y='amount', 
                                   title='Total Weekly Transactions',
                                   text_auto='.2s'
                                  )
        weekly_bar_chart.update_layout(
            height=500,
            plot_bgcolor='#f2f2f2',
            yaxis=dict(title='Transaction Amount'),
        )
        st.plotly_chart(weekly_bar_chart)

    with monthly_tab:
        # Create a bar chart for total monthly transactions
        monthly_bar_chart = px.bar(monthly_totals, 
                                    x='month', 
                                    y='amount', 
                                    title='Total Monthly Transactions',
                                    text_auto='.2s'
                                   )
        monthly_bar_chart.update_layout(
            height=500,
            plot_bgcolor='#f2f2f2',
            yaxis=dict(title='Transaction Amount'),
        )
        st.plotly_chart(monthly_bar_chart)

with tab4:
    st.title('Savings')
    
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
    cl_savings=saving_transactions.groupby('class').sum()['amount']
    count_savings=saving_transactions.groupby('class').count()['counts']
    leaders=saving_transactions[saving_transactions['typeId'].isin ([1,14,17])]
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
        
        st.metric('Balance',saving_bal)
        st.metric('Max',saving_max)
        st.metric('Min',saving_min)
        st.metric('interest',saving_interest)
        st.metric('Account Opening',account_opening)
       
    with leader2:
                
        savings_acc,savings_vol=st.columns(2)
        savings_acc.metric('Accounts',f'{saving_acc}')
        lid.drop(columns='school',inplace=True)
        lid.reset_index(drop=True, inplace=True)
        st.write(lid)

    l1,l2=st.columns(2)    
    with l1:
        st.subheader('General Balance Leader Board')
        st.write(saving_balance)
        
    with l2:
        st.subheader('General Transaction Leader Board')
        st.write(leaders)

    gnd=gnd.reset_index()
    gndx=px.pie(gnd,values='amount',names='gender',hole=0.5)
    gndx.update_layout(title_text='<b>Savings Distribution By Gender</b>',
                            height=300,
                            showlegend=True,            
     )
    save1.plotly_chart(gndx)
    cl_savings=cl_savings.reset_index()
    cl_sav=px.pie(cl_savings,values='amount',names='class',hole=0.5)
    cl_sav.update_layout(title_text='<b>Savings Distribution by Class</b>',
                        height=300,
                        showlegend=True,)
    save2.plotly_chart(cl_sav)

with tab5:
    noApp=parents[parents['pinCode']=='00000']
    app=parents[parents['pinCode']!='00000']
    noApp=noApp['userId'].count()
    app=app['userId'].count()

    p1,p2,p3,p4=st.columns(4)
    p1.metric('Without App',f'{noApp}')
    p2.metric('With App',f'{app}')

    st.subheader('parent transactions')

    send=parent_transactions['amount'].sum()
    sendCount=parent_transactions['id'].count()

    p3.metric('Deposit Value',send)
    p4.metric('Send Volume',f'{sendCount}')

    dailySend=parent_transactions.groupby('date').agg({'amount': 'sum', 'id': 'count'})
    dailySend=dailySend.reset_index()

    userSend=parent_transactions.groupby('userId').agg({'amount': 'sum', 'id': 'count','date':'max'}).sort_values(by='amount',ascending=False)
    userSend=userSend.reset_index()
    user_send_count=userSend['userId'].count()

    userSend['date']=pd.to_datetime(userSend['date'])
    active_parents=userSend[(userSend['amount']>=10000) & (userSend['date']>'2023-01-01')]
    active_parents_count=active_parents['userId'].count()
    frozen=active_parents[(active_parents['date']>='2023-01-01') & (active_parents['date']<='2023-04-30')]
    frozen=frozen.merge(parents[['userId','phoneNumber']],on='userId',how='left')
    frozen=frozen.merge(students[['userId','schoolId']],on='userId',how='left')
    frozen=frozen.merge(schools[['schoolId','schName']],on='schoolId',how='left')

    churn_parents = userSend[userSend['date'] < '2023-01-01']

    churn_parents_details = churn_parents.merge(parents, on="userId", how="left")
    churn_parents_details = churn_parents_details.merge(students, on='userId', how='left')

    churn_parents_details = churn_parents_details.fillna('NA')

    churn_parents_details = churn_parents_details[(churn_parents_details['studentId'] != 'NA') & (churn_parents_details['schoolId'] != 5)]

    churn_parents_details = churn_parents_details[['phoneNumber', 'amount', 'userName', 'firstName', 'lastName', 'className', 'schoolId', 'accBalance', 'date']]

    churn_parents_details = churn_parents_details.merge(schools[['schoolId', 'schName']], on='schoolId', how='left')

    churn_parents_count = churn_parents_details['phoneNumber'].nunique()

    p3.metric("Parents' Churn", f"{churn_parents_count}")

    frozen_origin = frozen['userId'].groupby(frozen['schName']).count()
    churn_parents_details_origin = churn_parents_details['phoneNumber'].groupby(churn_parents_details['schName']).count()

    pmf=active_parents[(active_parents['id']>=10)&(active_parents['amount']>=50000)]
    pmf_value=pmf['amount'].sum()
    pmf_count=pmf['userId'].count()
    pmf=pmf.merge(parents[['userId','phoneNumber']],on='userId',how='left')
    p1.metric('Current Active Parents',f'{int(active_parents_count)}')
    p1.info(user_send_count)
    p2.metric('PMF',f'{pmf_count}')
    p2.info(pmf_value)

    week=Weekly()
    weekly=week.getData()

    daily_send,weekly_send,monthly_send=st.tabs(['DAILY','WEEKLY','MONTHLY'])
    with weekly_send:
        st.subheader('WEEKLY')

        weekly['Week'] = weekly['Week'].astype(str)

        weekly['Year'] = weekly['Week'].str[:4].astype(int)
        weekly['Week_Num'] = weekly['Week'].str[4:].astype(int)

        weekly['Week'] = pd.to_datetime(weekly['Year'].astype(str) + '-01-01') + pd.to_timedelta((weekly['Week_Num'] - 1) * 7, unit='D')

        weekly['Week'] = weekly['Week'].dt.strftime('%Y-W%V')

        bar_chart = go.Bar(x=weekly['Week'], y=weekly['Amount'], name='Amount', marker=dict(color='#1a5ba6'))

        line_chart = go.Scatter(x=weekly['Week'], y=weekly['Volume'], name='Volume', yaxis='y2', mode='lines+markers', line=dict(color='green'))

        layout = go.Layout(title='Weekly Send Transaction Volume and Amount', xaxis=dict(title='Week',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='Amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    with daily_send:
        st.subheader('DAILY')

        bar_chart = go.Bar(x=dailySend['date'], y=dailySend['amount'], name='amount', marker=dict(color='#1a5ba6'))

        line_chart = go.Scatter(x=dailySend['date'], y=dailySend['id'], name='Volume', yaxis='y2', mode='lines', line=dict(color='green'))

        layout = go.Layout(title='Daily Send Transaction Volume and Amount', xaxis=dict(title='Date',tickangle=-90,showgrid=True, gridcolor='lightgray', gridwidth=1), yaxis=dict(title='amount'), yaxis2=dict(title='Volume', overlaying='y', side='right'))

        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(
            plot_bgcolor='white',
            autosize=False,
            width=1000,
            height=500                          
                        )
        frames = [go.Frame(data=[go.Bar(x=dailySend['date'][:i+1], y=dailySend['amount'][:i+1])]) for i in range(len(dailySend))]

        fig.frames = frames

        animation_options = dict(frame=dict(duration=400, redraw=True), fromcurrent=True)

        fig.update_layout(updatemenus=[dict(type='buttons', buttons=[dict(label='Play', method='animate', args=[None, animation_options])])])

        st.plotly_chart(fig)

    with monthly_send:
        monthly_send=parent_transactions.groupby(['month','years']).agg({'amount':'sum','id':'count'}).reset_index().sort_values(by='month',ascending=True)
      
        st.subheader('MONTHLY')
        monthly_send['month'] = monthly_send['month'] + ' ' + monthly_send['years'].astype(str)

        monthly_send['month'] = pd.to_datetime(monthly_send['month'], format='%B %Y')

        bar_chart = go.Bar(x=monthly_send['month'], 
                           y=monthly_send['amount'], 
                           name='amount', marker=dict(color='#1a5ba6')
                           )
        

        line_chart = go.Scatter(x=monthly_send['month'], 
                                y=monthly_send['id'], 
                                name='Volume', yaxis='y2',
                                mode='lines+markers', 
                                line=dict(color='green'))
        
        xaxis_labels = monthly_send['month'].dt.strftime('%b %Y')
        xaxis = dict(title='Date', tickangle=-90, showgrid=True, gridcolor='lightgray', gridwidth=1, tickvals=monthly_send['month'], ticktext=xaxis_labels)

        layout = go.Layout(
            title='Monthly Send Transaction Volume and Amount',                             
            xaxis=xaxis,                           
            yaxis=dict(title='amount'), 
            yaxis2=dict(title='Volume', overlaying='y', side='right')
        )

        fig = go.Figure(data=[bar_chart, line_chart], layout=layout)

        fig.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig)

    st.info('churn parents 2022')
    st.write(churn_parents_details)
    st.write(churn_parents_details_origin.sort_values(ascending=False))

    st.info('Top Parents')
    st.write(pmf)

    st.info('parents churn 2023')
    st.subheader('Pending Send')
    st.write(parent_accounts)

with tab6:
    schools.rename(columns={'rgnName':'region','dstName':'district','schName':'school'},inplace=True)
    regions = schools.groupby(['region', 'district']).agg({'schCode':'count','school': list}).reset_index()
    selected_region = st.selectbox(
        "Select Region", 
        regions['region'].unique(),
        key="region_selector_1"
    )
    filtered_df = regions[regions['region'] == selected_region]
    num_districts = len(filtered_df['district'].unique())
    num_schools=filtered_df['schCode'].sum()
    st.write(f"{num_districts} Districts in {selected_region} and {num_schools} Schools")
    selected_district = st.selectbox(
        "Select District", 
        filtered_df['district'].unique(),
        key="district_selector_1"
    )
    result_df = filtered_df[filtered_df['district'] == selected_district]
    st.write(f"{result_df['schCode'].values[0]} schools in {selected_district}")
    if len(result_df['school'].values) > 0:
        selected_school = st.selectbox(
            "Select School", 
            result_df['school'].values[0],
            key="school_selector_1"
        )

    st.write(result_df['school'].values[0])
    st.write(regions)
    st.write(school_transactions)
    df = pd.DataFrame(np.random.randn(1000, 2) / [50, 50] + [0.3476, 32.5825],
    columns=['lat', 'lon'])
    # Convert transactions column to numeric (in case of any formatting issues)
    school_transactions["transactions"] = pd.to_numeric(school_transactions["transactions"], errors="coerce")

    # Convert all potentially numeric columns to numeric type
    numeric_columns = ['transactions', 'Amount', 'Withdraw', 'Send', 'Payment', 'Deposit', 'CardReplacement', 'CardActivation']
    for column in numeric_columns:
        if column in school_transactions.columns:
            school_transactions[column] = pd.to_numeric(school_transactions[column], errors="coerce").fillna(0)

    # Separate schools with transactions above 10,000
    filtered_schools = school_transactions[school_transactions["transactions"] > 10000]

    # Sum the rest under "Other Schools"
    other_schools_sum = school_transactions[school_transactions["transactions"] <= 10000].sum(numeric_only=True)
    other_schools_sum["school"] = "Other Schools"

    # Append the summed "Other Schools" row
    final_school_transactions = pd.concat([filtered_schools, pd.DataFrame([other_schools_sum])], ignore_index=True)
    st.write(final_school_transactions)
    st.map(df)

@st.cache_data
def filter_and_aggregate_schools(school_performance, threshold=10000):
    """Filter schools with transactions above the threshold and aggregate others into 'Other Schools'."""
    # Ensure all relevant columns are numeric
    numeric_columns = ['Amount', 'transactions']
    for col in numeric_columns:
        school_performance[col] = pd.to_numeric(school_performance[col], errors='coerce').fillna(0)
    
    # Filter schools with transactions above the threshold
    main_schools = school_performance[school_performance['transactions'] >= threshold]
    
    # Aggregate schools with transactions below the threshold into "Other Schools"
    small_schools = school_performance[school_performance['transactions'] < threshold]
    if not small_schools.empty:
        others = pd.DataFrame({
            'school': ['Other Schools'],
            'Amount': [small_schools['Amount'].sum()],
            'transactions': [small_schools['transactions'].sum()]
        })
        
        # Combine main schools with others
        result = pd.concat([main_schools, others], ignore_index=True)
    else:
        result = main_schools
    
    return result

with tab6:
    st.header("School Performance Analysis")
    
    # Get the filtered and aggregated metrics data
    school_metrics = filter_and_aggregate_schools(school_transactions)
    
    # Ensure all relevant columns are numeric before aggregation
    school_metrics[['Amount', 'transactions']] = school_metrics[['Amount', 'transactions']].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    
    # Create tabs for different views
    perf_tab1, perf_tab2, perf_tab3 = st.tabs(["Transaction Analysis", "Regional Comparison", "Detailed Metrics"])
    
    with perf_tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Transaction Amount by School
            fig_amount = px.bar(
                school_transactions,
                x='school',
                y='Amount',
                color='school',
                title='Transaction Amount by School',
                barmode='group'
            )
            fig_amount.update_layout(
                xaxis_title="School",
                yaxis_title="Transaction Amount (UGX)",
                xaxis_tickangle=-45,
                height=500,
                legend_title="School"
            )
            st.plotly_chart(fig_amount, use_container_width=True)
            
            # Transaction Volume Heatmap
            fig_heatmap = px.density_heatmap(
                school_transactions,
                x='school',
                y='transactions',
                z='Amount',
                title='Transaction Volume Heatmap'
            )
            fig_heatmap.update_layout(height=400)
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Average Transaction Amount by School
            fig_avg = px.box(
                school_transactions,
                x='school',
                y='Amount',
                color='school',
                title='Average Transaction Amount Distribution'
            )
            fig_avg.update_layout(
                xaxis_tickangle=-45,
                height=500
            )
            st.plotly_chart(fig_avg, use_container_width=True)
            
            # Transaction Type Distribution
            transaction_types = ['Withdraw', 'Send', 'Payment', 'Deposit', 'CardReplacement', 'CardActivation']
            transaction_sums = school_transactions[transaction_types].sum().reset_index()
            transaction_sums.columns = ['transaction_type', 'total_amount']
            
            fig_dist = px.pie(
                transaction_sums,
                values='total_amount',
                names='transaction_type',
                title='Transaction Type Distribution',
                hole=0.4
            )
            st.plotly_chart(fig_dist, use_container_width=True)
    
    with perf_tab2:
        # Regional Performance Analysis
        region_metrics = school_transactions.groupby('school').agg({
            'Amount': 'sum',
            'transactions': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Regional Transaction Amounts
            fig_region = px.bar(
                region_metrics,
                x='school',
                y='Amount',
                color='school',
                title='Transaction Amount by School',
                barmode='group'
            )
            fig_region.update_layout(height=500)
            st.plotly_chart(fig_region, use_container_width=True)
        
        with col2:
            # Regional Transaction Volume
            fig_region_vol = px.bar(
                region_metrics,
                x='school',
                y='transactions',
                color='school',
                title='Transaction Volume by School',
                barmode='group'
            )
            fig_region_vol.update_layout(height=500)
            st.plotly_chart(fig_region_vol, use_container_width=True)
    
    with perf_tab3:
        # Detailed Metrics Table
        st.subheader("School Performance Metrics")
        
        # Ensure all relevant columns are numeric
        numeric_columns = ['Amount', 'transactions']
        for col in numeric_columns:
            school_transactions[col] = pd.to_numeric(school_transactions[col], errors='coerce').fillna(0)
        
        # Sort the DataFrame by 'Amount' in descending order
        metrics_summary = school_transactions.sort_values('Amount', ascending=False)
        
        # Format currency values
        metrics_summary['Amount'] = metrics_summary['Amount'].apply(lambda x: f'UGX {x:,.0f}')
        
        # Display the data
        st.dataframe(
            metrics_summary[['school', 'Amount', 'transactions']].rename(columns={
                'Amount': 'Total Amount',
                'transactions': 'Transaction Count'
            }),
            use_container_width=True
        )