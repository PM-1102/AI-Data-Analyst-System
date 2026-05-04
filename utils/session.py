import streamlit as st


class SessionManager:

    @staticmethod
    def init():
        defaults = {
            "page": "Upload",
            "df": None,
            "clean_df": None,
            "chat_history": [],
            "file_info": None
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    @staticmethod
    def set_page(page_name):
        st.session_state.page = page_name

    @staticmethod
    def get_page():
        return st.session_state.page

    @staticmethod
    def get_df():
        return st.session_state.df

    @staticmethod
    def set_df(df):
        st.session_state.df = df

    @staticmethod
    def get_clean_df():
        return st.session_state.clean_df

    @staticmethod
    def set_clean_df(df):
        st.session_state.clean_df = df


# Convenience functions for direct imports
def get_df():
    """Get raw dataframe from session"""
    return SessionManager.get_df()


def get_clean_df():
    """Get cleaned dataframe from session"""
    return SessionManager.get_clean_df()