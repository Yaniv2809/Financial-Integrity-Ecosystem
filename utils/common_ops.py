import csv
import json

def read_data_from_csv(file_path):
    """
    Read data from CSV or JSON files and return as list of tuples for pytest parametrize.
    For JSON files, returns list of tuples from the JSON array objects.
    """
    # Check if it's a JSON file
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            json_data = json.load(jsonfile)
            data = []
            if isinstance(json_data, list) and len(json_data) > 0:
                # Get keys from the first object to maintain order
                keys = list(json_data[0].keys())
                for item in json_data:
                    # Create tuple from values in the order of keys
                    values = tuple(item.get(key, '') for key in keys)
                    data.append(values)
            return data
    
    # Otherwise treat as CSV
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data


def read_data_from_csv_by_test(file_path, test_id):
    all_data = read_data_from_csv(file_path)
    return [row for row in all_data if row.get("test_id") == test_id]

def read_json_data_by_test(file_path, test_id):
    """
    קורא נתונים מקובץ JSON, שומר עליהם כמילונים (Dictionaries),
    ומסנן רק את הבלוק ששייך לטסט הספציפי.
    """
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        all_data = json.load(f)
        
    # מחזיר רשימה של מילונים שבהם ה-test_id תואם למה שביקשנו
    return [row for row in all_data if isinstance(row, dict) and row.get("test_id") == test_id]


#for performance analysis in test_e2e
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
    