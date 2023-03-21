import os
import streamlit as st
import openai

#------------------------page-Detail------------------------

st.title('不動産AIコンシェルジュ')
st.write('AIコンシェルジュです。不動産についてなんでも聞いてください。連続しての質問も可能です。',)

OA_API_KEY = st.secrets['server']['openai_service_account']
openai.api_key = OA_API_KEY 

question = st.text_input("こちらに記入してください。")

if "count" not in st.session_state:
    st.session_state["count"]=0
else:
    st.session_state["count"]+=1

st.session_state["question"+str(st.session_state["count"])]= question

st_messages=[]
for i in range(st.session_state["count"]):
    if divmod(i,2) == 0:
        st_messages.append({"role": "user", "content": st.session_state["question"+str(i)]})
    else:
        st_messages.append({"role": "assistant", "content": st.session_state["question"+str(i)]})


if st.button('AIの答えを出力'):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=st_messages
    )

    st.write(response["choices"][0]["message"]["content"])