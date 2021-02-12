import streamlit as st
import pandas as pd
import datetime
import math
import plotly.express as px
from PIL import Image


class county:
    def __init__(self, fips_dataset, population_dataset, zipcode, date_):
        county_array = get_data(get_fips(fips_dataset, zipcode), date_)
        # print("county array " + str(county_array))
        # print(county_array)
        if county_array == [' ', ' ', ' ', ' ', ' ', ' ', ' ']:
            county_array = [["none", "None", "None", 0, 0, 0]]
        self.date = date_
        self.name = get_county_name(fips_dataset, zipcode)
        self.state = abbrev_us_state[(get_state_abbrev(fips_dataset, zipcode))]
        self.fips = county_array[0][1]
        self.cases = county_array[0][7]
        self.deaths = county_array[0][8]

        population_array = population_dataset[(population_dataset["STNAME"] == self.state) & (
                population_dataset["CTYNAME"] == self.name)].values.tolist()
        self.population_2010 = population_array[0][18]
        self.population_2019 = population_array[0][18]
        self.zipcode = zipcode

    def get_date(self):
        return self.date

    def get_name(self):
        return self.name

    def get_state(self):
        return self.state

    def get_fips(self):
        return self.fips

    def get_cases(self):
        return self.cases

    def get_deaths(self):
        return self.deaths

    def get_population(self):
        return self.population_2019

    def get_zipcode(self):
        return self.zipcode


# functions


def get_data(fips, date):
    JH_County_Data = pd.read_csv(
        'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/' + date + '.csv')

    info = JH_County_Data[(JH_County_Data["FIPS"] == fips)].values.tolist()
    # print("info from get data:" + str(info))
    return info


def get_fips(dataset, zip_number):
    """

    :param dataset: pandas dataframe
    :type zip_number: String
    """
    data = dataset[dataset["ZIP"] == int(zip_number)].values.tolist()
    # print(data)
    return data[0][1]


def get_county_name(dataset, zip_number):
    data = dataset[dataset["ZIP"] == int(zip_number)].values.tolist()
    # print(data)
    return data[0][4]


def get_state_abbrev(dataset, zip_number):
    data = dataset[dataset["ZIP"] == int(zip_number)].values.tolist()
    # print(data)
    return data[0][3]


def remove(string, start, stop):  # code adapted from thispointer.com
    if len(string) > stop:
        string = string[0: start:] + string[stop + 1::]
    return string


us_state_abbrev = {
    # this is a python dictionary made by Roger Allen, the dictionary allow easy conversion form state
    # abbreviations to state full names
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands': 'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}
abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

zip_codes_data = pd.read_csv('zip_codes.csv')
population_data = pd.read_csv('county_population_estimate.csv', encoding='latin-1')


def circulating_cases(county_variable, bias, time_delta):
    # manipulate date to fit the JH-Data base format
    month = int(remove(county_variable.get_date(), 2, 9))  # extracting differnt parts of the date
    day = int(remove(remove(county_variable.get_date(), 0, 2), 2, 6))
    year = int(remove(county_variable.get_date(), 0, 5))
    # print(month)
    # print(day)
    # print(year)
    date = datetime.datetime(year, month, day)
    date_delta = datetime.timedelta(time_delta)
    date = date - date_delta

    # print("date after detla:", date)
    # print(date.strftime('%m-%d-%Y'))
    county_prior = county(zip_codes_data, population_data, county_variable.get_zipcode(), date.strftime('%m-%d-%Y'))

    # calculate circulating case estimate

    circulating_cases = (county_variable.get_cases() - county_prior.get_cases()) * bias

    # print(county_variable.get_cases())
    # print(county_prior.get_cases())
    return (circulating_cases)


# main code
def exposure_risk(community, establishment_population):
    total_cases = circulating_cases(community, 10, 14) * 0.2
    population = community.get_population()
    r_exposure = (1 - pow(1 - (total_cases / population), establishment_population))
    return r_exposure


