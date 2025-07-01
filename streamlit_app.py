import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import hashlib
import json

# Инициализация состояния сессии
def init_session():
    if 'groups' not in st.session_state:
        st.session_state.groups = {}
    if 'expenses' not in st.session_state:
        st.session_state.expenses = {}
    if 'members' not in st.session_state:
        st.session_state.members = {}
    if 'current_group' not in st.session_state:
        st.session_state.current_group = None

# Функция для расчета долгов
def calculate_debts(group_id):
    members = st.session_state.members.get(group_id, [])
    expenses = st.session_state.expenses.get(group_id, [])
    
    if not members or not expenses:
        return []
    
    total_expenses = sum(float(e['amount']) for e in expenses)
    per_person = total_expenses / len(members)
    
    balances = {m: -per_person for m in members}
    
    for e in expenses:
        if e['payer'] in balances:
            balances[e['payer']] += float(e['amount'])
    
    debtors = []
    creditors = []
    
    for member, balance in balances.items():
        if balance < -0.01:
            debtors.append({'member': member, 'amount': -balance})
        elif balance > 0.01:
            creditors.append({'member': member, 'amount': balance})
    
    debtors.sort(key=lambda x: x['amount'], reverse=True)
    creditors.sort(key=lambda x: x['amount'], reverse=True)
    
    transactions = []
    d_index = 0
    c_index = 0
    
    while d_index < len(debtors) and c_index < len(creditors):
        debtor = debtors[d_index]
        creditor = creditors[c_index]
        amount = min(debtor['amount'], creditor['amount'])
        
        transactions.append({
            'from': debtor['member'],
            'to': creditor['member'],
            'amount': round(amount, 2)
        })
        
        debtor['amount'] -= amount
        creditor['amount'] -= amount
        
        if debtor['amount'] < 0.01:
            d_index += 1
        if creditor['amount'] < 0.01:
            c_index += 1
    
    return transactions

