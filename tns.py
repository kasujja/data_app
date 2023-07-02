import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objs as go
import plotly.io as pio
import plotly.offline as pyo
import plotly.subplots as sp
from plotly.subplots import make_subplots
from datetime import date
import datetime
from st_aggrid import AgGrid, GridUpdateMode,JsCode

st.set_page_config(page_title='KAWU',layout='wide')

kawu = create_engine('mysql://jro:jro2021@localhost:3303/kawu_db')
acc=kawu.engine.execute("SET sql_mode=(select replace(@@sql_mode,'ONLY_FULL_GROUP_BY',''))")


day='select sum(tsnAmmount) amount,count(tsnNumber) Number,dayname(date(tsnDate)) day,typeName from transactions inner join transaction_type using(typeId) group by dayname(date(tsnDate)),typeId order by amount desc;'
day=pd.read_sql(day,kawu)

class Month():
    def __init__(self):
        self.month='''select sum(tsnAmmount) amount,count(tsnNumber) Number,monthname(tsnDate)
          month,year(tsnDate) year,month(tsnDate) mnt,typeName from  transactions
            inner join student_transactions using(tsnNumber) 
            inner join students using(studentId) 
            inner join transaction_type using(typeId)
            group by 
            monthname(tsnDate),month(tsnDate),typeId,year(tsnDate) order by mnt,year asc;'''
        self.month=pd.read_sql(self.month,kawu)

    def mnt_data(self):
        return self.month

class Trans(Month):
    def __init__(self):
            Month.__init__(self)


mnt=Month()
month=mnt.mnt_data()

class Students():
    def __init__(self):
        self.students='''select studentId,regDate,firstName,lastName,gender,
        schoolId,className,accBalance from students inner join student_accounts using(studentId)
        inner join classes using(classId)'''
        self.students=pd.read_sql(self.students,kawu)
    
    def getStudents(self):
        return self.students
class Transactions():
    def __init__(self):
        self.transactions='''select tsnNumber, tsnAmmount amount,tsnDate date,typeName from transactions natural join transaction_type'''
        self.transactions=pd.read_sql(self.transactions,kawu)
    
    def getTrans(self):
        return self.transactions
    
class studentTransactions():
    def __init__(self):
        self.studtsn='''select tsnNumber,tsnAmmount amount,tsnDate date,typeName from transactions full 
        join student_transactions using(tsnNumber) matural join transaction_type '''

    def getStudTrans(self):
        return self.studtsn        
    
    


std=Students()
student=std.getStudents()
students=len(student['studentId'])
schools=student['schoolId'].nunique()
balance=student['accBalance'].sum()
st.write(student)


#transactions objects
trans=Transactions()
tns=trans.getTrans()
counts=len(tns['tsnNumber'])
send=tns[tns['typeName']=='Send']
sendCount=len(send['tsnNumber'])
sent=send['amount'].sum()
tAmount=tns['amount'].sum()
# st.write(tns)
st.info(counts)
# st.write(send)
st.info(f'Send Value{sent},Send Volume{sendCount}')


# class Filters(Trans):
#     skuls=st.sidebar.multiselect(
#         'choose a school',
#         options=month['schName'].unique()
#        )
   
#     def filter_school(self):
#         skul=Filters.skuls
#         filt=month.query('schName==@skul') 
#         return filt
    
    
# filtered=Filters()
# sfilt=filtered.filter_school()
# st.write(sfilt)

class Years(Trans):
    yaz=st.sidebar.multiselect(
        'choose year',
        options=month['year'].unique()
    )

    def filter_year(self):
        time=Years.yaz
        filts=month.query('year==@time')
        return filts
    
filter=Years()
yfilt=filter.filter_year()

ov1,ov2,ov3,ov5,ov7=st.columns(5)
ovTns=month['Number'].sum()
ovVal=month['amount'].sum()
ovVal='{:,.0f}'.format(tAmount)
counts='{:,.0f}'.format(counts)
ov1.metric('Transaction Volume',f'{counts}')
ov2.metric('Transaction Value',f'UGX {ovVal}')
studentCount='{:,.0f}'.format(students)
ov3.metric('Students',f'{studentCount}')
# ov6.metric('Schools',f'{schools}')
balance='{:,.0f}'.format(balance)
ov5.metric('Student Balance',f'UGX {balance}')