class venue():
    """
    RNA_50_percent = 316
    deposition_probability = 0.5
    emission_breathing = 0.06
    emission_speaking = 0.6
    speaking_breathing_ratio = 0.1
    respiratory_rate = 10
    respiratory_fluid_RNA_conc = 5.00 * pow(10, 8)
    mean_wet_aerosol_diameter = 5  # um
    virus_lifetime_in_aerosol = 1.7
    duration = 12
    # vars that will change

    infectious_episode = 2  # days
    room_area = 60
    room_height = 3

    room_ventilation_rate = 2
    total_face_mask_efficiency = 0
    """

    def __init__(self, RNA_50_percent, deposition_probability, emission_breathing, emission_speaking,
                 speaking_breathing_ratio, respiratory_rate, respiratory_fluid_RNA_conc, mean_wet_aerosol_diameter,
                 virus_lifetime_in_aerosol, infectious_episode, room_area, room_height, room_ventilation_rate,
                 total_face_mask_efficiency):
        self.RNA_50_percent = RNA_50_percent
        self.deposition_probability = deposition_probability
        self.emission_breathing = emission_breathing
        self.emission_speaking = emission_speaking
        self.speaking_breathing_ratio = speaking_breathing_ratio
        self.respiratory_rate = respiratory_rate
        self.respiratory_fluid_RNA_conc = respiratory_fluid_RNA_conc
        self.mean_wet_aerosol_diameter = mean_wet_aerosol_diameter
        self.virus_lifetime_in_aerosol = virus_lifetime_in_aerosol

        self.infectious_episode = infectious_episode
        self.room_area = room_area
        self.room_height = room_height

        self.room_ventilation_rate = room_ventilation_rate
        self.total_face_mask_efficiency = total_face_mask_efficiency


def contract_risk(ven, establishment_population, hours):
    RNA_50_percent = 316
    deposition_probability = 0.5
    emission_breathing = 0.06
    emission_speaking = 0.6
    speaking_breathing_ratio = 0.1
    respiratory_rate = 10
    respiratory_fluid_RNA_conc = 5.00 * pow(10, 8)
    mean_wet_aerosol_diameter = 5
    virus_lifetime_in_aerosol = 1.7

    # vars that will change

    infectious_episode = 2  # days
    room_area = 60
    room_height = 3

    room_ventilation_rate = 2
    total_face_mask_efficiency = 0.7
    susceptible_number_persons = 24

    duration = 12
    # normalized results - adapted from  Max Planck Institute for Chemistry

    infection_probability = 1 - pow(10, (math.log(0.5, 10)) / ven.RNA_50_percent)

    RNA_content_in_aerosol = ven.respiratory_fluid_RNA_conc * 0.5 * pow((ven.mean_wet_aerosol_diameter / 10000), 3)

    aerosol_emission = (ven.emission_breathing * (
            1 - ven.speaking_breathing_ratio) + ven.emission_speaking * ven.speaking_breathing_ratio) * 1000 * ven.respiratory_rate * 60

    steady_state_aerosol_conc = aerosol_emission / (ven.room_area * ven.room_height * 1000)
    steady_state_RNA_cont_aerosal_conc = RNA_content_in_aerosol * steady_state_aerosol_conc
    RNA_dosis = ven.respiratory_rate * 60 * steady_state_RNA_cont_aerosal_conc * ven.deposition_probability

    dosis_duration_hours = RNA_dosis / (ven.room_ventilation_rate + 1 / ven.virus_lifetime_in_aerosol) * (
            1 - ven.total_face_mask_efficiency) * hours
    dosis_infectious_episode = ven.infectious_episode * dosis_duration_hours
    r_contract = (1 - pow(pow(1 - infection_probability, dosis_infectious_episode),
                          establishment_population)) * 100

    return (r_contract)


def transmission_risk(county, establishment, establishment_population, duration):
    return exposure_risk(county, establishment_population) * contract_risk(establishment, establishment_population,
                                                                           duration)


# code for App ________________________________________________

st.title("COVID-19 Transmission Risk Predictor")

