import os, sqlite3, math, uuid, io
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import qrcode
from PIL import Image

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / 'cleanghat.db'
UPLOAD_DIR = APP_DIR / 'uploads'
QR_DIR = APP_DIR / 'qr_codes'
UPLOAD_DIR.mkdir(exist_ok=True)
QR_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title='CleanGhat', page_icon='♻️', layout='wide')

I18N = {
 'en': {
     'title': 'CleanGhat',
     'subtitle': 'Godavari Pushkaralu 2027 · Waste Collection & Cleanliness',
     'tagline': 'PS-07: Rapid Cleanliness Reporting & Smart Operations',
     'badge_sim': 'Hackathon Prototype · Simulated Telemetry Data',
     'tab_report': '📝 Report Waste Issue',
     'tab_track': '🔍 Track Ticket Status',
     'language': 'Language / భాష / भाषा',
     'location': 'Pushkaralu Location / Ghat',
     'location_help': 'Select the ghat or public area requiring cleaning',
     'landmark': 'Landmark / Specific Spot Details (Optional)',
     'other_loc': '➕ Other / Not Listed (Custom Location)',
     'custom_loc_desc': 'Exact Location Description & Landmark (Compulsory)',
     'custom_loc_required_err': 'Location description is compulsory when selecting "Other / Not listed".',
     'custom_loc_warning': '⚠️ Notice: Custom locations are sent to the Supervisor Verification Queue. A cleaning team will NEVER be automatically dispatched until verified by a Pushkaralu supervisor.',
     'category': 'Waste Issue Category (PS-07)',
     'description': 'Additional details / Landmark description (optional)',
     'photo': 'Upload Photo of Waste (optional)',
     'contact': 'Citizen Contact Number (optional)',
     'contact_privacy': '🔒 Privacy: Your contact number is confidential for supervisor verification and will never be exposed on public tracking screens.',
     'submit': 'Submit Cleanliness Report',
     'success_verified': 'Report submitted successfully!',
     'success_custom': 'Report registered under Supervisor Verification!',
     'ticket': 'Your Ticket Number',
     'assigned_to': 'Assigned to Team',
     'est_distance': 'Straight-line distance estimate',
     'no_team_avail': 'Report recorded in dispatch queue. No cleaning team is currently available; a team will be assigned once available.',
     'custom_submitted_msg': 'Because this is an unlisted custom location, it has been forwarded to the Pushkaralu sanitation supervisor for manual verification and zone assignment. No team is auto-dispatched.',
     'ticket_lookup_title': 'Track Complaint Ticket',
     'ticket_lookup_prompt': 'Enter your ticket number to view live cleaning progress and photo proof:',
     'ticket_placeholder': 'e.g. CG-261103-XXXXXX',
     'track_button': 'Track Status',
     'ticket_not_found': 'No record found for this ticket ID. Please verify and try again.',
     'current_status': 'Current Status',
     'reported_on': 'Reported On',
     'assigned_team': 'Assigned Sanitation Team',
     'cleaning_proof': 'Cleaning Verification Photos (Before & After)',
     'no_proof_yet': 'Photographic evidence will appear here as soon as the cleaning team completes the task.',
     'status_verification': 'Awaiting Supervisor Verification',
     'status_pending': 'In Dispatch Queue (Awaiting Available Team)',
     'status_assigned': 'Team Assigned & Dispatched',
     'status_accepted': 'Accepted by Cleaning Team',
     'status_inprogress': 'Cleaning in Progress at Site',
     'status_completed': 'Cleaned & Resolved (Verified)',
     'overflow': 'Overflowing dustbin',
     'litter': 'Litter on ground',
     'accumulation': 'Waste accumulation',
     'river': 'Garbage near riverbank',
     'dirty': 'Dirty public area',
     'other': 'Other cleanliness issue',
     'no_location': 'QR location not recognised. Please choose a location from the list.',
     'submit_another': '➕ Submit Another Complaint',
     'copy_ticket_note': 'Please note down or screenshot this ticket number to track cleaning progress.'
 },
 'te': {
     'title': 'క్లీన్‌ఘాట్',
     'subtitle': 'గోదావరి పుష్కరాలు 2027 · వ్యర్థాల సేకరణ మరియు పరిశుభ్రత',
     'tagline': 'PS-07: వేగవంతమైన పరిశుభ్రత ఫిర్యాదులు మరియు నిర్వహణ',
     'badge_sim': 'నమూనా ప్రదర్శన · అనుకరణ నిర్వహణ డేటా',
     'tab_report': '📝 సమస్యను నివేదించండి',
     'tab_track': '🔍 టికెట్ స్థితిని తనిఖీ చేయండి',
     'language': 'భాష / Language / भाषा',
     'location': 'పుష్కరాల ప్రదేశం / ఘాట్',
     'location_help': 'వ్యర్థాలు ఉన్న ఘాట్ లేదా ప్రాంతాన్ని ఎంచుకోండి',
     'landmark': 'ల్యాండ్‌మార్క్ / నిర్దిష్ట ప్రాంత వివరాలు (ఐచ్ఛికం)',
     'other_loc': '➕ ఇతర / జాబితాలో లేని ప్రదేశం (కస్టమ్ లొకేషన్)',
     'custom_loc_desc': 'ఖచ్చితమైన ప్రదేశం మరియు ల్యాండ్‌మార్క్ వివరణ (తప్పనిసరి)',
     'custom_loc_required_err': 'జాబితాలో లేని ప్రదేశాన్ని ఎంచుకున్నప్పుడు ప్రదేశ వివరణ తప్పనిసరి.',
     'custom_loc_warning': '⚠️ గమనిక: జాబితాలో లేని ప్రదేశాలు సూపర్‌వైజర్ పరిశీలన జాబితాకు పంపబడతాయి. సైట్ సూపర్‌వైజర్ ధృవీకరించే వరకు పారిశుద్ధ్య బృందం ఆటోమేటిక్‌గా కేటాయించబడదు.',
     'category': 'సమస్య రకం (PS-07)',
     'description': 'అదనపు వివరాలు (ఐచ్ఛికం)',
     'photo': 'వ్యర్థాల ఫోటో అప్‌లోడ్ చేయండి (ఐచ్ఛికం)',
     'contact': 'ఫోన్ నంబర్ (ఐచ్ఛికం)',
     'contact_privacy': '🔒 గోప్యత: మీ మొబైల్ నంబర్ గోప్యంగా ఉంచబడుతుంది మరియు బహిరంగ ట్రాకింగ్ స్క్రీన్‌లలో ఎప్పుడూ చూపబడదు.',
     'submit': 'ఫిర్యాదు సమర్పించండి',
     'success_verified': 'మీ ఫిర్యాదు విజయవంతంగా నమోదు అయింది!',
     'success_custom': 'ఫిర్యాదు సూపర్‌వైజర్ పరిశీలన కొరకు నమోదు చేయబడింది!',
     'ticket': 'మీ టికెట్ నంబర్',
     'assigned_to': 'కేటాయించబడిన బృందం',
     'est_distance': 'అంచనా దూరం (నేరుగా)',
     'no_team_avail': 'ఫిర్యాదు నమోదు చేయబడింది. ప్రస్తుతం అందుబాటులో ఉన్న బృందాలు లేవు; బృందం అందుబాటులోకి వచ్చిన వెంటనే కేటాయించబడుతుంది.',
     'custom_submitted_msg': 'ఇది జాబితాలో లేని ప్రదేశం కాబట్టి, మాన్యువల్ ధృవీకరణ మరియు జోన్ కేటాయింపు కోసం పుష్కరాల పారిశుద్ధ్య సూపర్‌వైజర్‌కు పంపబడింది. ఆటోమేటిక్‌గా బృందం కేటాయించబడదు.',
     'ticket_lookup_title': 'ఫిర్యాదు టికెట్ స్థితిని తనిఖీ చేయండి',
     'ticket_lookup_prompt': 'సఫాయి పురోగతి మరియు ఫోటో ఆధారాలను చూడటానికి మీ టికెట్ నంబర్‌ను నమోదు చేయండి:',
     'ticket_placeholder': 'ఉదా. CG-261103-XXXXXX',
     'track_button': 'స్థితి చూడండి',
     'ticket_not_found': 'ఈ టికెట్ నంబర్‌తో రికార్డు కనుగొనబడలేదు. దయచేసి తనిఖీ చేసి మళ్ళీ ప్రయత్నించండి.',
     'current_status': 'ప్రస్తుత స్థితి',
     'reported_on': 'నమోదు చేసిన సమయం',
     'assigned_team': 'కేటాయించిన పారిశుద్ధ్య బృందం',
     'cleaning_proof': 'శుభ్రత ధృవీకరణ ఫోటోలు (ముందు మరియు తర్వాత)',
     'no_proof_yet': 'పారిశుద్ధ్య బృందం పని పూర్తి చేసిన తర్వాత ముందు మరియు తర్వాత ఫోటోలు ఇక్కడ కనిపిస్తాయి.',
     'status_verification': 'సూపర్‌వైజర్ పరిశీలనలో ఉంది',
     'status_pending': 'డిస్పాచ్ క్యూలో ఉంది (బృందం లభ్యత కొరకు వేచి ఉంది)',
     'status_assigned': 'బృందం కేటాయించబడింది మరియు బయలుదేరింది',
     'status_accepted': 'పారిశుద్ధ్య బృందం ఆమోదించింది',
     'status_inprogress': 'ఘాట్ వద్ద శుభ్రపరచడం జరుగుతోంది',
     'status_completed': 'శుభ్రం చేయబడింది మరియు ధృవీకరించబడింది',
     'overflow': 'చెత్త బుట్ట నిండిపోయింది',
     'litter': 'నేలపై చెత్త',
     'accumulation': 'చెత్త పేరుకుపోవడం',
     'river': 'నది ఒడ్డున చెత్త',
     'dirty': 'అపరిశుభ్రమైన బహిరంగ ప్రదేశం',
     'other': 'ఇతర పరిశుభ్రత సమస్య',
     'no_location': 'QR ప్రదేశం గుర్తించబడలేదు. దయచేసి జాబితా నుండి ఎంచుకోండి.',
     'submit_another': '➕ మరొక ఫిర్యాదును నమోదు చేయండి',
     'copy_ticket_note': 'పరిశుభ్రత పురోగతిని తెలుసుకోవడానికి దయచేసి ఈ టికెట్ నంబర్‌ను భద్రపరుచుకోండి.'
 },
 'hi': {
     'title': 'क्लीनघाट',
     'subtitle': 'गोदावरी पुष्कराज 2027 · अपशिष्ट संग्रह एवं स्वच्छता',
     'tagline': 'PS-07: त्वरित स्वच्छता रिपोर्टिंग एवं स्मार्ट परिचालन',
     'badge_sim': 'डेमो प्रोटोटाइप · सिमुलेटेड परिचालन डेटा',
     'tab_report': '📝 शिकायत दर्ज करें',
     'tab_track': '🔍 टिकट स्थिति देखें',
     'language': 'भाषा / Language / భాష',
     'location': 'पुष्करालु स्थान / घाट',
     'location_help': 'वह घाट या क्षेत्र चुनें जहाँ सफाई की आवश्यकता है',
     'landmark': 'विशिष्ट लैंडमार्क / सटीक स्थान विवरण (वैकल्पिक)',
     'other_loc': '➕ अन्य / सूची में नहीं (कस्टम स्थान)',
     'custom_loc_desc': 'सटीक स्थान एवं लैंडमार्क का विवरण (अनिवार्य)',
     'custom_loc_required_err': 'अन्य / सूची में नहीं चुनने पर स्थान का विवरण अनिवार्य है।',
     'custom_loc_warning': '⚠️ सूचना: अनिर्दिष्ट स्थानों को पहले सुपरवाइजर सत्यापन सूची में भेजा जाता है। सुपरवाइजर द्वारा पुष्टि होने तक किसी भी टीम को स्वचालित रूप से नहीं भेजा जाता।',
     'category': 'समस्या श्रेणी (PS-07)',
     'description': 'अतिरिक्त विवरण (वैकल्पिक)',
     'photo': 'अपशिष्ट की फोटो अपलोड करें (वैकल्पिक)',
     'contact': 'नागरिक संपर्क नंबर (वैकल्पिक)',
     'contact_privacy': '🔒 गोपनीयता: आपका मोबाइल नंबर सुरक्षित रखा जाता है और सार्वजनिक ट्रैकिंग में कभी प्रदर्शित नहीं होगा।',
     'submit': 'रिपोर्ट जमा करें',
     'success_verified': 'आपकी शिकायत सफलतापूर्वक दर्ज हो गई है!',
     'success_custom': 'शिकायत सुपरवाइजर सत्यापन के लिए दर्ज की गई!',
     'ticket': 'आपकी शिकायत टिकट संख्या',
     'assigned_to': 'आवंटित टीम',
     'est_distance': 'सीधी अनुमानित दूरी',
     'no_team_avail': 'रिपोर्ट दर्ज कर ली गई है। वर्तमान में कोई टीम उपलब्ध नहीं है; टीम उपलब्ध होते ही आवंटित की जाएगी।',
     'custom_submitted_msg': 'चूंकि यह एक असूचीबद्ध स्थान है, इसे सत्यापन और ज़ोन आवंटन हेतु स्वच्छता सुपरवाइजर को भेजा गया है। स्वचालित रूप से कोई टीम नहीं भेजी गई है।',
     'ticket_lookup_title': 'शिकायत टिकट की स्थिति देखें',
     'ticket_lookup_prompt': 'सफाई की प्रगति और फोटो साक्ष्य देखने के लिए अपना टिकट नंबर दर्ज करें:',
     'ticket_placeholder': 'उदा. CG-261103-XXXXXX',
     'track_button': 'स्थिति जांचें',
     'ticket_not_found': 'इस टिकट नंबर के लिए कोई रिकॉर्ड नहीं मिला। कृपया पुनः जाँचें।',
     'current_status': 'वर्तमान स्थिति',
     'reported_on': 'रिपोर्ट की तिथि',
     'assigned_team': 'आवंटित सफाई टीम',
     'cleaning_proof': 'सफाई प्रमाण फोटो (पहले और बाद की)',
     'no_proof_yet': 'सफाई कर्मचारी द्वारा कार्य पूरा करने के तुरंत बाद पहले और बाद की फोटो यहाँ दिखाई देंगी।',
     'status_verification': 'सुपरवाइज़र सत्यापन के अधीन',
     'status_pending': 'डिस्पैच कतार में (टीम उपलब्धता लंबित)',
     'status_assigned': 'टीम आवंटित और प्रेषित',
     'status_accepted': 'सफाई टीम द्वारा कार्य स्वीकृत',
     'status_inprogress': 'स्थल पर सफाई कार्य प्रगति पर है',
     'status_completed': 'सफाई पूर्ण और सत्यापित',
     'overflow': 'कूड़ेदान भरा हुआ है',
     'litter': 'जमीन पर कचरा',
     'accumulation': 'कचरे का जमाव',
     'river': 'नदी किनारे कचरा',
     'dirty': 'गंदा सार्वजनिक क्षेत्र',
     'other': 'अन्य स्वच्छता समस्या',
     'no_location': 'QR स्थान पहचाना नहीं गया। कृपया सूची से स्थान चुनें।',
     'submit_another': '➕ दूसरी शिकायत दर्ज करें',
     'copy_ticket_note': 'सफाई की प्रगति देखने के लिए कृपया इस टिकट नंबर को नोट कर लें।'
 }
}
CATEGORIES = ['overflow','litter','accumulation','river','dirty','other']
CATEGORY_EN = {'overflow':'Overflowing bin','litter':'Litter on ground','accumulation':'Waste accumulation','river':'Garbage near riverbank','dirty':'Dirty public area','other':'Other cleanliness issue'}