# Главная функция
def main():
    st.set_page_config(
        page_title="Trata - Управление групповыми расходами",
        page_icon="💰",
        layout="wide"
    )
    
    init_session()
    
    # CSS стили
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            background-attachment: fixed;
            min-height: 100vh;
        }
        .stButton>button {
            background: linear-gradient(to right, #6a11cb, #2575fc) !important;
            color: white !important;
            border: none !important;
            border-radius: 50px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(106, 17, 203, 0.3) !important;
            transition: all 0.3s !important;
        }
        .stButton>button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 7px 20px rgba(106, 17, 203, 0.4) !important;
        }
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {
            border-radius: 50px !important;
            padding: 10px 15px !important;
            border: 2px solid #ddd !important;
        }
        .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stSelectbox>div>div>select:focus {
            border-color: #6a11cb !important;
            box-shadow: 0 0 0 3px rgba(106, 17, 203, 0.2) !important;
        }
        .card {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 20px !important;
            padding: 25px !important;
            margin-bottom: 20px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .debtor {
            color: #ff4757;
            font-weight: 600;
        }
        .creditor {
            color: #2ed573;
            font-weight: 600;
        }
        .amount-badge {
            background: linear-gradient(45deg, #6a11cb, #2575fc);
            color: white;
            padding: 2px 10px;
            border-radius: 20px;
            font-weight: 600;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Главная страница - создание группы
    if st.session_state.current_group is None:
        st.markdown("<div style='text-align: center; margin-bottom: 30px;'>", unsafe_allow_html=True)
        st.markdown("<div class='logo' style='width: 140px; height: 140px; background: linear-gradient(45deg, #6a11cb, #2575fc); border-radius: 50%; margin: 0 auto 30px; display: flex; align-items: center; justify-content: center; font-size: 50px; color: white; font-weight: bold;'>💰</div>", unsafe_allow_html=True)
        st.title("Создайте новую компанию")
        st.markdown("</div>", unsafe_allow_html=True)
        
        group_name = st.text_input("Введите название компании", max_chars=50, placeholder="Название компании")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Создать группу", use_container_width=True):
                if group_name:
                    group_id = str(uuid.uuid4())
                    st.session_state.groups[group_id] = {
                        'name': group_name,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.expenses[group_id] = []
                    st.session_state.members[group_id] = []
                    st.session_state.current_group = group_id
                    st.experimental_rerun()
                else:
                    st.error("Введите название компании!")
        
        with col2:
            if st.button("Пригласить", use_container_width=True):
                if group_name:
                    group_id = str(uuid.uuid4())
                    st.session_state.groups[group_id] = {
                        'name': group_name,
                        'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.expenses[group_id] = []
                    st.session_state.members[group_id] = []
                    st.session_state.current_group = group_id
                    st.experimental_rerun()
                else:
                    st.error("Введите название компании!")
    
    # Страница группы
    else:
        group_id = st.session_state.current_group
        group = st.session_state.groups[group_id]
        
        # Шапка
        st.markdown("<div class='header'>", unsafe_allow_html=True)
        st.title(group['name'])
        if st.button("Пригласить участников"):
            invite_url = f"https://your-domain.com/group/{group_id}"
            st.code(invite_url, language="text")
            st.success("Ссылка скопирована в буфер обмена!")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Участники
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Участники")
            
            members = st.session_state.members[group_id]
            if members:
                cols = st.columns(4)
                for i, member in enumerate(members):
                    with cols[i % 4]:
                        st.markdown(f"""
                            <div style="
                                background: linear-gradient(45deg, #6a11cb, #2575fc);
                                color: white;
                                padding: 10px;
                                border-radius: 10px;
                                text-align: center;
                                margin-bottom: 10px;
                                position: relative;
                            ">
                                {member}
                                <button style="
                                    position: absolute;
                                    top: 5px;
                                    right: 5px;
                                    background: none;
                                    border: none;
                                    color: white;
                                    cursor: pointer;
                                    font-size: 16px;
                                " onclick="alert('Удалить участника?')">×</button>
                            </div>
                        """, unsafe_allow_html=True)
            
            new_member = st.text_input("Введите имя участника", key="new_member")
            if st.button("Добавить участника"):
                if new_member:
                    st.session_state.members[group_id].append(new_member)
                    st.experimental_rerun()
                else:
                    st.error("Введите имя участника!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Траты
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Траты")
            
            expenses = st.session_state.expenses[group_id]
            if expenses:
                df = pd.DataFrame(expenses)
                df = df[['description', 'payer', 'amount', 'date']]
                st.dataframe(
                    df.style.format({'amount': '{:.2f} ₽'}),
                    use_container_width=True,
                    hide_index=True
                )
            
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                expense_desc = st.text_input("Описание траты", key="expense_desc")
            with col2:
                expense_amount = st.number_input("Сумма", min_value=0.01, step=0.01, format="%.2f", key="expense_amount")
            with col3:
                payer = st.selectbox("Кто оплатил?", st.session_state.members[group_id], key="payer")
            
            if st.button("Добавить трату"):
                if expense_desc and expense_amount:
                    new_expense = {
                        'id': str(uuid.uuid4()),
                        'description': expense_desc,
                        'amount': float(expense_amount),
                        'payer': payer,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.expenses[group_id].append(new_expense)
                    st.experimental_rerun()
                else:
                    st.error("Заполните описание и сумму!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Расчет долгов
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("Расчет долгов")
            
            transactions = calculate_debts(group_id)
            if transactions:
                st.markdown("**Для погашения долгов:**")
                for t in transactions:
                    st.markdown(f"""
                        <div style="
                            padding: 10px;
                            margin: 10px 0;
                            background: white;
                            border-radius: 10px;
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                        ">
                            <span class="debtor">{t['from']}</span> должен 
                            <span class="creditor">{t['to']}</span>
                            <span class="amount-badge">{t['amount']} ₽</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Нет долгов для расчета или недостаточно данных")
            
            if st.button("Пересчитать долги"):
                st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