st.markdown("""
<style>
   body {
    color: #111;
    background-image: linear-gradient(180deg, #2af598 0%, #009efd 100%);
    background-color: #8FC1E3;
  }
/*
 .css-1aumxhk {
    background-color: #5085A5;
    background-image: none;
    color: #111; 
}

.css-145kmo2 {
    font-size: 0.8rem;
    color: #fff;
    margin-bottom: 0.4rem;
}
.st-bm {
    color: #000;
}
.st-ek {
    color: #fff;
}
*/
</style>
 """, unsafe_allow_html=True)
# 6b9de3
# 011839
st.header("This web app uses probabilistic modeling to predict the transmission risk when visiting a venue.")

st.markdown(
    '''
    Please Enter your Event-Related, Venue-Related, and Personal factors on the side bar to the left. Explanations for each factor are given. Web app created by Daiwik Pal. 
    '''
)

# Covid - 19 related information
RNA_50_percent = 316
deposition_probability = 0.5
emission_breathing = 0.06
emission_speaking = 0.6

respiratory_rate = 10
respiratory_fluid_RNA_conc = 5.00 * pow(10, 8)
mean_wet_aerosol_diameter = 5
virus_lifetime_in_aerosol = 1.7
infectious_episode = 2
# vars that will change

# venue releated factor(s):
room_area = 100
room_height = 4
room_ventilation_rate = 2

# event releated factor(s)
susceptible_number_persons = 20
duration = 9
speaking_breathing_ratio = 0.6

# personal factor(s)
total_face_mask_efficiency = 0

zipcode = st.sidebar.text_input('What is your zipcode?')

st.sidebar.subheader('Event Related Factors:')
susceptible_number_persons = st.sidebar.number_input('How many people will be at the venue?', 0)
duration = st.sidebar.number_input('How long will you attend the venue? (Hours)')
speaking_breathing_ratio = st.sidebar.slider("What percentage of the time during your visit do you expect to speak?", 1,
                                             100, 0) / 100
st.sidebar.write(round(speaking_breathing_ratio * 100))
with st.sidebar.beta_expander("More Information", False):
    st.write('''
    #### Total Number of People: 
    The total number of people at the venue is used when calculating the risk that an individual might get exposed to a carrier of the virus (*Exposure Risk*). 
    
    #### Duration: 
    The longer one stays at the venue the more chance they have of meeting a carrier and more dosis they inhale. In these trying times it is best to visit a venue for as short of a time as possible. 
    
    #### Speaking Ratio: 
    This factor is used to determine the the number or dosis of the virus you may inhale during your visit. When speaking, individuals tend to inhale aerosols, which is why is it is used to calculate the total dosage inhaled the visit. 
    ''')

st.sidebar.subheader("Venue Related Factors:")
room_area = st.sidebar.number_input('Enter Room Area in Squared Feet', 0) * 0.0929
room_height = st.sidebar.number_input('Enter Room Height in Feet', 0) * 0.3048
room_ventilation_radio = st.sidebar.radio('Room Ventilation', ["No Ventilation", "Some Ventilation", "Public Area"])

if room_ventilation_radio == "No Ventilation":
    room_ventilation_rate = 0
elif room_ventilation_radio == "Some Ventilation":
    room_ventilation_rate = 2
else:
    room_ventilation_rate = 6
st.sidebar.write(room_ventilation_rate)

st.sidebar.subheader("Personal Factors")
total_face_mask_efficiency_radio = st.sidebar.radio("What mask will you be using?",
                                                    ["No Mask", "Normal Mask", "Surgical Mask"])

if total_face_mask_efficiency_radio == "No Mask":
    total_face_mask_efficiency = 0
elif total_face_mask_efficiency_radio == "Normal Mask":
    total_face_mask_efficiency = 0.2
else:
    total_face_mask_efficiency = 0.5

st.sidebar.write(total_face_mask_efficiency)