def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS locations(id INTEGER PRIMARY KEY, qr_code TEXT UNIQUE, name TEXT, zone TEXT, area_type TEXT, lat REAL, lon REAL, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS teams(id INTEGER PRIMARY KEY, name TEXT, lat REAL, lon REAL, available INTEGER DEFAULT 1, active INTEGER DEFAULT 1, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS workers(id INTEGER PRIMARY KEY, team_id INTEGER REFERENCES teams(id), name TEXT, worker_code TEXT UNIQUE, phone TEXT, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY, ticket TEXT UNIQUE, location_id INTEGER, category TEXT, description TEXT, language TEXT, contact TEXT, reporter_photo TEXT, priority INTEGER, status TEXT, created_at TEXT);
        CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, report_id INTEGER, team_id INTEGER, status TEXT, assigned_at TEXT, accepted_at TEXT, started_at TEXT, completed_at TEXT, distance_m REAL, before_photo TEXT, after_photo TEXT);
        CREATE TABLE IF NOT EXISTS status_history(id INTEGER PRIMARY KEY, report_id INTEGER, task_id INTEGER, old_status TEXT, new_status TEXT, actor TEXT, changed_at TEXT);
        ''')
        # Add columns safely to existing databases
        report_columns = {
            row['name']
            for row in c.execute("PRAGMA table_info(reports)").fetchall()
        }

        if 'location_text' not in report_columns:
            c.execute("ALTER TABLE reports ADD COLUMN location_text TEXT")
        if 'is_custom_location' not in report_columns:
            c.execute("ALTER TABLE reports ADD COLUMN is_custom_location INTEGER DEFAULT 0")
        if 'qr_source_location_id' not in report_columns:
            c.execute("ALTER TABLE reports ADD COLUMN qr_source_location_id INTEGER")
        if 'assigned_zone' not in report_columns:
            c.execute("ALTER TABLE reports ADD COLUMN assigned_zone TEXT")
        if 'supervisor_notes' not in report_columns:
            c.execute("ALTER TABLE reports ADD COLUMN supervisor_notes TEXT")

        task_columns = {
            row['name']
            for row in c.execute("PRAGMA table_info(tasks)").fetchall()
        }
        if 'worker_id' not in task_columns:
            c.execute("ALTER TABLE tasks ADD COLUMN worker_id INTEGER")

        if c.execute('SELECT COUNT(*) FROM locations').fetchone()[0] == 0:
            locations = [
             ('GHAT-A-001','Pushkar Ghat — Main entrance','Zone A','Ghat',17.0008,81.8040),
             ('GHAT-A-002','Pushkar Ghat — Bathing steps','Zone A','Riverbank',17.0002,81.8048),
             ('GHAT-A-003','Pushkar Ghat — Dustbin cluster','Zone A','Public area',16.9998,81.8055),
             ('GHAT-B-001','Kotilingala Ghat — Entrance','Zone B','Ghat',17.0050,81.7800),
             ('GHAT-B-002','Kotilingala Ghat — Riverbank','Zone B','Riverbank',17.0044,81.7808),
             ('ROAD-C-001','Main approach road — North','Zone C','Road',17.0100,81.7900),
             ('ROAD-C-002','Main approach road — South','Zone C','Road',16.9950,81.7980),
             ('PUB-D-001','Public gathering area — East','Zone D','Public area',17.0080,81.8120),
             ('PUB-D-002','Public parking area','Zone D','Public area',17.0120,81.8080),
             ('RIVER-E-001','Riverbank access — South','Zone E','Riverbank',16.9920,81.8100),
            ]
            c.executemany('INSERT INTO locations(qr_code,name,zone,area_type,lat,lon) VALUES(?,?,?,?,?,?)', locations)
        if c.execute('SELECT COUNT(*) FROM teams').fetchone()[0] == 0:
            now = datetime.now().isoformat(timespec='seconds')
            teams = [('Team Alpha',17.0010,81.8030,1),('Team Bravo',17.0060,81.7810,1),('Team Charlie',17.0090,81.8090,1),('Team Delta',16.9960,81.7970,0),('Team Echo',17.0130,81.8070,1)]
            c.executemany('INSERT INTO teams(name,lat,lon,available,updated_at) VALUES(?,?,?,?,?)', [(n,la,lo,av,now) for n,la,lo,av in teams])
        if c.execute('SELECT COUNT(*) FROM workers').fetchone()[0] == 0:
            workers = [
                (1, 'K. Ramesh (Lead)', 'W-ALP-01', '9848011221'),
                (1, 'P. Venkatesh', 'W-ALP-02', '9848011222'),
                (2, 'M. Appa Rao (Lead)', 'W-BRV-01', '9848022331'),
                (2, 'B. Satyanarayana', 'W-BRV-02', '9848022332'),
                (3, 'G. Ravi Kumar (Lead)', 'W-CHR-01', '9848033441'),
                (3, 'S. Lakshmi Narayana', 'W-CHR-02', '9848033442'),
                (4, 'Ch. Durga Rao (Lead)', 'W-DLT-01', '9848044551'),
                (4, 'K. Srinivas', 'W-DLT-02', '9848044552'),
                (5, 'V. Nageswara Rao (Lead)', 'W-ECH-01', '9848055661'),
                (5, 'T. Subrahmanyam', 'W-ECH-02', '9848055662'),
            ]
            c.executemany('INSERT INTO workers(team_id, name, worker_code, phone) VALUES(?,?,?,?)', workers)


def haversine(lat1, lon1, lat2, lon2):
    r = 6371000
    p1,p2 = math.radians(lat1), math.radians(lat2)
    dp,dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))


def allocate_team(location_id):
    if not location_id:
        return None, None
    with db() as c:
        loc = c.execute('SELECT * FROM locations WHERE id=? AND active=1',(location_id,)).fetchone()
        if not loc: return None, None
        # Eligible teams must be active, available, and have no currently assigned/accepted/in-progress task.
        teams = c.execute('''SELECT t.* FROM teams t WHERE t.active=1 AND t.available=1 AND NOT EXISTS
            (SELECT 1 FROM tasks x WHERE x.team_id=t.id AND x.status IN ('ASSIGNED','ACCEPTED','IN_PROGRESS'))''').fetchall()
        if not teams: return None, None
        ranked = sorted([(haversine(loc['lat'],loc['lon'],t['lat'],t['lon']),t) for t in teams], key=lambda x:x[0])
        distance, team = ranked[0]
        c.execute('UPDATE teams SET available=0 WHERE id=?',(team['id'],))
        return team['id'], distance


def save_upload(upload, prefix):
    if upload is None: return None
    suffix = Path(upload.name).suffix.lower() or '.jpg'
    name = f'{prefix}_{uuid.uuid4().hex[:10]}{suffix}'
    path = UPLOAD_DIR / name
    path.write_bytes(upload.getbuffer())
    return str(path.relative_to(APP_DIR))


def history(report_id, task_id, old, new, actor):
    with db() as c:
        c.execute('INSERT INTO status_history(report_id,task_id,old_status,new_status,actor,changed_at) VALUES(?,?,?,?,?,?)',
                  (report_id,task_id,old,new,actor,datetime.now().isoformat(timespec='seconds')))


@st.cache_data
def make_qr(qr_code, base_url):
    url = f'{base_url.rstrip("/")}/?page=report&location={qr_code}'
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), url


@st.cache_resource
def get_initialized_db():
    init_db()
    return True

get_initialized_db()


@st.cache_data(ttl=60)
def get_active_locations():
    with db() as c:
        return [dict(x) for x in c.execute('SELECT * FROM locations WHERE active=1 ORDER BY zone, name').fetchall()]
params = st.query_params
page_param = params.get('page','').lower()
qr_param = params.get('location','')

# Determine active portal mode
if page_param in ['report', 'citizen']:
    page = 'Citizen portal'
elif page_param == 'worker':
    page = 'Worker portal'
elif page_param in ['admin', 'qr']:
    page = 'Admin dashboard'
elif page_param == 'settings':
    page = 'System settings'
else:
    # Sidebar navigation for desktop demo
    with st.sidebar:
        st.markdown("### ♻️ CleanGhat")
        st.caption("Godavari Pushkaralu 2027 Prototype\nPS-07: Waste & Cleanliness")
        page_choice = st.radio(
            "Select Portal",
            [
                "📱 Citizen portal",
                "🧹 Worker portal",
                "📊 Admin command portal",
                "⚙️ System settings"
            ],
            index=0
        )
        st.divider()
        st.caption("⚡ Demonstration prototype · Simulated operational data")
        if page_choice == "📱 Citizen portal":
            page = "Citizen portal"
        elif page_choice == "🧹 Worker portal":
            page = "Worker portal"
        elif page_choice == "📊 Admin command portal":
            page = "Admin dashboard"
        else:
            page = "System settings"

is_mobile_view = (page == 'Citizen portal')

# Clean Gov-Tech Light Theme Styling
base_css = '''<style>
/* Base Theme */
body, [data-testid="stAppViewContainer"] {
    background-color: #f8faf9 !important;
    color: #0f172a !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}
.gov-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.gov-header {
    background: linear-gradient(135deg, #0e5a36 0%, #166534 100%);
    color: #ffffff;
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 16px;
    text-align: center;
}
.gov-header h1 {
    color: #ffffff !important;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 4px 0 6px 0;
}
.gov-header p {
    color: #dcfce7 !important;
    font-size: 0.92rem;
    margin: 0;
}
.proto-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.35);
    color: #ffffff;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    margin-top: 8px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.status-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
}
.status-verif { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
.status-pend { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
.status-assign { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.status-accept { background: #ede9fe; color: #5b21b6; border: 1px solid #ddd6fe; }
.status-prog { background: #fae8ff; color: #86198f; border: 1px solid #f5d0fe; }
.status-done { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
[data-testid="stMetric"] {
    background: #ffffff !important;
    padding: 16px !important;
    border-radius: 12px !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03) !important;
}

/* Explicit Button & Download Button Contrast */
.stDownloadButton button,
.stButton button,
button[data-testid="stBaseButton-secondary"],
button[kind="secondary"] {
    background-color: #0e5a36 !important;
    color: #ffffff !important;
    border: 1px solid #0e5a36 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease-in-out !important;
}

.stDownloadButton button:hover,
.stButton button:hover,
button[data-testid="stBaseButton-secondary"]:hover,
button[kind="secondary"]:hover {
    background-color: #094025 !important;
    color: #ffffff !important;
    border-color: #094025 !important;
}

.stDownloadButton button p,
.stDownloadButton button span,
.stDownloadButton button div,
.stButton button p,
.stButton button span,
.stButton button div,
button[data-testid="stBaseButton-secondary"] p,
button[kind="secondary"] p,
button[data-testid="stBaseButton-secondary"] span,
button[kind="secondary"] span {
    color: #ffffff !important;
    font-weight: 600 !important;
}

button[data-testid="stBaseButton-primary"],
button[kind="primary"] {
    background-color: #0e5a36 !important;
    color: #ffffff !important;
    border: 1px solid #0e5a36 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

button[data-testid="stBaseButton-primary"]:hover,
button[kind="primary"]:hover {
    background-color: #094025 !important;
    color: #ffffff !important;
}

button[data-testid="stBaseButton-primary"] p,
button[kind="primary"] p,
button[data-testid="stBaseButton-primary"] span,
button[kind="primary"] span {
    color: #ffffff !important;
    font-weight: 600 !important;
}

/* Code badge styling */
code {
    background-color: #e8f5ed !important;
    color: #0e5a36 !important;
    font-weight: 600 !important;
    border-radius: 4px !important;
    padding: 2px 6px !important;
    border: 1px solid #c2e7d1 !important;
}
</style>'''

mobile_css = '''<style>
/* Citizen Mobile View: strictly no sidebar, single column */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
.block-container {
    max-width: 540px !important;
    padding-top: 1rem !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
    margin: 0 auto !important;
}
</style>'''

desktop_css = '''<style>
.block-container {
    max-width: 1180px !important;
    padding-top: 1.5rem !important;
}
</style>'''

st.markdown(base_css, unsafe_allow_html=True)
if is_mobile_view:
    st.markdown(mobile_css, unsafe_allow_html=True)
else:
    st.markdown(desktop_css, unsafe_allow_html=True)

if page == 'Citizen portal':
    # Language Switcher
    lang = st.radio(
        "Language",
        ['English', 'తెలుగు', 'हिन्दी'],
        horizontal=True,
        index=0,
        label_visibility="collapsed"
    )
    lang_code = {'English': 'en', 'తెలుగు': 'te', 'हिन्दी': 'hi'}[lang]
    t = I18N[lang_code]

    # Citizen Portal Header
    st.markdown(f'''
    <div class="gov-header">
        <div style="font-size:0.85rem; letter-spacing:0.8px; opacity:0.95; font-weight:600;">ANDHRA PRADESH SWACHH PUSHKARALU 2027</div>
        <h1>{t["title"]}</h1>
        <p>{t["subtitle"]}</p>
        <div class="proto-badge">PS-07 · Waste Collection & Cleanliness · Prototype Demo</div>
    </div>
    ''', unsafe_allow_html=True)

    tab_report, tab_track = st.tabs([t['tab_report'], t['tab_track']])

    with tab_report:
        if 'submitted_ticket_info' in st.session_state:
            sub = st.session_state['submitted_ticket_info']
            st.success(sub['success_msg'])
            st.markdown(f'''
            <div class="gov-card" style="border-left: 4px solid {sub['border_color']};">
                <span class="status-badge {sub['status_class']}">{sub['status_label']}</span>
                <h3 style="margin-top:10px; margin-bottom:8px;">{t["ticket"]}: <code style="font-size:1.25rem; color:#0e5a36;">{sub['ticket']}</code></h3>
                <p style="font-size:0.95rem; margin-bottom:10px;">{sub['detail_msg']}</p>
                <div style="background:#f1f5f9; padding:10px 14px; border-radius:8px; border:1px dashed #cbd5e1; margin-bottom:12px;">
                    <p style="margin:0; font-weight:600; font-size:0.92rem;">📍 {sub['loc_title']}</p>
                    <p style="margin:4px 0 0 0; color:#64748b; font-size:0.85rem;">🏷️ {sub['cat_title']} · 🕒 {sub['time_str']}</p>
                </div>
                <p style="font-size:0.88rem; color:#475569; margin:0;">ℹ️ {t['copy_ticket_note']}</p>
            </div>
            ''', unsafe_allow_html=True)

            st.write("")
            if st.button(t['submit_another'], type="primary", use_container_width=True):
                del st.session_state['submitted_ticket_info']
                st.rerun()

        else:
            locations = get_active_locations()

            # Build dropdown options
            loc_options = [f"{x['name']} ({x['qr_code']}) — {x['zone']}" for x in locations]
            loc_options.append(t['other_loc'])

            # Determine prefill index if scanned via QR
            default_index = 0
            qr_matched_loc = None
            if qr_param:
                qr_matched_loc = next((x for x in locations if x['qr_code'] == qr_param), None)
                if qr_matched_loc:
                    default_index = [x['qr_code'] for x in locations].index(qr_param)
                else:
                    st.warning(t['no_location'])

            selected_option = st.selectbox(
                t['location'],
                loc_options,
                index=default_index,
                help=t['location_help']
            )

            is_custom_selected = (selected_option == t['other_loc'])
            custom_location_text = ""
            landmark_text = ""

            if is_custom_selected:
                st.warning(t['custom_loc_warning'])
                custom_location_text = st.text_input(
                    t['custom_loc_desc'],
                    placeholder="e.g. Near temporary food stalls, 150m north of bathing steps"
                )
            else:
                chosen_loc = locations[loc_options.index(selected_option)]
                st.info(f"📍 **{t['location']}:** {chosen_loc['name']} · {chosen_loc['zone']} · Code: `{chosen_loc['qr_code']}`")
                landmark_text = st.text_input(
                    t['landmark'],
                    placeholder="e.g. Near bathing step #4, beside drinking water kiosk"
                )

            # Waste Issue Category (strictly PS-07)
            cat_label = st.selectbox(t['category'], [t[x] for x in CATEGORIES])
            cat_key = CATEGORIES[[t[x] for x in CATEGORIES].index(cat_label)]

            description = st.text_area(t['description'], max_chars=500, placeholder="Describe waste accumulation, size, or urgency...")
            photo = st.file_uploader(t['photo'], type=['jpg', 'jpeg', 'png'], help="Upload photographic evidence of waste or litter")
            contact = st.text_input(t['contact'], max_chars=15, placeholder="e.g. 9876543210")
            st.caption(t['contact_privacy'])

            submitted = st.button(t['submit'], type="primary", use_container_width=True)

            if submitted:
                if is_custom_selected and not custom_location_text.strip():
                    st.error(t.get('custom_loc_required_err', "Location description is compulsory when selecting 'Other / Not listed'."))
                else:
                    reporter_photo = save_upload(photo, 'report')
                    ticket = 'CG-' + datetime.now().strftime('%y%m%d') + '-' + uuid.uuid4().hex[:6].upper()
                    priority = {'overflow': 45, 'litter': 25, 'accumulation': 35, 'river': 65, 'dirty': 25, 'other': 20}[cat_key]

                    if is_custom_selected:
                        # CUSTOM LOCATION WORKFLOW:
                        # Status is VERIFICATION_REQUIRED.
                        # NEVER auto-assign a team.
                        with db() as c:
                            c.execute('''
                                INSERT INTO reports(
                                    ticket, location_id, location_text, is_custom_location,
                                    qr_source_location_id, category, description, language,
                                    contact, reporter_photo, priority, status, created_at
                                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                            ''', (
                                ticket, None, custom_location_text.strip(), 1,
                                (qr_matched_loc['id'] if qr_matched_loc else None),
                                cat_key, description.strip(), lang_code,
                                contact.strip() or None, reporter_photo, priority,
                                'VERIFICATION_REQUIRED', datetime.now().isoformat(timespec='seconds')
                            ))
                            report_id = c.execute('SELECT id FROM reports WHERE ticket=?', (ticket,)).fetchone()['id']

                        history(report_id, None, None, 'VERIFICATION_REQUIRED', 'citizen-custom-location')

                        st.session_state['submitted_ticket_info'] = {
                            'ticket': ticket,
                            'success_msg': t['success_custom'],
                            'status_label': t['status_verification'],
                            'status_class': 'status-verif',
                            'border_color': '#f59e0b',
                            'detail_msg': t['custom_submitted_msg'],
                            'loc_title': f"{t['other_loc']}: {custom_location_text.strip()}",
                            'cat_title': CATEGORY_EN.get(cat_key, cat_key),
                            'time_str': datetime.now().strftime('%d %b %Y, %I:%M %p')
                        }
                        st.session_state['recent_ticket'] = ticket
                        st.rerun()

                    else:
                        # REGISTERED LOCATION WORKFLOW:
                        # Status starts as PENDING, auto-allocation is attempted.
                        with db() as c:
                            c.execute('''
                                INSERT INTO reports(
                                    ticket, location_id, location_text, is_custom_location,
                                    qr_source_location_id, category, description, language,
                                    contact, reporter_photo, priority, status, created_at
                                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                            ''', (
                                ticket, chosen_loc['id'], landmark_text.strip() or None, 0,
                                (chosen_loc['id'] if qr_param else None),
                                cat_key, description.strip(), lang_code,
                                contact.strip() or None, reporter_photo, priority,
                                'PENDING', datetime.now().isoformat(timespec='seconds')
                            ))
                            report_id = c.execute('SELECT id FROM reports WHERE ticket=?', (ticket,)).fetchone()['id']

                        team_id, distance = allocate_team(chosen_loc['id'])
                        if team_id:
                            with db() as c:
                                c.execute('INSERT INTO tasks(report_id,team_id,status,assigned_at,distance_m) VALUES(?,?,?,?,?)',
                                    (report_id, team_id, 'ASSIGNED', datetime.now().isoformat(timespec='seconds'), distance))
                                task_id = c.execute('SELECT id FROM tasks WHERE report_id=?', (report_id,)).fetchone()['id']
                                c.execute("UPDATE reports SET status='ASSIGNED' WHERE id=?", (report_id,))
                                team_name = c.execute('SELECT name FROM teams WHERE id=?', (team_id,)).fetchone()['name']
                            history(report_id, task_id, 'PENDING', 'ASSIGNED', 'dispatch-engine')

                            detail_msg = f"🚚 <b>{t['assigned_to']}:</b> {team_name} · <b>{distance:.0f}m</b> ({t['est_distance']})"
                            status_label = t['status_assigned']
                            status_class = 'status-assign'
                            border_color = '#0e5a36'
                        else:
                            detail_msg = t['no_team_avail']
                            status_label = t['status_pending']
                            status_class = 'status-pend'
                            border_color = '#94a3b8'

                        st.session_state['submitted_ticket_info'] = {
                            'ticket': ticket,
                            'success_msg': t['success_verified'],
                            'status_label': status_label,
                            'status_class': status_class,
                            'border_color': border_color,
                            'detail_msg': detail_msg,
                            'loc_title': f"{chosen_loc['name']} ({chosen_loc['zone']})",
                            'cat_title': CATEGORY_EN.get(cat_key, cat_key),
                            'time_str': datetime.now().strftime('%d %b %Y, %I:%M %p')
                        }
                        st.session_state['recent_ticket'] = ticket
                        st.rerun()

    with tab_track:
        st.markdown(f"#### {t['ticket_lookup_title']}")
        st.caption(t['ticket_lookup_prompt'])
        prefill_ticket = st.session_state.get('recent_ticket', '')
        search_ticket = st.text_input(t['ticket_placeholder'], value=prefill_ticket, max_chars=35, placeholder="e.g. CG-261103-XXXXXX").strip().upper()

        if st.button(t['track_button'], use_container_width=True, type="primary"):
            if not search_ticket:
                st.warning("Please enter a ticket ID.")
            else:
                with db() as c:
                    rep = c.execute('''
                        SELECT r.*, l.name AS location_name, l.zone, l.area_type
                        FROM reports r
                        LEFT JOIN locations l ON l.id = r.location_id
                        WHERE UPPER(r.ticket) = ?
                    ''', (search_ticket,)).fetchone()

                    if rep:
                        task = c.execute('''
                            SELECT ta.*, t.name AS team_name
                            FROM tasks ta
                            LEFT JOIN teams t ON t.id = ta.team_id
                            WHERE ta.report_id = ?
                            ORDER BY ta.id DESC LIMIT 1
                        ''', (rep['id'],)).fetchone()
                    else:
                        task = None

                if not rep:
                    st.error(t['ticket_not_found'])
                else:
                    # Privacy-Safe Complaint Details (no contact info exposed)
                    loc_display = rep['location_name'] or f"Custom Location: {rep['location_text'] or 'Unspecified'}"
                    if rep['location_name'] and rep['location_text']:
                        loc_display += f" ({rep['location_text']})"

                    cat_display = t.get(rep['category'], rep['category'])
                    status = rep['status']

                    # Status pill class and label
                    badge_class = {
                        'VERIFICATION_REQUIRED': 'status-verif',
                        'PENDING': 'status-pend',
                        'ASSIGNED': 'status-assign',
                        'ACCEPTED': 'status-accept',
                        'IN_PROGRESS': 'status-prog',
                        'COMPLETED': 'status-done'
                    }.get(status, 'status-pend')

                    status_label = {
                        'VERIFICATION_REQUIRED': t['status_verification'],
                        'PENDING': t['status_pending'],
                        'ASSIGNED': t['status_assigned'],
                        'ACCEPTED': t['status_accepted'],
                        'IN_PROGRESS': t['status_inprogress'],
                        'COMPLETED': t['status_completed']
                    }.get(status, status)

                    st.markdown(f'''
                    <div class="gov-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:700; font-size:1.1rem; color:#0f172a;">{rep["ticket"]}</span>
                            <span class="status-badge {badge_class}">{status_label}</span>
                        </div>
                        <p style="margin:4px 0;">📍 <b>{t["location"]}:</b> {loc_display}</p>
                        <p style="margin:4px 0;">♻️ <b>{t["category"]}:</b> {cat_display}</p>
                        <p style="margin:4px 0; font-size:0.85rem; color:#64748b;">🕒 <b>{t["reported_on"]}:</b> {rep["created_at"]}</p>
                    ''', unsafe_allow_html=True)

                    if rep['description']:
                        st.caption(f"Details: {rep['description']}")

                    if task and task['team_name']:
                        st.markdown(f"🚚 **{t['assigned_team']}:** {task['team_name']}")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # Completion evidence if completed
                    if status == 'COMPLETED' and task:
                        st.markdown(f"##### {t['cleaning_proof']}")
                        p_cols = st.columns(2)
                        with p_cols[0]:
                            if task['before_photo'] and (APP_DIR / task['before_photo']).exists():
                                st.image(str(APP_DIR / task['before_photo']), caption="Before Cleaning", use_container_width=True)
                            else:
                                st.caption("Before photo recorded")
                        with p_cols[1]:
                            if task['after_photo'] and (APP_DIR / task['after_photo']).exists():
                                st.image(str(APP_DIR / task['after_photo']), caption="After Cleaning (Resolved)", use_container_width=True)
                            else:
                                st.caption("After photo recorded")
                    elif status != 'COMPLETED':
                        st.caption(t['no_proof_yet'])

    # Evaluator switch helper for testing on mobile view
    st.divider()
    with st.expander("🛠️ Demo Portal Switcher (For Evaluators & Judges)", expanded=False):
        st.caption("Switch portals for end-to-end evaluation:")
        eval_cols = st.columns(2)
        if eval_cols[0].button("🧹 Worker Portal", key="sw_worker", use_container_width=True):
            st.query_params["page"] = "worker"
            st.rerun()
        if eval_cols[1].button("📊 Admin Portal (with QR Codes)", key="sw_admin", use_container_width=True):
            st.query_params["page"] = "admin"
            st.rerun()

elif page == 'Worker portal':
    st.markdown('''
    <div class="gov-header">
        <div style="font-size:0.85rem; letter-spacing:0.8px; opacity:0.95; font-weight:600;">ANDHRA PRADESH SWACHH PUSHKARALU 2027</div>
        <h1>🧹 Sanitation Worker Portal</h1>
        <p>Field Cleaning Operations · Task Execution · Photographic Verification</p>
        <div class="proto-badge">Simulated Field Accounts · Mandatory Photo Proof</div>
    </div>
    ''', unsafe_allow_html=True)

    with db() as c:
        teams = [dict(row) for row in c.execute('SELECT * FROM teams WHERE active=1 ORDER BY name').fetchall()]

    col_t1, col_t2 = st.columns([1, 1])
    with col_t1:
        team = st.selectbox(
            '🏢 Select Sanitation Team',
            teams,
            format_func=lambda x: f"{x['name']} ({'🟢 Available' if x['available'] else '🔴 On Active Task'})"
        )

    with db() as c:
        workers = [dict(w) for w in c.execute('SELECT * FROM workers WHERE team_id=? AND active=1 ORDER BY id', (team['id'],)).fetchall()]

    with col_t2:
        if workers:
            worker = st.selectbox(
                '👤 Select Worker Account',
                workers,
                format_func=lambda w: f"{w['name']} [{w['worker_code']}]"
            )
        else:
            worker = {'id': None, 'name': team['name'], 'worker_code': 'N/A'}
            st.info("No individual worker profiles registered for this team.")

    # Team status summary bar
    with db() as c:
        active_count = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE team_id=? AND status IN ('ASSIGNED','ACCEPTED','IN_PROGRESS')",
            (team['id'],)
        ).fetchone()[0]
        completed_count = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE team_id=? AND status='COMPLETED'",
            (team['id'],)
        ).fetchone()[0]

    st.markdown(f'''
    <div class="gov-card" style="padding:12px 18px; margin-bottom:14px; background:#f8fafc;">
        <span style="font-weight:600; color:#0f172a;">Team Status:</span>
        <span style="margin-left:8px;" class="status-badge {'status-done' if active_count == 0 else 'status-prog'}">
            {'🟢 Ready for Assignment' if active_count == 0 else f'⚠️ 1 Active Task in Progress (Max 1 per team)'}
        </span>
        <span style="margin-left:16px; font-size:0.88rem; color:#64748b;">
            Logged in as: <b>{worker['name']}</b> · Tasks Completed by Team: <b>{completed_count}</b> · Simulated GPS: <code>{team['lat']:.4f}, {team['lon']:.4f}</code>
        </span>
    </div>
    ''', unsafe_allow_html=True)

    tab_active, tab_completed = st.tabs(["📋 Assigned & In-Progress Tasks", "🏆 Completed Proof Archive"])

    with tab_active:
        with db() as c:
            tasks = c.execute('''
                SELECT ta.*, r.ticket, r.category, r.description, r.priority, r.reporter_photo, r.location_text, r.created_at AS report_time,
                    COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS location_name,
                    l.zone, l.lat, l.lon,
                    w.name AS worker_name
                FROM tasks ta
                JOIN reports r ON r.id = ta.report_id
                LEFT JOIN locations l ON l.id = r.location_id
                LEFT JOIN workers w ON w.id = ta.worker_id
                WHERE ta.team_id = ? AND ta.status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS')
                ORDER BY ta.assigned_at DESC
            ''', (team['id'],)).fetchall()

        if not tasks:
            st.info(f"✨ No active tasks assigned to {team['name']} right now. When citizens submit waste reports near your area, tasks will appear here.")
        else:
            for task in tasks:
                status = task['status']
                badge_style = {
                    'ASSIGNED': 'status-assign',
                    'ACCEPTED': 'status-accept',
                    'IN_PROGRESS': 'status-prog'
                }.get(status, 'status-pend')

                status_label = {
                    'ASSIGNED': 'Action Required: Accept Task',
                    'ACCEPTED': 'Task Accepted · Proceed to Ghat',
                    'IN_PROGRESS': 'Cleaning in Progress at Site'
                }.get(status, status)

                with st.container(border=True):
                    head_col1, head_col2 = st.columns([3, 1])
                    with head_col1:
                        st.subheader(f"🎫 {task['ticket']} · {CATEGORY_EN.get(task['category'], task['category'])}")
                        st.write(f"📍 **Target Location:** {task['location_name']}" + (f" ({task['zone']})" if task['zone'] else ""))
                        if task['location_text'] and task['location_text'] not in task['location_name']:
                            st.write(f"📌 **Spot / Landmark Details:** `{task['location_text']}`")
                        st.caption(f"Assigned At: {task['assigned_at']} · Straight-line distance: {task['distance_m']:.0f}m")
                    with head_col2:
                        st.markdown(f'''<div style="text-align:right;"><span class="status-badge {badge_style}">{status_label}</span><br><br><span style="font-size:0.85rem; color:#475569;">Priority: <b>{task['priority']}/100</b></span></div>''', unsafe_allow_html=True)

                    if task['description']:
                        st.info(f"📝 **Citizen Details:** {task['description']}")

                    # Show reporter photo if uploaded
                    if task['reporter_photo'] and (APP_DIR / task['reporter_photo']).exists():
                        with st.expander("📷 View Citizen Uploaded Waste Photo", expanded=False):
                            st.image(str(APP_DIR / task['reporter_photo']), caption="Citizen Reported Evidence", width=300)

                    st.divider()

                    # WORKFLOW STEP 1: ACCEPT
                    if status == 'ASSIGNED':
                        st.write("👉 **Step 1:** Confirm that your team is ready to respond to this cleanliness report.")
                        if st.button('✅ Accept Task', key=f"accept_{task['id']}", type="primary"):
                            with db() as c:
                                c.execute(
                                    "UPDATE tasks SET status='ACCEPTED', accepted_at=?, worker_id=? WHERE id=?",
                                    (datetime.now().isoformat(timespec='seconds'), worker['id'], task['id'])
                                )
                                c.execute("UPDATE reports SET status='ACCEPTED' WHERE id=?", (task['report_id'],))
                            history(task['report_id'], task['id'], 'ASSIGNED', 'ACCEPTED', f"{worker['name']} ({team['name']})")
                            st.success(f"Task accepted by {worker['name']}! Ready to start cleaning.")
                            st.rerun()

                    # WORKFLOW STEP 2: START CLEANING
                    elif status == 'ACCEPTED':
                        st.write("👉 **Step 2:** Arrive at the ghat/waste spot and click below to mark work in progress.")
                        if st.button('🚀 Start Cleaning (Arrived at Site)', key=f"start_{task['id']}", type="primary"):
                            with db() as c:
                                c.execute(
                                    "UPDATE tasks SET status='IN_PROGRESS', started_at=?, worker_id=? WHERE id=?",
                                    (datetime.now().isoformat(timespec='seconds'), worker['id'], task['id'])
                                )
                                c.execute("UPDATE reports SET status='IN_PROGRESS' WHERE id=?", (task['report_id'],))
                            history(task['report_id'], task['id'], 'ACCEPTED', 'IN_PROGRESS', f"{worker['name']} ({team['name']})")
                            st.success("Status updated to In Progress. Please perform cleaning.")
                            st.rerun()

                    # WORKFLOW STEP 3: COMPLETE WITH MANDATORY BEFORE & AFTER PHOTOS
                    elif status == 'IN_PROGRESS':
                        st.markdown("👉 **Step 3: Verification & Completion**")
                        st.warning("⚠️ **Strict Requirement:** Both Before-cleaning and After-cleaning photographs are mandatory to prevent fraudulent completion.")

                        upload_col1, upload_col2 = st.columns(2)
                        with upload_col1:
                            before = st.file_uploader('📷 1. Before-cleaning photo *', type=['jpg', 'jpeg', 'png'], key=f"before_{task['id']}")
                        with upload_col2:
                            after = st.file_uploader('📷 2. After-cleaning photo *', type=['jpg', 'jpeg', 'png'], key=f"after_{task['id']}")

                        worker_notes = st.text_input('Worker field notes (optional)', placeholder="e.g. Cleared 2 bags of litter, disinfected the area with bleaching powder", key=f"notes_{task['id']}")

                        if st.button('🏁 Upload Evidence & Complete Task', key=f"complete_{task['id']}", type="primary", use_container_width=True):
                            if not before or not after:
                                st.error('❌ Incomplete evidence: Both Before and After photographs must be uploaded before completing the task.')
                            else:
                                bp = save_upload(before, 'before')
                                ap = save_upload(after, 'after')
                                now_ts = datetime.now().isoformat(timespec='seconds')
                                with db() as c:
                                    c.execute('''
                                        UPDATE tasks SET
                                            status='COMPLETED',
                                            completed_at=?,
                                            before_photo=?,
                                            after_photo=?,
                                            worker_id=?
                                        WHERE id=?
                                    ''', (now_ts, bp, ap, worker['id'], task['id']))
                                    c.execute("UPDATE reports SET status='COMPLETED' WHERE id=?", (task['report_id'],))
                                    # Release team back to available
                                    c.execute('UPDATE teams SET available=1 WHERE id=?', (team['id'],))
                                history(task['report_id'], task['id'], 'IN_PROGRESS', 'COMPLETED', f"{worker['name']} ({team['name']})")
                                st.success(f"🎉 Task completed and verified by {worker['name']}! Evidence recorded, and {team['name']} is now marked available for new assignments.")
                                st.rerun()

    with tab_completed:
        with db() as c:
            completed_tasks = c.execute('''
                SELECT ta.*, r.ticket, r.category, r.location_text, r.created_at AS report_time,
                    COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS location_name,
                    l.zone,
                    w.name AS worker_name, w.worker_code
                FROM tasks ta
                JOIN reports r ON r.id = ta.report_id
                LEFT JOIN locations l ON l.id = r.location_id
                LEFT JOIN workers w ON w.id = ta.worker_id
                WHERE ta.team_id = ? AND ta.status = 'COMPLETED'
                ORDER BY ta.completed_at DESC
            ''', (team['id'],)).fetchall()

        if not completed_tasks:
            st.info(f"No completed tasks recorded for {team['name']} yet.")
        else:
            for ctask in completed_tasks:
                with st.container(border=True):
                    c_h1, c_h2 = st.columns([3, 1])
                    with c_h1:
                        st.subheader(f"✅ {ctask['ticket']} · {CATEGORY_EN.get(ctask['category'], ctask['category'])}")
                        st.write(f"📍 **Cleaned Location:** {ctask['location_name']}" + (f" ({ctask['zone']})" if ctask['zone'] else ""))
                        if ctask['location_text'] and ctask['location_text'] not in ctask['location_name']:
                            st.write(f"📌 **Spot / Landmark Details:** `{ctask['location_text']}`")
                        worker_display = ctask['worker_name'] or "Assigned Field Staff"
                        code_display = f" [{ctask['worker_code']}]" if ctask['worker_code'] else ""
                        st.write(f"👤 **Completed by:** {worker_display}{code_display}")
                    with c_h2:
                        st.markdown('''<div style="text-align:right;"><span class="status-badge status-done">Cleaned & Resolved</span></div>''', unsafe_allow_html=True)
                        st.caption(f"Completed: {ctask['completed_at']}")

                    st.markdown("##### 📸 Cleaning Evidence Proof (Before & After)")
                    photo_cols = st.columns(2)
                    with photo_cols[0]:
                        if ctask['before_photo'] and (APP_DIR / ctask['before_photo']).exists():
                            st.image(str(APP_DIR / ctask['before_photo']), caption="Before Cleaning", use_container_width=True)
                        else:
                            st.caption("No before photo available")
                    with photo_cols[1]:
                        if ctask['after_photo'] and (APP_DIR / ctask['after_photo']).exists():
                            st.image(str(APP_DIR / ctask['after_photo']), caption="After Cleaning (Cleaned & Sanitized)", use_container_width=True)
                        else:
                            st.caption("No after photo available")

elif page == 'Admin dashboard':
    st.markdown('''
    <div class="gov-header">
        <div style="font-size:0.85rem; letter-spacing:0.8px; opacity:0.95; font-weight:600;">ANDHRA PRADESH SWACHH PUSHKARALU 2027</div>
        <h1>📊 Command & Admin Portal</h1>
        <p>Real-Time Cleanliness Monitoring · Supervisor Verification · Fleet Dispatch · Hotspot Analytics</p>
        <div class="proto-badge">PS-07 Central Operations Command · Simulated Telemetry</div>
    </div>
    ''', unsafe_allow_html=True)

    with db() as c:
        # Load comprehensive reports dataset
        reports = pd.read_sql_query('''
            SELECT r.*,
                COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS location_name,
                COALESCE(l.zone, r.assigned_zone, 'Unassigned') AS zone,
                COALESCE(l.area_type, 'Custom') AS area_type
            FROM reports r
            LEFT JOIN locations l ON l.id = r.location_id
            ORDER BY r.created_at DESC
        ''', c)

        tasks = pd.read_sql_query('''
            SELECT ta.*, r.ticket, r.category,
                COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS location_name,
                t.name AS team_name, w.name AS worker_name
            FROM tasks ta
            JOIN reports r ON r.id = ta.report_id
            LEFT JOIN locations l ON l.id = r.location_id
            LEFT JOIN teams t ON t.id = ta.team_id
            LEFT JOIN workers w ON w.id = ta.worker_id
            ORDER BY ta.assigned_at DESC
        ''', c)

        teams_df = pd.read_sql_query('SELECT * FROM teams', c)
        workers_df = pd.read_sql_query('''
            SELECT w.name AS worker_name, w.worker_code, t.name AS team_name,
                   COUNT(ta.id) AS tasks_completed
            FROM workers w
            JOIN teams t ON t.id = w.team_id
            LEFT JOIN tasks ta ON ta.worker_id = w.id AND ta.status = 'COMPLETED'
            GROUP BY w.id, w.name, w.worker_code, t.name
            ORDER BY tasks_completed DESC, w.id ASC
        ''', c)

    # High-level KPIs
    total = len(reports)
    pending_verif = int((reports.status == 'VERIFICATION_REQUIRED').sum()) if total else 0
    active = int((tasks.status.isin(['ASSIGNED', 'ACCEPTED', 'IN_PROGRESS'])).sum()) if len(tasks) else 0
    completed = int((reports.status == 'COMPLETED').sum()) if total else 0
    available = int((teams_df.available == 1).sum()) if len(teams_df) else 0

    k = st.columns(5)
    k[0].metric('Total Reports', total)
    k[1].metric('Verification Queue', pending_verif, delta=f"{pending_verif} custom" if pending_verif else None, delta_color="inverse")
    k[2].metric('Active Field Tasks', active)
    k[3].metric('Cleaned & Resolved', completed)
    k[4].metric('Available Teams', f"{available} / {len(teams_df)}")

    tab_verif, tab_all, tab_hotspots, tab_fleet, tab_qr = st.tabs([
        f"⚠️ Supervisor Verification ({pending_verif})",
        "📋 All Complaints & Dispatch Log",
        "🔥 Cleanliness Hotspots & Analytics",
        "🚚 Fleet & Worker Performance",
        "🔳 Location QR Codes"
    ])

    # TAB 1: SUPERVISOR VERIFICATION QUEUE
    with tab_verif:
        st.subheader("⚠️ Unverified Custom Locations Queue")
        st.caption("Requirement 5: Custom locations are never auto-assigned. A Pushkaralu supervisor must review the location, assign an operational zone/ghat, and approve dispatch.")

        with db() as c:
            unverified_reports = c.execute('''
                SELECT r.*, qr_loc.name AS scanned_qr_name
                FROM reports r
                LEFT JOIN locations qr_loc ON qr_loc.id = r.qr_source_location_id
                WHERE r.status = 'VERIFICATION_REQUIRED'
                ORDER BY r.created_at ASC
            ''').fetchall()

        if not unverified_reports:
            st.success("🎉 All custom location reports have been verified! No unverified reports pending.")
        else:
            reg_locations = get_active_locations()
            with db() as c:
                avail_teams = [dict(tm) for tm in c.execute('SELECT * FROM teams WHERE active=1 AND available=1 ORDER BY name').fetchall()]

            for u_rep in unverified_reports:
                with st.container(border=True):
                    v_col1, v_col2 = st.columns([2, 1])
                    with v_col1:
                        st.markdown(f"### 🎫 `{u_rep['ticket']}` · {CATEGORY_EN.get(u_rep['category'], u_rep['category'])}")
                        st.markdown(f"📍 **Reported Custom Spot:** `{u_rep['location_text'] or 'Unspecified description'}`")
                        if u_rep['scanned_qr_name']:
                            st.caption(f"Scanned from nearby QR code: {u_rep['scanned_qr_name']}")
                        if u_rep['description']:
                            st.write(f"📝 **Citizen Notes:** {u_rep['description']}")
                        if u_rep['contact']:
                            st.caption(f"📞 Citizen Contact: {u_rep['contact']} (Confidential for supervisor verification)")
                        st.caption(f"Reported at: {u_rep['created_at']} · Priority: {u_rep['priority']}/100")

                    with v_col2:
                        if u_rep['reporter_photo'] and (APP_DIR / u_rep['reporter_photo']).exists():
                            st.image(str(APP_DIR / u_rep['reporter_photo']), caption="Citizen Photo", width=180)
                        else:
                            st.caption("No photo attached")

                    st.divider()
                    st.write("**Supervisor Actions: Review, Map & Dispatch**")
                    act_col1, act_col2 = st.columns(2)

                    with act_col1:
                        zone_choice = st.selectbox(
                            "Assign Pushkaralu Operational Zone",
                            ["Zone A (Pushkar Ghat)", "Zone B (Kotilingala Ghat)", "Zone C (Main Approach Road)", "Zone D (Public Gathering Area)", "Zone E (Riverbank South)"],
                            key=f"zone_{u_rep['id']}"
                        )
                        mapped_loc = st.selectbox(
                            "Map to Nearest Registered Master Ghat",
                            reg_locations,
                            format_func=lambda x: f"{x['name']} ({x['zone']})",
                            key=f"loc_{u_rep['id']}"
                        )
                        sup_notes = st.text_input(
                            "Supervisor Verification Notes",
                            value=f"Verified spot in {zone_choice.split()[0]} near {mapped_loc['name']}",
                            key=f"snotes_{u_rep['id']}"
                        )

                    with act_col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        # Option A: Auto-dispatch nearest team
                        if st.button("🚀 Verify & Auto-Dispatch Nearest Available Team", key=f"auto_disp_{u_rep['id']}", type="primary", use_container_width=True):
                            zone_val = zone_choice.split()[0]
                            with db() as c:
                                c.execute('''
                                    UPDATE reports SET
                                        location_id=?,
                                        assigned_zone=?,
                                        supervisor_notes=?,
                                        status='PENDING'
                                    WHERE id=?
                                ''', (mapped_loc['id'], zone_val, sup_notes, u_rep['id']))

                            team_id, distance = allocate_team(mapped_loc['id'])
                            if team_id:
                                now_str = datetime.now().isoformat(timespec='seconds')
                                with db() as c:
                                    c.execute('''
                                        INSERT INTO tasks(report_id, team_id, status, assigned_at, distance_m)
                                        VALUES(?, ?, 'ASSIGNED', ?, ?)
                                    ''', (u_rep['id'], team_id, now_str, distance))
                                    task_id = c.execute('SELECT id FROM tasks WHERE report_id=?', (u_rep['id'],)).fetchone()['id']
                                    c.execute("UPDATE reports SET status='ASSIGNED' WHERE id=?", (u_rep['id'],))
                                    t_name = c.execute('SELECT name FROM teams WHERE id=?', (team_id,)).fetchone()['name']
                                history(u_rep['id'], task_id, 'VERIFICATION_REQUIRED', 'ASSIGNED', f"supervisor-auto-to-{t_name}")
                                st.success(f"Verified & Dispatched to {t_name} ({distance:.0f}m)!")
                            else:
                                history(u_rep['id'], None, 'VERIFICATION_REQUIRED', 'PENDING', 'supervisor-queued')
                                st.warning("Verified! No team currently available; placed in dispatch queue.")
                            st.rerun()

                        # Option B: Manual direct team assignment
                        if avail_teams:
                            manual_team = st.selectbox(
                                "Or Manually Assign Available Team:",
                                avail_teams,
                                format_func=lambda t: f"{t['name']} (GPS: {t['lat']:.4f}, {t['lon']:.4f})",
                                key=f"mteam_{u_rep['id']}"
                            )
                            if st.button(f"👉 Directly Assign to {manual_team['name']}", key=f"man_disp_{u_rep['id']}", use_container_width=True):
                                dist = haversine(mapped_loc['lat'], mapped_loc['lon'], manual_team['lat'], manual_team['lon'])
                                now_str = datetime.now().isoformat(timespec='seconds')
                                zone_val = zone_choice.split()[0]
                                with db() as c:
                                    c.execute('''
                                        UPDATE reports SET
                                            location_id=?,
                                            assigned_zone=?,
                                            supervisor_notes=?,
                                            status='ASSIGNED'
                                        WHERE id=?
                                    ''', (mapped_loc['id'], zone_val, sup_notes, u_rep['id']))
                                    c.execute('''
                                        INSERT INTO tasks(report_id, team_id, status, assigned_at, distance_m)
                                        VALUES(?, ?, 'ASSIGNED', ?, ?)
                                    ''', (u_rep['id'], manual_team['id'], now_str, dist))
                                    task_id = c.execute('SELECT id FROM tasks WHERE report_id=?', (u_rep['id'],)).fetchone()['id']
                                    c.execute('UPDATE teams SET available=0 WHERE id=?', (manual_team['id'],))
                                history(u_rep['id'], task_id, 'VERIFICATION_REQUIRED', 'ASSIGNED', f"supervisor-manual-to-{manual_team['name']}")
                                st.success(f"Assigned directly to {manual_team['name']}!")
                                st.rerun()
                        else:
                            st.caption("ℹ️ No teams currently available for manual assignment.")

    # TAB 2: ALL COMPLAINTS & DISPATCH LOG
    with tab_all:
        st.subheader("📋 Comprehensive Cleanliness Reports Log")
        st.caption("Full audit record of every citizen complaint, exact location, timestamps, dispatch assignment and completion evidence.")

        with db() as c:
            all_reports_df = pd.read_sql_query('''
                SELECT 
                    r.ticket AS [Ticket ID],
                    r.category AS [Category],
                    r.priority AS [Priority],
                    r.status AS [Status],
                    COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS [Location / Landmark],
                    COALESCE(l.zone, r.assigned_zone, 'Unassigned') AS [Zone],
                    r.created_at AS [Reported At],
                    t.name AS [Assigned Team],
                    w.name AS [Assigned Worker],
                    ta.assigned_at AS [Assigned At],
                    ta.started_at AS [Started At],
                    ta.completed_at AS [Completed At]
                FROM reports r
                LEFT JOIN locations l ON l.id = r.location_id
                LEFT JOIN tasks ta ON ta.report_id = r.id
                LEFT JOIN teams t ON t.id = ta.team_id
                LEFT JOIN workers w ON w.id = ta.worker_id
                ORDER BY r.created_at DESC
            ''', c)

        if len(all_reports_df):
            # Interactive filter row
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(all_reports_df['Status'].unique()))
            with f_col2:
                zone_filter = st.selectbox("Filter by Zone", ["All"] + sorted(list(all_reports_df['Zone'].unique())))
            with f_col3:
                cat_filter = st.selectbox("Filter by Category", ["All"] + sorted(list(all_reports_df['Category'].unique())))

            filtered_df = all_reports_df.copy()
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['Status'] == status_filter]
            if zone_filter != "All":
                filtered_df = filtered_df[filtered_df['Zone'] == zone_filter]
            if cat_filter != "All":
                filtered_df = filtered_df[filtered_df['Category'] == cat_filter]

            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            st.caption(f"Showing {len(filtered_df)} of {len(all_reports_df)} total recorded reports.")

            # Detail inspect expandable
            with st.expander("🔍 Inspect Full Details & Photos of Any Ticket"):
                ticket_choices = all_reports_df['Ticket ID'].tolist()
                picked_ticket = st.selectbox("Select Ticket to Inspect", ticket_choices)
                if picked_ticket:
                    with db() as c:
                        p_rep = c.execute('''
                            SELECT r.*, COALESCE(l.name, 'Custom: ' || r.location_text, 'Custom location') AS loc_name
                            FROM reports r LEFT JOIN locations l ON l.id=r.location_id
                            WHERE r.ticket=?
                        ''', (picked_ticket,)).fetchone()
                        p_task = c.execute('''
                            SELECT ta.*, t.name AS team_name, w.name AS worker_name
                            FROM tasks ta
                            LEFT JOIN teams t ON t.id=ta.team_id
                            LEFT JOIN workers w ON w.id=ta.worker_id
                            WHERE ta.report_id=?
                        ''', (p_rep['id'],)).fetchone()
                        p_hist = c.execute('SELECT * FROM status_history WHERE report_id=? ORDER BY changed_at ASC', (p_rep['id'],)).fetchall()

                    d_col1, d_col2 = st.columns([2, 1])
                    with d_col1:
                        st.write(f"**Ticket:** `{p_rep['ticket']}` · **Category:** {p_rep['category']} · **Status:** `{p_rep['status']}`")
                        st.write(f"**Location:** {p_rep['loc_name']}")
                        if p_rep['description']:
                            st.write(f"**Citizen Description:** {p_rep['description']}")
                        if p_task:
                            st.write(f"**Assigned Team:** {p_task['team_name']} | **Worker:** {p_task['worker_name'] or 'Not yet picked'}")
                            st.write(f"**Timestamps:** Assigned: {p_task['assigned_at']} | Started: {p_task['started_at']} | Completed: {p_task['completed_at']}")
                    with d_col2:
                        if p_rep['reporter_photo'] and (APP_DIR / p_rep['reporter_photo']).exists():
                            st.image(str(APP_DIR / p_rep['reporter_photo']), caption="Citizen Reported Photo", width=180)

                    # Before and after if available
                    if p_task and (p_task['before_photo'] or p_task['after_photo']):
                        st.write("**Cleaning Verification Photographs:**")
                        c_cols = st.columns(2)
                        with c_cols[0]:
                            if p_task['before_photo'] and (APP_DIR / p_task['before_photo']).exists():
                                st.image(str(APP_DIR / p_task['before_photo']), caption="Before Cleaning", use_container_width=True)
                        with c_cols[1]:
                            if p_task['after_photo'] and (APP_DIR / p_task['after_photo']).exists():
                                st.image(str(APP_DIR / p_task['after_photo']), caption="After Cleaning (Resolved)", use_container_width=True)

                    if p_hist:
                        st.caption("Audit Timeline:")
                        for h in p_hist:
                            st.write(f"• `{h['changed_at']}`: {h['old_status'] or 'NEW'} ➔ **{h['new_status']}** (Actor: {h['actor']})")
        else:
            st.info("No reports registered yet.")

    # TAB 3: CLEANLINESS HOTSPOTS & ANALYTICS
    with tab_hotspots:
        st.subheader("🔥 Pushkaralu Cleanliness Hotspots")
        st.caption("Locations with recurring waste accumulation, bin overflow, or riverbank litter requiring increased municipal frequency.")

        if total:
            hotspots = reports.groupby(['location_name', 'category']).size().reset_index(name='report_count').sort_values('report_count', ascending=False)
            st.dataframe(
                hotspots.rename(columns={'location_name': 'Pushkaralu Location / Ghat', 'category': 'Issue Category', 'report_count': 'Total Reports'}),
                use_container_width=True,
                hide_index=True
            )

            st.divider()
            c_chart1, c_chart2 = st.columns(2)
            with c_chart1:
                st.markdown("#### Reports by Status")
                st.bar_chart(reports['status'].value_counts())
            with c_chart2:
                st.markdown("#### Reports by Ghat / Area")
                st.bar_chart(reports.groupby('location_name').size().sort_values(ascending=False))
        else:
            st.info("Analytics will populate as reports are submitted.")

    # TAB 4: FLEET & WORKER PERFORMANCE
    with tab_fleet:
        st.subheader("🚚 Cleaning Team Fleet Status")
        st.caption("Simulated operational telemetry · Straight-line Haversine nearest-dispatch tracking")

        st.dataframe(
            teams_df[['name', 'lat', 'lon', 'available', 'active']].rename(columns={
                'name': 'Team Name',
                'lat': 'Simulated Latitude',
                'lon': 'Simulated Longitude',
                'available': 'Available Flag (1=Ready, 0=Busy)',
                'active': 'Active Status'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader("👤 Worker Attribution & Resolution Leaderboard")
        st.caption("Number of cleanliness tasks completed and verified by individual sanitation workers under their respective teams:")

        st.dataframe(
            workers_df.rename(columns={
                'worker_name': 'Worker Name',
                'worker_code': 'Worker ID',
                'team_name': 'Team',
                'tasks_completed': 'Tasks Completed & Verified'
            }),
            use_container_width=True,
            hide_index=True
        )

    # TAB 5: LOCATION QR CODES (INTEGRATED IN ADMIN PORTAL)
    with tab_qr:
        st.subheader("🔳 Location-Specific QR Code Centre")
        st.caption("Generate, preview, and download QR codes for every pre-registered Pushkaralu ghat, riverbank step, and approach road. Scanning these codes opens the mobile citizen reporting portal with the location pre-filled.")

        base_url = st.text_input('Application Public Base URL', value=os.getenv('CLEANGHAT_BASE_URL', 'http://localhost:8501'), key="admin_qr_base_url")
        st.caption('ℹ️ Note: Default localhost URL is for local browser testing. Enter the deployed public HTTPS URL before printing QR posters for the festival.')

        locations = get_active_locations()

        qr_cols = st.columns(2)
        for idx, loc in enumerate(locations):
            with qr_cols[idx % 2]:
                with st.container(border=True):
                    qr_bytes, url = make_qr(loc['qr_code'], base_url)
                    qc1, qc2 = st.columns([2, 1])
                    with qc1:
                        st.markdown(f"#### {loc['name']}")
                        st.write(f"🏷️ Code: `{loc['qr_code']}` · 🚩 Zone: **{loc['zone']}**")
                        st.caption(f"Area Type: {loc['area_type']} · GPS: ({loc['lat']:.4f}, {loc['lon']:.4f})")
                        st.caption(f"Target URL: `{url}`")
                        st.download_button(
                            f"⬇️ Download {loc['qr_code']}.png",
                            data=qr_bytes,
                            file_name=f"{loc['qr_code']}.png",
                            mime='image/png',
                            key=f"adm_qr_btn_{loc['id']}",
                            use_container_width=True
                        )
                    with qc2:
                        st.image(qr_bytes, caption="Scan with Phone", width=140)

else:
    st.markdown('''
    <div class="gov-header">
        <div style="font-size:0.85rem; letter-spacing:0.8px; opacity:0.95; font-weight:600;">ANDHRA PRADESH SWACHH PUSHKARALU 2027</div>
        <h1>⚙️ System Settings & Simulation Disclaimers</h1>
        <p>Innovation Challenge Architecture Assumptions · Master Data Management</p>
        <div class="proto-badge">Hackathon Demonstration Telemetry</div>
    </div>
    ''', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('### 📡 Coverage & Scope (PS-07)')
        st.write('CleanGhat is built specifically for **PS-07: Waste Collection and Environmental Cleanliness** at the Godavari Pushkaralu 2027 festival. It models waste management across 10 strategic master locations (ghats, riverbanks, approach roads, public gathering spaces, and parking areas).')

    with st.container(border=True):
        st.markdown('### 🚚 Simulated Fleet & Dispatch Logic')
        st.write('Five demonstration cleaning teams (`Team Alpha` through `Team Echo`) are seeded with coordinates. Dispatch uses the Haversine formula to compute straight-line distances to the nearest available team, ensuring teams cannot take multiple simultaneous active tasks.')

    with st.container(border=True):
        st.markdown('### ⚠️ Student Prototype Disclaimers & Production Gaps')
        st.write('1. **Simulated Telemetry:** GPS coordinates, team locations, and worker activity are simulated for demonstration purposes. They are not connected to official municipal government databases.')
        st.write('2. **Production Enhancements:** A real-world municipal deployment would integrate road-network routing (OSRM / Google Maps), hardware IoT bin level sensors, SMS/WhatsApp gateway notifications, and role-based biometric worker login.')

    with st.container(border=True):
        st.markdown('### 🔄 Reset Demo Reports & Tasks')
        st.warning('Resetting demo data clears all submitted reports, tasks, and audit logs. All 10 master locations, 5 teams, and 10 worker accounts will be safely preserved.')
        if st.button('Reset Submitted Reports and Tasks', type='secondary'):
            with db() as c:
                c.execute('DELETE FROM status_history')
                c.execute('DELETE FROM tasks')
                c.execute('DELETE FROM reports')
                c.execute('UPDATE teams SET available=1')
                c.execute("UPDATE teams SET available=0 WHERE name='Team Delta'")
            st.success('Demo reports and tasks cleared successfully. Master locations, teams, and workers retained.')
            st.rerun()

st.divider()
st.caption('CleanGhat · Godavari Pushkaralu 2027 Innovation Challenge · PS-07 Waste Collection & Cleanliness · Simulated Data Only')


    