studets=st.container()
with studets:
    st.subheader('STUDENTS')
    gender=student[['studentId','gender','className']].groupby(['gender']).count()
    genderBal=student[['gender','accBalance']].groupby(['gender']).sum()
    studClass=student[['studentId','className']].groupby(['className']).count()
    classBal=student[['gender','className','accBalance']].groupby(['className']).sum()
    active=len(student[student['accBalance']>0])
    kawu=students-active
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
        gd=student[['studentId','gender','className']]
        gd['stdId']=gd['studentId'].count()
        # st.write(gd)
        gdc=px.histogram(gd, x="gender", y="studentId", color='className',barmode='group',title='transactions by class and gender')
        st.plotly_chart(gdc)
    with bal:
        cl=student[['gender','className','accBalance']]
        clb=px.histogram(cl, x="gender", y="accBalance", color='className',barmode='group',title='Student Balance grouped by Gender and Class')
        st.plotly_chart(clb)

# ov4.metric('Active cards',f'{active}')
ov7.metric('In Kawu',f'{kawu}')


st.subheader('TRANSACTIONS')

smnt = px.bar(month, x='month', y='amount', color='typeName', title='Total Monthly Transactions ' ,text_auto='.2s'
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
    labels=month['typeName'],
    values=month['amount'],
    hole=.4,    
    # marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0.55, 1], y=[0.5, 1]),
    texttemplate='%{percent}<br>%{label}',
))
smnt.add_trace(go.Pie(
    labels=month['typeName'],
    values=month['Number'],
    hole=.4,
    title='Transaction Type Value',
    # marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0, 0.3], y=[0.5, 1]),
    textfont=dict(size=12),
    texttemplate='%{percent}<br>%{label}',
))
st.plotly_chart(smnt)

amount=yfilt['amount'].sum()
counts=yfilt['Number'].sum()
groups=yfilt.groupby('typeName').sum()[['amount']]

groups.reset_index(inplace=True)
groups=groups.to_dict()
# sch=yfilt['schName'].nunique()




st.write(yfilt)
a,b,c,d=st.columns(4)
a.metric('Value',f'{amount}')
b.metric('Volume',f'{counts}')
st.info(groups)
# c.metric('Schools',f'{sch}')
# for group in groups:
#     st.info(f'{groups["typeName"],groups["amount"]}')

mnt = px.bar(yfilt, x='month', y='amount', color='typeName', title='total monthly Transactions' ,text_auto='.2s'
            )

mnt.update_layout(
    barmode='group',
    height=600,
    plot_bgcolor='#f2f2f2',
    legend=dict(title='Transaction Type'),
    yaxis=dict(title='Transaction Amount',domain=[0, 0.85]),
    yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True, domain=[0.87, 1]),
)
# add a pie chart subplot for the transaction type breakdown
mnt.add_trace(go.Pie(
    labels=yfilt['typeName'],
    values=yfilt['amount'],
    hole=.4,    
    marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0, 0.7], y=[0.6, 1]),
    texttemplate='%{percent}<br>%{label}',
))
# mnt.add_trace(go.Pie(
#     labels=yfilt['year'],
#     values=yfilt['Number'],
#     hole=.4,
#     title='Transaction Type Value',
#     marker_colors=['#1a5ba6', '#00BFFF'],
#     domain=dict(x=[0, 0.6], y=[0.6, 1]),
#     textfont=dict(size=12),
#     texttemplate='%{percent}<br>%{label}',
# ))
# mnt.update_layout(legend=dict(yanchor="top", y=0.9, xanchor="left", x=0.4))


st.plotly_chart(mnt)



mnt2 = px.bar(month, x='month', y='amount', color='typeName' ,text_auto='.2s',facet_col="year",barmode='group',title='monthly transactions compared by year'
            )
mnt2.update_layout(
    height=600,
    plot_bgcolor='#f2f2f2',    
    yaxis=dict(title='Transaction Amount',domain=[0, 0.85]),
    xaxis_tickangle=90,xaxis2_tickangle=90,
    yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True),
)

mnt2.add_trace(go.Pie(
    labels=month['year'],
    values=month['amount'],
    hole=.4,    
    marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0.55, 1], y=[0.6, 1]),
    texttemplate='%{percent}<br>%{label}',
))

mnt2.add_trace(go.Pie(
    labels=month['year'],
    values=month['Number'],
    hole=.4,    
    marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0.55, 1], y=[0.6, 1]),
    texttemplate='%{percent}<br>%{label}',
))


st.plotly_chart(mnt2)




# create bar chart for total transaction amount by day and transaction type
fig = px.bar(day, x='day', y='amount', color='typeName', title='Total transaction amount by day')

