import pandas as pd

def clean_diabetes_data(data: list) -> pd.DataFrame:
    df = pd.DataFrame(data)
    
    # Удаляем записи без patient_id
    if 'patient_id' in df.columns:
        df = df.dropna(subset=['patient_id'])
    
    # Удаляем записи без уровня глюкозы
    if 'glucose_level' in df.columns:
        df = df[df['glucose_level'].notna()]
    
    # Удаляем некорректный возраст (отрицательный или больше 120)
    if 'age' in df.columns:
        df = df[(df['age'] >= 0) & (df['age'] <= 120)]
    
    return df


if __name__ == "__main__":
    raw_data = [
        {"patient_id": "P001", "glucose_level": 7.8, "age": 45, "status": "prediabetes"},
        {"patient_id": None, "glucose_level": 5.5, "age": 30, "status": "normal"},
        {"patient_id": "P002", "glucose_level": None, "age": 50, "status": "unknown"},
        {"patient_id": "P003", "glucose_level": 9.1, "age": -5, "status": "diabetes"},
    ]
    
    print(clean_diabetes_data(raw_data))

from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}