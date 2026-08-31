import streamlit as st

def app():
    st.header('WaterBuddy Premium')
    st.write('Upgrade for advanced reminders, cloud sync, export, and themes.')

    st.markdown('''
- Scheduled reminders (customizable)
- Cross-device sync (coming soon)
- CSV export of your hydration history
- Priority support
''')

    st.button('Upgrade — Contact us')
    st.info('This demo contains placeholders for premium features. Integrations require backend services or third-party APIs.')
