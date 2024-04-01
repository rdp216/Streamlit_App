import numpy as np
import streamlit as st
import requests
# import seaborn as sns
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
title_text = "My Streamlit App"
bg_color = "#F0F2F5"  # Example light gray color, choose your desired color

# Display the title with custom component (experimental)
st.set_page_config(
   page_title="Reverse DCF",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",

)

# Navigation options
navigation_options = ["Home", "Evaluation"]

def Sales_Profit_Table(soup):
    sales = soup.find_all('table', class_='ranges-table')[0].text
    profit = soup.find_all('table', class_='ranges-table')[1].text
    lsSales = []
    lsProfit = []
    sales = sales.split("\n")
    profit = profit.split("\n")

    for item in sales:
        if item.endswith('%'):
            lsSales.append(int(item.replace('%', '')))
    for item in profit:
        if item.endswith('%'):
            lsProfit.append(int(item.replace('%', '')))

    df = pd.DataFrame(columns=["10 Years", "5 Years", "3 Years", "TTM"])

    df.loc["Sales"] = lsSales
    df.loc["Profit"] = lsProfit

    data = list(zip(lsSales, lsProfit))  # Combine lists into tuples
    index = ["10 Years", "5 Years", "3 Years", "TTM"]  # Custom index for timeframes

    # Create the DataFrame
    df1 = pd.DataFrame(data, columns=["Sales", "Profit"], index=index)
    st.title("Sales and Profit Comparison")
    st.dataframe(df,width=900)
    # Create a row container to display the bar charts side-by-side
    # col1, col2, col3 = st.columns(3)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(22,8))  # Adjust figure size

    # Plot Sales Data in the first subplot (ax1)
    bars1 = ax0.barh(index, lsSales, color='skyblue', label='Sales')
    ax0.set_xlabel('Value')
    ax0.set_ylabel('Year')
    ax0.set_title('Sales Performance')
    ax0.legend()
    # st.pyplot(fig)
    # with col2:
        # Plot Profit Data in the second subplot (ax2)
    bars2 = ax1.barh(index, lsProfit, color='gold', label='Profit')  # Different color for clarity
    ax1.set_xlabel('Value')
    ax1.set_ylabel('Year')
    ax1.set_title('Profit Performance')
    ax1.legend()
    ax1.legend(fontsize=14)
    ax0.tick_params(axis='both', which='major', labelsize=14)
    ax1.tick_params(axis='both', which='major', labelsize=14)
    # In your Streamlit layout
    with st.container():
        st.pyplot(fig)
        st.write('<style>.element { width: 200px; }</style>', unsafe_allow_html=True)

    # Adjust layout (optional)
    plt.tight_layout()


def roceMedian(soup):
    roceRaw = soup.find_all("table", class_="data-table responsive-text-nowrap")[4]
    roceRaw1 = roceRaw.find_all('td')
    iterable = 0
    ls = []
    while iterable < 5:

        for i in (roceRaw1[72 + iterable]):
            ls.append(int(i.strip("%")))

            iterable += 1
    roceMed = np.median(ls)
    st.write("5-yr median pre-tax RoCE : ", str(roceMed))
def FY23PE(soup):
    section = soup.find('section', {'id': 'profit-loss'})
    if section:
        table = section.find('table', {'class': 'data-table'})
        if table:

            # Rows with Net Profit
            netProfitTable = table.find_all('tr')
            netProfitRaw = netProfitTable[10].text
            yearsRaw = netProfitTable[0].text
            yearsRaw = yearsRaw.split()
            netProfitRaw = netProfitRaw.split()
            i = 0
            years = []
            for i in range(0, len(yearsRaw)):
                if i % 2 != 0:
                    years.append(yearsRaw[i])
            netProfit = netProfitRaw[3:]
            yearly_net_profit = dict(zip(years, netProfit))
            netProfit = yearly_net_profit["2023"].replace(",", "")
            intNetProfit = int(netProfit)

            # Market Cap
            roce_type = soup.find_all("span", class_="number")
            marketCapRaw = roce_type[0].text.replace(",","")
            marketCapInt = int(marketCapRaw)
            PE23 = round(marketCapInt / intNetProfit,2)
            st.write("FY23PE : "+ str(PE23))
        else:
            print("Profit and loss table not found")
    else:
        print("Profit and loss section not found")
def slider():
    st.slider('Cost Of Capital (CoC): % ', min_value=8, max_value=16, step=2, value=12)
    st.slider('Return on Capital Employed (RoCE): % ', min_value=10, max_value=100, step=10, value=20)
    st.slider('Growth during high growth period: $ ', min_value=8, max_value=20, step=2, value=12)
    st.slider('High growth period(years) ', min_value=10, max_value=25, step=2, value=15)
    st.slider('Fade period(years): ', min_value=5, max_value=20, step=5, value=15)
    st.slider('Terminal growth rate: %', min_value=0, max_value=8, step=1, value=5)

def PE(soup):
    roce_type = soup.find_all("li", class_="flex flex-space-between")[3]
    value = roce_type.find("span", class_="number").text
    st.write("Current PE: " + value)

    FY23PE(soup)
    roceMedian(soup)


def Evaluation():
    st.markdown("### VALUING CONSISTENT COMPOUNDERS")
    st.write("Hi there!")
    st.write("This page will help you calculate intrinsic PE of consistent compounders through growth-RoCE DCF model.")
    st.write("We then compare this with current PE of the stock to calculate degree of overvaluation.")

    sym = st.text_input("NSE/BSE symbol", value="NESTLEIND")
    url = "https://www.screener.in/company/" + str(sym) + "/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    stockName = soup.find_all("h1", class_="h2 shrink-text")
    st.write("Company : " ,stockName[0].text )
    st.write("Stock Symbol : ", sym)
    PE(soup)
    Sales_Profit_Table(soup)
    slider()


def content_display(selected_page):
    if selected_page == "Home":
        st.write("This site provides interactive tools to valuate and analyze stocks"
                 " through Reverse DCF model. Check the navigation bar for more.")
    elif selected_page == "Evaluation":
        Evaluation()
    else:
        st.error("Unexpected page selection!")


def app_layout():
    col1, col2 = st.columns([3, 0.8])  # Adjust column widths as needed

    with col1:
        st.markdown("""
              # Reverse DCF
        """)
    with col2:
        # Navigation dropdown with arrow
        selected_page = st.selectbox("Pages", navigation_options, key="navigation")

    # Content section below the navigation
    content_display(selected_page)


# Call the app_layout function to display the app
app_layout()

# Use session state to store the selected page
if 'selected_page' not in st.session_state:
    st.session_state['selected_page'] = "Home"  # Set default page on first run
