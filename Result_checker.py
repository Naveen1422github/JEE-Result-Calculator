import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import streamlit as st

## Scrap vales section wise (like maths mcq and sa)
def calculate(section1, section2):
    # Mcqs
    mcqs = section1.find_all('table', class_='menu-tbl')
    for num in mcqs:
        tds = num.find_all('td', class_='bold') 
        question_ids.append(tds[1].text)
        ans = tds[7].text
        if ans != " -- ":
            val = int(ans)+1
            your_answers.append(tds[val].text)
        else :
            your_answers.append("")

    # numerics quetions
    nums = section2.find_all('table', class_='menu-tbl')

    for num in nums:
        given_answer_element = num.find('td', string='Question ID :')
    
        if given_answer_element:
            # Extract the value from the next sibling (assuming it's the next element)
            que = given_answer_element.find_next_sibling('td', class_='bold').text.strip()   
            question_ids.append(que)

    # numerics answers
    nums = section2.find_all('table', class_='questionRowTbl')

    for num in nums:
        given_answer_element = num.find('td', string='Given Answer :') 
        if given_answer_element:
            # Extract the value from the next sibling (assuming it's the next element)
            ans = given_answer_element.find_next_sibling('td', class_='bold').text
            if ans != " -- ":
              your_answers.append(ans)
            else :
              your_answers.append("")

# Calucalate values subject wise
def subject_val(sub):
    Total_Attempted = sub['Your_Answer'].value_counts().iloc[0]
    Wrong_mcq =  (sub['Marks']== -1).sum()
    Correct_mcq = ((sub['Marks'] == 4) & (sub.index >= 0) & (sub.index <= 19)).sum()

    Correct_sa = ((sub['Marks'] == 4) & (sub.index >= 20) & (sub.index <= 29)).sum()
    Total_sa = Total_Attempted - ( Wrong_mcq + Correct_mcq )

    Total_Marks = sub['Marks'].sum()

    sub_Output = [Total_Attempted, Correct_mcq, Wrong_mcq, Total_sa, Correct_sa, Total_Marks]
    return sub_Output

# Start
url = "https://cdn3.digialm.com//per/g28/pub/2083/touchstone/AssessmentQPHTMLMode1//2083O23354/2083O23354S16D16841/17067995351433920/MP13002537_2083O23354S16D16841E1.html"
path = "Answer1.csv"    

#-----

st.markdown(
    """
    <style>
        .title {
            background-color: #3498db;
            padding: 10px;
            color: white;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 class="title">JEE Result Summary</h1>', unsafe_allow_html=True)

# Get URL input from the user

url = st.text_input("Enter URL and Press Enter:", "https://www.google.com/")

Start = st.button("Calculate")
# AnswerSheet Manipulation(given by NTA)

ans_sheet = pd.read_csv(path)
ans_sheet = ans_sheet.drop(0)
ans_sheet = ans_sheet.rename(columns={'Unnamed: 0': 'Question ID', 'Unnamed: 1': 'Answers'})
ans_sheet = ans_sheet.reset_index(drop=True)
ans_sheet['Question ID'] = ans_sheet['Question ID'].astype(str)
ans_sheet['Answers'] = ans_sheet['Answers'].astype(str)
ans_sheet = ans_sheet.sort_values(by='Question ID')


# Getting Page for Scrapping
page = requests.get(url)
soup = bs(page.text, 'html.parser')
sections = soup.find_all('div', class_='section-cntnr')

# List 
question_ids = []
your_answers = []

if Start:
    # Filling List with Subject Entries
    calculate(sections[0], sections[1]) # maths
    calculate(sections[2], sections[3]) # phy
    calculate(sections[4], sections[5]) # chem


    # Created que_sheet from your question list from NTA
    que_sheet = pd.DataFrame({
        'Question ID': question_ids,
        'Your_Answer': your_answers
    })
    que_sheet = que_sheet.sort_values(by='Question ID')

    # merging ans_sheet and que_sheet
    merged_df = pd.merge( ans_sheet, que_sheet, on='Question ID', how='left')

    # calculatin Marks Column
    merged_df['Marks'] = merged_df.apply(lambda row: 4 if row['Answers'] == row['Your_Answer'] else (-1 if len(str(row['Your_Answer'])) == 10 else 0), axis=1)

    # Subject Divisions and calculated Fields 
    Total_Attempted = merged_df['Your_Answer'].value_counts().iloc[0]
    Total_Marks = merged_df['Marks'].sum()
    sectioned_dfs = [merged_df.iloc[i:i+30] for i in range(0, len(merged_df), 30)]
    Maths = sectioned_dfs[0]
    Phy = sectioned_dfs[1]
    Chem = sectioned_dfs[2]

    Total = [Total_Attempted, Total_Marks]

    # calculating Subject values using subject_val function
    Maths_Output = subject_val(Maths)
    Phy_Output = subject_val(Phy)
    Chem_Output = subject_val(Chem)

 
        # Subheaders with colorful background
    st.markdown(
        """
        <style>
            .subheader {
                background-color: #2ecc71;
                padding: 5px;
                color: white;
                border-radius: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<h2 class="subheader">Total Marks Obtained: {}</h2>'.format(Total[1]), unsafe_allow_html=True)
    st.markdown('<h2 class="subheader">Total Questions Attempted: {}</h2>'.format(Total[0]), unsafe_allow_html=True)


    # Create a table for displaying subject-wise details
    # Subject-wise Performance header with enhanced styling
    st.markdown(
        """
        <style>
            .performance-header {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 10px;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<h3 class="performance-header">Subject-wise Performance</h3>', unsafe_allow_html=True)

    table_data = {
        'Subject': ['Maths', 'Physics', 'Chemistry'],
        'Attempted': [Maths_Output[0], Phy_Output[0], Chem_Output[0]],
        'Correct MCQs': [Maths_Output[1], Phy_Output[1], Chem_Output[1]],
        'Wrong MCQs': [Maths_Output[2], Phy_Output[2], Chem_Output[2]],
        'Correct SAs': [Maths_Output[3], Phy_Output[3], Chem_Output[3]],
        'Wrong SAs': [Maths_Output[4], Phy_Output[4], Chem_Output[4]],
        'Marks': [Maths_Output[5], Phy_Output[5], Chem_Output[5]],
    }

    st.markdown(
        """
        <style>
            .data-table {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.table(table_data)

