import streamlit as st
import plotly.express as px
import pandas as pd

import os
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Mega Store", page_icon=":shopping_bags:",layout="wide")

st.title(" :shopping_bags: Mega Store Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":open_file_folder: Upload file here",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "ISO-8859-1")

else:
    os.chdir("C:\Tim\streamlit_dashboard")
    df=pd.read_csv("Superstore.csv", encoding = "ISO-8859-1")


col1, col2 = st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d/%m/%Y")


# for filtering the dates
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:    
    date2 = pd.to_datetime(st.date_input("End Date",endDate))

df = df[(df["Order Date"]>= date1)& (df["Order Date"]<= date2)].copy()


st.sidebar.header("Pick a filter")
region = st.sidebar.multiselect("Select a region", df["Region"].unique())

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Select a state", df2["State"].unique())
if not state:
    df3 = df2.copy()

else:
    df3 = df2[df2["State"].isin(state)]



city = st.sidebar.multiselect("Select a city", df3["City"].unique())
# Filter by City, state and region

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city: 
    filtered_df = df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region and city: 
    filtered_df = df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state: 
    filtered_df = df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city: 
    filtered_df = df3[df3["City"].isin(city) ]
else: 
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]


category_df = filtered_df.groupby(by=["Category"],as_index=False)["Sales"].sum()

with col1: 
    st.subheader("Category Type Sales")
    fig = px.bar(category_df,x="Category",y="Sales",text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height =200)

with col2:
    st.subheader("Region Type Sales")
    fig = px.pie(filtered_df, values="Sales",names="Region",hole=0.5)
    fig.update_traces(text = filtered_df["Region"],textposition= "outside")
    st.plotly_chart(fig,use_container_width=True)

cl1, cl2 = st.columns((2))

with cl1:
    with st.expander("Category_Row_Data"):
        
        #st.write(category_df.T.style.background_gradient(cmap="Orange"))
        st.write(category_df)
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_Row_Data"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region)
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
        
filtered_df["month_year"]= filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig_2= px.line(linechart,x="month_year",y="Sales",labels={"Sales":"Amount"},height=500,width=1000,template="gridon")
st.plotly_chart(fig_2,use_container_width=True)

with st.expander("Expand Time Series"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv=linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download this Data', data=csv,file_name="Timeseries.csv",mime='text/csv')


st.subheader("Sales view using Treemap hierarchy")
fig3 = px.treemap(filtered_df,path=["Region","Category","Sub-Category"],values="Sales",hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800,height=850)
st.plotly_chart(fig3,use_container_width=True)

chart1,chart2 = st.columns((2))
with chart1:
    st.subheader('Sales by Segment')
    fig=px.pie(filtered_df,values="Sales",names="Segment",template="gridon")
    fig.update_traces(text=filtered_df["Segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

with chart2:
    st.subheader('Sales by Category')
    fig=px.pie(filtered_df,values="Sales",names="Category",template="plotly_dark")
    fig.update_traces(text=filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":arrow_forward: Monthly wise custom columns")
with st.expander("Summary_table"):
    df_sample = df[0:10][["Region","State","City","Category","Quantity","Profit","Sales"]]
    fig = ff.create_table(df_sample,colorscale="Cividis")
    st.plotly_chart(fig,use_container_width=True)

    st.markdown("Table for Subcategories by Month")
    filtered_df["month"]=filtered_df["Order Date"].dt.month_name()
    sub_Category_Year = pd.pivot_table(data=filtered_df,values="Sales",index=["Sub-Category"],columns="month")
    #st.write(sub_Category_Year.T.style.background_gradient(cmap="Blues"))
    st.write(sub_Category_Year)

#Scatter plot 
data1 = px.scatter(filtered_df,x="Sales",y="Profit",size="Quantity")
data1['layout'].update(title="Scatter plot Sales against Proft.",
                       titlefont=dict(size=20),xaxis=dict(title="Sales",titlefont=dict(size=18)),
                       yaxis=dict(title="Profit",titlefont=dict(size=18)))

st.plotly_chart(data1,use_container_width=True)



st.subheader(":arrow_forward: Other Charts")


col1, col2 = st.columns((2))
sales_df = filtered_df.groupby(by=["Discount"],as_index=False)["Sales"].sum()
#sales_df["Discount"] = sales_df["Discount"].astype(str)


sub_category_df = filtered_df.groupby(by=["Sub-Category"],as_index=False)["Sales"].sum()


with col1: 
    
    st.subheader("Sales vs Discount Line Chart")

    # Line chart
    fig = px.line(sales_df, x="Discount", y="Sales", markers=True, labels={"Discount": "Discount", "Sales": "Sales"})
    st.plotly_chart(fig, use_container_width=True, height =200)


with col2: 
   
    st.subheader("Subcategory by Sales")
    fig = px.bar(sub_category_df,x="Sub-Category",y="Sales",text=['${:,.2f}'.format(x) for x in sub_category_df["Sales"]],
                 template = "seaborn")
    st.plotly_chart(fig,use_container_width=True, height =200)


cl1, cl2 = st.columns((2))


with cl1:
    with st.expander("Discount_Row_Data"):
        
        #st.write(category_df.T.style.background_gradient(cmap="Orange"))
        st.write(sales_df)
        csv = sales_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Discount.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("Subcategory_Row_Data"):
        st.write(sub_category_df)
        csv = sub_category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Subcategory.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')


st.subheader(":arrow_forward: Download Original Data set")
with st.expander("Download set"):
    csv=df.to_csv(index=False).encode("utf-8")
    st.download_button('Download this Data', data=csv,file_name="Original.csv",mime='text/csv')

        
