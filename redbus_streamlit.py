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

if mydb.is_connected():
    st.markdown(f"## <span style='color:white'>RedBus</span>", unsafe_allow_html=True)

mycursor = mydb.cursor(buffered=True)

# Styling the App
st.markdown(
    """
    <style>
    .stApp {
        background-color:#333333; /* Dark Charcoal */
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

with st.sidebar:
    selected_page = option_menu(
        "Main Menu",
        ["Home", "Bus Criteria Form"],
        icons=['house', 'filter'],
        # menu_icon="cast",
        default_index=0,
    )

if selected_page == "Home":  
    st.markdown("<h1 style='color:white;'>Welcome to RedBus </h1>", unsafe_allow_html=True)
    st.markdown("""
    <p style='color:white;'>
    The RedBus project is designed to help users search for bus services between different cities and filter buses based on
    criteria like rating, departure time, and more. This platform integrates with a MySQL database to retrieve real-time 
    bus information and provide users with accurate and updated details.
    </p>
   
    """, unsafe_allow_html=True)

if selected_page == "Bus Criteria Form":

    mycursor.execute("SELECT DISTINCT state_names FROM bus_data")
    states = [state[0] for state in mycursor.fetchall()]

    mycursor.execute("SELECT DISTINCT From_Place FROM bus_data")
    from_places = [place[0] for place in mycursor.fetchall()]

    mycursor.execute("SELECT DISTINCT To_Place FROM bus_data")
    to_places = [place[0] for place in mycursor.fetchall()]

    with st.form("Bus Criteria Form"):  
        st.markdown(f"## <span style='color:white'>Bus Criteria Form</span>", unsafe_allow_html=True)
        
        selected_state = st.selectbox("Select State", states)

        selected_from_place = st.selectbox("Select Departure Place", from_places)
        
        selected_to_place = st.selectbox("Select Destination Place", to_places)
        
        selected_rating = st.slider('Select Minimum Bus Rating', min_value=0.0, max_value=5.0, value=3.0, step=0.1)
        
        selected_bus_type = st.selectbox("Select Bus Type", ["All", "AC", "Non-AC", "Sleeper", "Seater"])
        
        # Change: Using text input for time filter instead of slider
        selected_time_input = st.text_input("Select Departure Time (HH:MM format)", "18:00", max_chars=5)
        
        # Ensure the user input is in the correct format
        try:
            # If the user input is valid, this will pass
            selected_time = pd.to_datetime(selected_time_input, format='%H:%M').strftime('%H:%M:%S')
        except ValueError:
            st.error("Invalid time format. Please use the format HH:MM.")
            selected_time = None

        min_price, max_price = st.slider('Select Ticket Price Range', min_value=100, max_value=5000, value=(300, 2000), step=100)

        
        submit_button = st.form_submit_button(label='Submit')

    
    if submit_button:
        if selected_time:  # Only proceed if the time input is valid
            st.write("Debugging Info:")
            st.write(f"State: {selected_state}")
            st.write(f"From Place: {selected_from_place}")
            st.write(f"To Place: {selected_to_place}")
            st.write(f"Bus Type: {selected_bus_type}")
            st.write(f"Rating: {selected_rating}")
            st.write(f"Time: {selected_time}")
            st.write(f"Price Range: {min_price} - {max_price}")

            # Querying the Database with Filters
            bus_type_condition = f"AND LOWER(bus_types) = LOWER('{selected_bus_type}')" if selected_bus_type != "All" else ""
            query = f"""
                SELECT bus_names, bus_types, departure_times, reaching_time, prices, ratings,seats
                FROM bus_data 
                WHERE LOWER(state_names) = LOWER('{selected_state}')
                AND LOWER(From_Place) = LOWER('{selected_from_place}') 
                AND LOWER(To_Place) = LOWER('{selected_to_place}') 
                AND ratings >= {selected_rating} 
                AND STR_TO_DATE(departure_times, '%H:%i:%s') > '{selected_time}'
                AND CAST(REPLACE(prices, 'INR ', '') AS DECIMAL(10,2)) BETWEEN {min_price} AND {max_price}
            """

            # st.write(f"Executed Query: {query}")
            # Executing the Query and Displaying Results
            try:
                mycursor.execute(query)

                filtered_data = mycursor.fetchall()

                if filtered_data:
                    df = pd.DataFrame(filtered_data, columns=['BusName', 'BusType', 'BusDepartureTime', 'BusReachingTime', 'TicketPrice', 'BusRating','Seats'])
                    st.markdown(f"### <span style='color:white'>Filtered Bus Details for {selected_from_place} to {selected_to_place}</span>", unsafe_allow_html=True)
                    st.write(df)
                else:
                    st.write("No buses found with the selected filters.")
            
            except mysql.connector.Error as err:
                st.error(f"Error: {err}")
        else:
            st.write("Please enter a valid time.")