zip_codes_data = pd.read_csv('zip_codes.csv')
population_data = pd.read_csv('county_population_estimate.csv', encoding='latin-1')
timeDelta = datetime.timedelta(2)
now = datetime.datetime.now() - timeDelta
dateString = now.strftime("%m-%d-%Y")
# creating the community and establishment objects

# Calculate Transmission Risk Button (Individual)
st.header("Calculate Transmission Risk:")
run_button = st.button('Calculate Transmission Risk')
if run_button:
    if not zipcode or not (zipcode.isnumeric()) or room_area == 0 or room_height == 0:
        st.warning('Please enter a valid zipcode or provide a non-zero value for room dimensions!')
        st.stop()
    community = county(zip_codes_data, population_data, zipcode, dateString)
    establishment = venue(RNA_50_percent, deposition_probability, emission_breathing, emission_speaking,
                          speaking_breathing_ratio, respiratory_rate, respiratory_fluid_RNA_conc,
                          mean_wet_aerosol_diameter, virus_lifetime_in_aerosol, infectious_episode, room_area,
                          room_height, room_ventilation_rate, total_face_mask_efficiency)
    r_transmission = transmission_risk(community, establishment, susceptible_number_persons, duration)

    st.subheader(community.get_name() + ", " + community.get_state())

    if 0 <= r_transmission < 10:
        st.success("***Predicted Risk: VERY LOW***")
    elif 10 <= r_transmission < 30:
        st.success("***Predicted Risk: LOW***")
    elif 30 <= r_transmission < 60:
        st.warning("***Predicted Risk: MEDIUM***")
    elif 60 <= r_transmission < 70:
        st.error("***Predicted Risk: HIGH***")
    elif 70 <= r_transmission < 85:
        st.error("***Predicted Risk: VERY HIGH***")
    elif 85 <= r_transmission <= 100:
        st.error("***Predicted Risk: EXTREME***")
    # st.beta_expander()
    st.write("Predicted Transmission Risk: " + str(round(r_transmission * 100) / 100))

st.header("Transmission Risk Comparison:")
st.write(
    "This section will help you contextualize the transmission risk prediction you received based on varied venue population sizes.")

Graph_button = st.button("Generate Graph:")

if Graph_button:
    if not zipcode or not (zipcode.isnumeric()) or room_area == 0 or room_height == 0:
        st.warning('Please enter a valid zipcode or provide a non-zero value for room dimensions!')
        st.stop()
    community = county(zip_codes_data, population_data, zipcode, dateString)
    establishment = venue(RNA_50_percent, deposition_probability, emission_breathing, emission_speaking,
                          speaking_breathing_ratio, respiratory_rate, respiratory_fluid_RNA_conc,
                          mean_wet_aerosol_diameter, virus_lifetime_in_aerosol, infectious_episode, room_area,
                          room_height, room_ventilation_rate, total_face_mask_efficiency)
    data = {
        'Transmission Risk': [],
        'Population': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 300, 400, 500, 600, 700,
                       800, 900, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 10000, 50000, 70000, 100000,
                       susceptible_number_persons]
    }

    my_bar = st.progress(0)
    progress_var = 0
    for i in range(0, len(data['Population'])):
        data['Transmission Risk'].append(transmission_risk(community, establishment, data['Population'][i], duration))
        my_bar.progress((i + 1) / len(data['Population']))

    df = pd.DataFrame(data=data)

    fig = px.scatter(df, x='Population', y='Transmission Risk', log_x=True, range_x=[1, 100000], range_y=[0, 110])

    fig.add_hrect(y0=0, y1=30, line_width=0, fillcolor="green", opacity=0.2)
    fig.add_hrect(y0=30, y1=60, line_width=0, fillcolor="yellow", opacity=0.2)
    fig.add_hrect(y0=60, y1=100, line_width=0, fillcolor="red", opacity=0.2)


    st.plotly_chart(fig, use_container_width=True)
    with st.beta_expander('More Information:'):
        st.table(data)

# with st.beta_expander("How does the Transmission Risk Model work?", False):
# st.write('''
# #### This is where the explanations with latex equations and stuff will go
# ''')
