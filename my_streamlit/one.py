import streamlit as st 

st.write('hello there!')

# make random dataframe 
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.randn(50, 20), columns=('col%d' % i for i in range(20)))

st.line_chart(data=df, width=0, height=0, use_container_width=True,x='col1', y='col2')

# make matplotlib chart of df 

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.scatter(df['col1'], df['col2'])
fig # make streamlit plot it -> magic 


st.write('another df ')
st.dataframe(df)

st.write('some stylish df')
st.dataframe(df.style.highlight_max(axis=0))

st.write('now a static table only 10 rows though lmao ')
st.table(df.iloc[:10])


# widgets 

x = st.slider('x') 
st.write(x, 'squared is', x * x)


st.write('your name is  ')
st.text_input("Your name", key="name")
# You can access the value at any point with:
st.write('your name is ' + st.session_state.name)


st.write('checkbos ')

if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    chart_data
    
    
st.write('select an option ')

df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })

option = st.selectbox(
    'Which number do you like best?',
     df['first column'])

'You selected: ', df['second column'].iloc[int(option)]


st.write('sidebar !  ')

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox(
    'How would you like to be contacted?',
    ('Email', 'Home phone', 'Mobile phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider(
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)

# Display the chosen values:
st.write('You selected this option: ', add_selectbox)
st.write('You selected this range of values: ', add_slider)