MOBILE_CAPS = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:udid": "jb4xaa45q4jzinjf",
    # במקום הנתיב לקובץ ההתקנה, אנחנו משתמשים בשם החבילה שכבר מותקנת:
    "appium:appPackage": "com.atidcollege.atidexpensetracker",
    "appium:appActivity": ".MainActivity",
    "appium:autoGrantPermissions": True
}

APPIUM_SERVER = "http://127.0.0.1:4723" 
TIMEOUT = 10



# def get_capabilities():
#     """
#     מחזיר את הגדרות המכשיר (Capabilities) מנותקות מהקוד.
#     מחשב אוטומטית את הנתיב היחסי ל-APK כדי שיעבוד בכל מחשב.
#     """
#     # חישוב הנתיב לשורש הפרויקט (3 רמות למעלה מ-data/mobile)
#     project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


    
#     # ודא שה-APK אכן יושב בשורש הפרויקט, או עדכן את התיקייה כאן:
#     apk_path = mobile_apk_path  # נתיב דינמי ל-APK מתוך הקונפיג

#     caps = {
#         "platformName": "Android",
#         "appium:automationName": "UiAutomator2",
#         "appium:app": apk_path,
#         # אפשר להוסיף כאן בעתיד עוד הגדרות אם נצטרך (כמו deviceName וכו')
#     }
    
#     return caps