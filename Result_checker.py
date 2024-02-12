import pandas as pd
import requests
import os
from bs4 import BeautifulSoup as bs
import streamlit as st
import time

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
    Total_Attempted = (sub['Your_Answer'].apply(len) != 0).sum() 
    Wrong_mcq =  (sub['Marks']== -1).sum()
    Correct_mcq = ((sub['Marks'] == 4) & (sub['Answers'].apply(len) == 10)).sum()
    
    Correct_sa = ((sub['Marks'] == 4) & (sub['Answers'].apply(len) != 10)).sum()
    Total_sa = Total_Attempted - ( Wrong_mcq + Correct_mcq )

    Total_Marks = sub['Marks'].sum()

    sub_Output = [Total_Attempted, Correct_mcq, Wrong_mcq, Total_sa, Correct_sa, Total_Marks]
    return sub_Output

# Start
url = "https://cdn3.digialm.com//per/g28/pub/2083/touchstone/AssessmentQPHTMLMode1//2083O23354/2083O23354S16D16841/17067995351433920/MP13002537_2083O23354S16D16841E1.html"
path = "Answer312.csv"    

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
st.write("# JEE Result Summary")
st.markdown('<h3 class="title">Just Paste Your Answer Sheet Link 👇 & Select you shift </h3>', unsafe_allow_html=True)

# Get URL input from the user

# URL input
url = st.text_input("", "")
url = url.strip()

# Columns for day and shift
day_column, shift_column = st.columns(2)

# Radio buttons for selecting day
selected_day = day_column.radio("Select Day", ["27 Jan", "29 Jan", "30 Jan", "31 Jan", "01 Feb"])
selected_day = selected_day[:2]

# Radio buttons for selecting shift
selected_shift = shift_column.radio("Select Shift", ["Shift 1", "Shift 2"])
selected_shift = selected_shift[-1:]

# Update path with day and shift
# path = f"Answer_Sheets\Answer{selected_day}{selected_shift}.csv"
csv_folder = "Answer_Sheets"
if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

path = os.path.join(csv_folder, f"Answer{selected_day}{selected_shift}.csv")

Start = st.button("Calculate")
# AnswerSheet Manipulation(given by NTA)

ans_sheet = pd.read_csv(path)
ans_sheet = ans_sheet.rename(columns={'Unnamed: 0': 'Question ID', 'Unnamed: 1': 'Answers'})
ans_sheet = ans_sheet.reset_index(drop=True)
ans_sheet['Question ID'] = ans_sheet['Question ID'].astype(str)
ans_sheet['Answers'] = ans_sheet['Answers'].astype(str)


if Start:
    # Getting Page for Scrapping
    page = requests.get(url)
    soup = bs(page.text, 'html.parser')
    sections = soup.find_all('div', class_='section-cntnr')


    if not page:
        st.warning("Unable to fetch Page check your link or internet")
        time.delay(1)
    # List 
    question_ids = []
    your_answers = []



    # Filling List with Subject Entries
    calculate(sections[0], sections[1]) # maths
    calculate(sections[2], sections[3]) # phy
    calculate(sections[4], sections[5]) # chem


    # Created que_sheet from your question list from NTA
    que_sheet = pd.DataFrame({
        'Question ID': question_ids,
        'Your_Answer': your_answers
    })

    # merging ans_sheet and que_sheet
    merged_df = pd.merge( ans_sheet, que_sheet, on='Question ID', how='left')

    # calculatin Marks Column
    merged_df['Marks'] = merged_df.apply(lambda row: 4 if row['Answers'] == row['Your_Answer'] else (-1 if len(str(row['Your_Answer'])) == 10 else 0), axis=1)
    
    
    #time.sleep(1)
    # Subject Divisions and calculated Fields 
    
    if (merged_df['Your_Answer'].apply(lambda x: len(str(x)) if pd.notna(x) else 0) != 0).sum():
        Total_Attempted = (merged_df['Your_Answer'].apply(len) != 0).sum()
    else :
        st.warning("Make sure you have selected correct Shift or used correct candidate link")

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
    st.markdown('<h3 class="subheader">Total Marks Obtained: {}</h3>'.format(Total[1]), unsafe_allow_html=True)
    st.markdown('<h3 class="subheader">Total Questions Attempted: {}</h3>'.format(Total[0]), unsafe_allow_html=True)


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
    st.markdown('<h4 class="performance-header">Subject-wise Performance</h4>', unsafe_allow_html=True)

    table_data = {
        'Subject': ['Maths', 'Physics', 'Chemistry'],
        'Attempted': [Maths_Output[0], Phy_Output[0], Chem_Output[0]],
        'Correct MCQs': [Maths_Output[1], Phy_Output[1], Chem_Output[1]],
        'Wrong MCQs': [Maths_Output[2], Phy_Output[2], Chem_Output[2]],
        'Total SAs': [Maths_Output[3], Phy_Output[3], Chem_Output[3]],
        'Correct SAs': [Maths_Output[4], Phy_Output[4], Chem_Output[4]],
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

    df = pd.read_csv("other_files/data.csv")

    new_data = {'URL': url, 'Total Marks': Total_Marks, 'Total Attempted': Total_Attempted, 'Day':selected_day, 'Shift':selected_shift}
    df = df._append(new_data, ignore_index=True)

    df.to_csv("data.csv")