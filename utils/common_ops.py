import csv
import json

def read_data_from_csv(file_path):
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

#for performance analysis in test_e2e_web.py
def calc_performance(times: list) -> dict:
    sorted_t = sorted(times)
    n = len(times)
    return {
        "avg":         sum(times) / n,
        "p95":         sorted_t[int(n * 0.95) - 1],
        "min":         sorted_t[0],
        "max":         sorted_t[-1],
        "degradation": (sum(times[-5:]) / 5) / (sum(times[:5]) / 5) - 1
    }




def load_test_data(file_path):
    """
    פונקציה גנרית לטעינת נתונים מקובץ JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    