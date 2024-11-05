import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu
# Database connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Abinesh",
    database='redbus_project'
)
#Connection Check and Cursor Initialization
if mydb.is_connected():
    st.markdown(f"## <span style='color:white'>RedBus</span>", unsafe_allow_html=True)
mycursor = mydb.cursor(buffered=True)

#Styling the App
st.markdown(
    """
    <style>
    .stApp {
        background-color:#222222; /*  Charcoal*/
    }
    label[data-testid="stSelectLabel"] {
        color: white !important;
    }
    label[data-testid="stTextInputLabel"] {
        color: white !important;
    }
    .css-1d391kg p {
        color: white !important; /* Text inside markdown elements */
    }
    .css-16huue1.e16nr0p34 {
        color: white !important; /* Slider label text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)

#Fetching Data for Filters
mycursor.execute("SELECT DISTINCT state_names FROM bus_data")
states = [state[0] for state in mycursor.fetchall()]

mycursor.execute("SELECT DISTINCT From_Place FROM bus_data")
from_places = [place[0] for place in mycursor.fetchall()]

mycursor.execute("SELECT DISTINCT To_Place FROM bus_data")
to_places = [place[0] for place in mycursor.fetchall()]
#Creating the Form for Input Criteria
with st.form("Bus Search Criteria"): 
    st.markdown(f"## <span style='color:white'>Bus Search Criteria</span>", unsafe_allow_html=True)
    selected_state = st.selectbox("Select State", states)
    selected_from_place = st.selectbox("Select Departure Place", from_places) 
    
    selected_to_place = st.selectbox("Select Destination Place", to_places)
    
    selected_rating = st.slider('Select Minimum Bus Rating', min_value=0.0, max_value=5.0, value=3.0, step=0.1)
    
    time_filter = st.slider("Select Time (HH:MM) for Departure Filter (After selected time)", 
                            min_value=0, max_value=23, value=18, step=1)
    
    
    min_price, max_price = st.slider('Select Ticket Price Range', min_value=100, max_value=5000, value=(500, 3000), step=100)

    
    submit_button = st.form_submit_button(label='Submit')

    #Processing Form Submission
    if submit_button:
        selected_time = f"{time_filter:02d}:00:00"

        
        st.write("Info:")
        st.write(f"State: {selected_state}")
        st.write(f"From Place: {selected_from_place}")
        st.write(f"To Place: {selected_to_place}")
        st.write(f"Rating: {selected_rating}")
        st.write(f"Time: {selected_time}")
        st.write(f"Price Range: {min_price} - {max_price}")

        #Querying the Database with Filters
        query = f"""
            SELECT bus_names, bus_types,departure_times,reaching_time,prices,ratings
            FROM bus_data 
            WHERE LOWER(From_Place) = LOWER('{selected_from_place}') 
            AND LOWER(To_Place) = LOWER('{selected_to_place}') 
            AND ratings >= {selected_rating} 
            AND STR_TO_DATE(departure_times, '%H:%i:%s') > '{selected_time}'
            AND CAST(REPLACE(prices, 'INR ', '') AS DECIMAL(10,2)) BETWEEN {min_price} AND {max_price}
        """

        
        # st.write(f"Executed Query: {query}")
        #Executing the Query and Displaying Results
        try:
            mycursor.execute(query)

            
            filtered_data = mycursor.fetchall()

            if filtered_data:
                df = pd.DataFrame(filtered_data, columns=['bus_names', 'bus_types', 'departure_times', 'reaching_time', 'prices', 'ratings'])
                st.markdown(f"### <span style='color:white'> Bus Details for {selected_from_place} to {selected_to_place}</span>", unsafe_allow_html=True)
                st.write(df)
            else:
                st.write("No buses found with the selected filters.")
        
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")