import pandas as pd
from diabetes_etl import clean_diabetes_data

def test_clean_diabetes_data():
    raw_data = [
        {"patient_id": "P001", "glucose_level": 7.8, "age": 45, "status": "prediabetes"},
        {"patient_id": None, "glucose_level": 5.5, "age": 30, "status": "normal"},
        {"patient_id": "P002", "glucose_level": None, "age": 50, "status": "unknown"},
        {"patient_id": "P003", "glucose_level": 9.1, "age": -5, "status": "diabetes"},
    ]
    
    df = clean_diabetes_data(raw_data)
    
    # Должна остаться только одна валидная запись
    assert len(df) == 1
    
    # Проверяем значения
    assert df.iloc[0]['patient_id'] == "P001"
    assert df.iloc[0]['glucose_level'] == 7.8
    assert df.iloc[0]['age'] == 45
    assert df.iloc[0]['status'] == "prediabetes"