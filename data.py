"""Static content used across the MediNav AI Streamlit app."""

FEATURES = [
    ("🏥", "Hospital Finder", "Find nearby hospitals instantly, filtered by department and rating."),
    ("📱", "Indoor Navigation", "QR-code based indoor navigation gets you to the right room, floor by floor."),
    ("🩺", "Doctor Finder", "Search doctors by specialization, hospital, and language spoken."),
    ("📅", "Appointment Booking", "Book appointments online in a few clicks, no phone queue required."),
    ("🤖", "AI Health Assistant", "A chatbot that answers healthcare questions and routes you to the right care."),
    ("🚨", "Emergency SOS", "One tap emergency support that alerts the nearest hospital and an ambulance."),
    ("🌐", "Multi-language Support", "Use MediNav AI in English, Hindi, or Telugu."),
    ("📄", "Medical Reports", "Store and manage your medical reports securely in one place."),
    ("💊", "Pharmacy Locator", "Find nearby pharmacies stocking your prescribed medicine."),
    ("🚑", "Ambulance Tracking", "Track your ambulance live from dispatch to arrival."),
]

HOSPITALS = [
    {"name": "Sunrise Multispecialty Hospital", "location": "Banjara Hills, Hyderabad", "rating": 4.7,
     "depts": ["Cardiology", "Orthopedics", "Pediatrics"], "open": True},
    {"name": "Horizon Care Institute", "location": "Gachibowli, Hyderabad", "rating": 4.5,
     "depts": ["Neurology", "Oncology", "ENT"], "open": True},
    {"name": "Lakeview General Hospital", "location": "Kukatpally, Hyderabad", "rating": 4.3,
     "depts": ["General Medicine", "Dermatology"], "open": False},
    {"name": "Pulse Heart & Vascular Center", "location": "Jubilee Hills, Hyderabad", "rating": 4.8,
     "depts": ["Cardiology", "Vascular Surgery"], "open": True},
    {"name": "Meridian Children's Hospital", "location": "Madhapur, Hyderabad", "rating": 4.6,
     "depts": ["Pediatrics", "Neonatology"], "open": True},
    {"name": "Northgate Trauma Center", "location": "Secunderabad, Hyderabad", "rating": 4.4,
     "depts": ["Trauma", "Orthopedics", "General Medicine"], "open": True},
]

DOCTORS = [
    {"name": "Dr. Aisha Rao", "spec": "Cardiology", "hospital": "Sunrise Multispecialty Hospital",
     "exp": "14 yrs", "langs": ["English", "Hindi"], "avail": "Mon–Fri", "initials": "AR"},
    {"name": "Dr. Rohan Mehta", "spec": "Orthopedics", "hospital": "Northgate Trauma Center",
     "exp": "9 yrs", "langs": ["English", "Hindi", "Telugu"], "avail": "Tue–Sat", "initials": "RM"},
    {"name": "Dr. Sara Thomas", "spec": "Pediatrics", "hospital": "Meridian Children's Hospital",
     "exp": "11 yrs", "langs": ["English", "Telugu"], "avail": "Mon–Sat", "initials": "ST"},
    {"name": "Dr. Vikram Iyer", "spec": "Neurology", "hospital": "Horizon Care Institute",
     "exp": "17 yrs", "langs": ["English", "Hindi"], "avail": "Wed–Sun", "initials": "VI"},
    {"name": "Dr. Priya Nair", "spec": "Dermatology", "hospital": "Lakeview General Hospital",
     "exp": "7 yrs", "langs": ["English", "Telugu"], "avail": "Mon–Fri", "initials": "PN"},
    {"name": "Dr. Daniel Cho", "spec": "Oncology", "hospital": "Horizon Care Institute",
     "exp": "19 yrs", "langs": ["English"], "avail": "Mon–Thu", "initials": "DC"},
]

FAQS = [
    ("Is MediNav AI free to use?",
     "Yes, creating an account and using hospital search, doctor finder, and the AI assistant is free for patients."),
    ("How accurate is the indoor navigation?",
     "MediNav AI maintains a 98% average navigation accuracy across connected hospitals, using QR-anchored indoor maps."),
    ("Does the AI assistant give medical diagnoses?",
     "No. The assistant offers general guidance and points you to the right specialist, but it never replaces a licensed doctor."),
    ("Which hospitals are supported?",
     "MediNav AI is connected to 420+ hospitals and growing, with new locations added every month."),
]

CHAT_RESPONSES = [
    (["fever"], "Fever can come from many causes. Stay hydrated and rest. If it stays above 102°F, lasts more "
                 "than 2 days, or comes with severe symptoms, see a General Medicine doctor — check the Doctors page."),
    (["cardio", "heart"], "The nearest available cardiologist is Dr. Aisha Rao at Sunrise Multispecialty Hospital, "
                           "available Mon–Fri. You can book her from the Doctors page."),
    (["timing", "hours", "open"], "Most MediNav-connected hospitals are open 24/7 for emergencies. Outpatient "
                                   "departments typically run 8 AM – 8 PM. Check a hospital's card for exact status."),
    (["diabetes"], "Diabetes is a condition where the body can't properly regulate blood sugar, either from "
                    "insufficient insulin (Type 1) or insulin resistance (Type 2). It's managed with diet, "
                    "medication, and regular checkups with an endocrinologist."),
    (["emergency", "ambulance"], "For emergencies, open the Emergency page and tap the SOS button. It alerts the "
                                  "nearest hospital and dispatches an ambulance to your location."),
    (["appointment", "book"], "You can book an appointment from any hospital or doctor card on the Hospitals or "
                               "Doctors page — you'll need to be logged in first."),
]

DEFAULT_REPLY = ("Thanks for sharing that. For a precise answer, could you tell me a bit more — is this about a "
                  "symptom, a doctor, or a hospital service?")


def get_bot_reply(text: str) -> str:
    lower = text.lower()
    for keywords, reply in CHAT_RESPONSES:
        if any(k in lower for k in keywords):
            return reply
    return DEFAULT_REPLY