# add a second y-axis for the transaction count
# fig.add_trace(go.Scatter(x=day['day'], y=day['Number'], name='Transaction Count', yaxis='y2'))

# update the layout
fig.update_layout(
    barmode='group',
    height=600,
    plot_bgcolor='white',
    legend=dict(title='Transaction Type'),
    yaxis=dict(title='Transaction Amount',domain=[0, 0.85]),
    yaxis2=dict(title='Transaction Count', overlaying='y', side='right', showgrid=True, domain=[0.87, 1]),
)

# add a pie chart subplot for the transaction type breakdown
fig.add_trace(go.Pie(
    labels=day['typeName'],
    values=day['amount'],
    hole=.4,
    title='Transaction Type Value',
    marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0.55, 1], y=[0.5, 1]),
    texttemplate='%{percent}<br>%{label}',
))

fig.add_trace(go.Pie(
    labels=day['typeName'],
    values=day['Number'],
    hole=.3,
    title='Transaction type count',
    marker_colors=['#1a5ba6', '#00BFFF'],
    domain=dict(x=[0, 0.6], y=[0.6, 1]),
    textfont=dict(size=12),
    textposition='inside',
    texttemplate='%{percent}<br>%{label}',
))

# update the layout of the pie chart subplot
fig.update_layout(
    title='Transaction Analysis',
    grid=dict(rows=1, columns=2)
)

st.plotly_chart(fig)

st.header('Performance By Month')
class Mont():
    mnts=st.multiselect(
        'select a month',
        options=yfilt['month'].unique()
        )

    def filter_month(self):
        mnt=Mont.mnts
        mntfilt=yfilt.query('month==@mnt') 
        return mntfilt
    # def mreg(self):
monthly=Mont()
mfilt=monthly.filter_month()
st.write(mfilt)
total=mfilt['amount'].sum()
ntotal=mfilt['Number'].sum()
st.write()
n,v,c=st.columns(3)
n.metric('Transaction Volume',f'{ntotal}')
v.metric('Transaction Value',f'UGX {total}')
act=mfilt[mfilt['typeName']=='Card Activation']

act=act.iloc[0,1]
c.metric('Cards Activated',f'{act}')


# plot cahrt for the month selected
fp=px.pie(mfilt,values='amount',names='typeName',hole=0.4)
fp.update_layout(title_text='<b>Transaction Value Grouped by Type</b>',
                    height=350,
                    showlegend=True,
    
    )
st.plotly_chart(fp)


# dail=st.container()
# with dail: 
#     st.subheader('Performance by date')
#     # d = st.date_input("When's your birthday",datetime.date(2019, 7, 6))
#     class Day(Filters):
#         sfilt['date']=sfilt['date'].astype(str)
#         day=sfilt['date'].str[0:10]

#         sfilt['day']=pd.to_datetime(day)
#         #days=sfilt['day']
        
daiz= st.date_input(
    'choose a date',
    #pd.to_datetime(days)
    datetime.date(2022,6,23)
    )

#         def filter_day(self):
#             dy=Day.daiz
#             dzfilt=sfilt.query('day==@dy')
#             return dzfilt
#     daily=Day()
#     dfilt=daily.filter_day()

#     tod=dfilt['amount'].sum()
#     dailyTypeSum=dfilt.groupby('type')[['amount']].sum()
#     st.info(tod)
#     st.write(dailyTypeSum)

    
#     dailyCount=dfilt['code'].count()
#     dailyTypeCount=dfilt.groupby('type')[['student']].count()
    
#     st.info(dailyCount)
#     st.write(dailyTypeCount)
    
#     # dstud=dfilt[['cardNumber','balance','gender','day']].drop_duplicates()
#     # st.write(dstud)
#     todayMax=dfilt['amount'].max()
#     todayMin=dfilt['amount'].min()
#     todayAvg=dfilt['amount'].mean()
#     st.info('Maximum :%f, Minimum : %f, Average :%f' % (todayMax, todayMin, todayAvg))
#     st.subheader('minimum transaction by type')
#     typeMin=dfilt[['amount','school','student','type']].groupby('type').min()
#     st.write(typeMin)
#     st.subheader('maximum transaction by type')
#     typeMax=dfilt.groupby('type')[['amount','school','student']].max()
#     st.write(typeMax)



import numpy as np
import pydeck as pdk

chart_data = pd.DataFrame(
   np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
   columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=37.76,
        longitude=-122.4,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=chart_data,
           get_position='[lon, lat]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))
st.write(chart_data)



