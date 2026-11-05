import json
import re
import csv
from datetime import datetime, date, timedelta

with open("/Users/sharonxu/gabriel-quest-map/materi_belum_selesai.json", "r", encoding="utf-8") as f:
    raw = json.load(f)

with open("/Users/sharonxu/gabriel-quest-map/catalog_verified.json", "r", encoding="utf-8") as f:
    catalog_verified = json.load(f)

# Ensure known 5-char suffixed slugs are populated in catalog_verified
for a in catalog_verified.get("waydivers-1-term-1-ay-20262027", {}).get("activities", []):
    if a["activity_id"] == 978921:
        a["verified_slug"] = "group-session-2-meeting-1-61y2y"
for a in catalog_verified.get("waydivers-1-term-2-ay-20262027", {}).get("activities", []):
    if a["activity_id"] == 1030167:
        a["verified_slug"] = "academic-calendar-j3bow"
for a in catalog_verified.get("year-1-pjok-semester-1-ta-20262027", {}).get("activities", []):
    if a["activity_id"] == 980217:
        a["verified_slug"] = "jumat-24-jul-2026-jangan-lupa-pemanasan-dan-pendinginan-gih5x"

MONTH_MAP = {
    "jan": 1, "januari": 1, "january": 1,
    "feb": 2, "februari": 2, "february": 2,
    "mar": 3, "maret": 3, "march": 3,
    "apr": 4, "april": 4,
    "mei": 5, "may": 5,
    "jun": 6, "juni": 6, "june": 6,
    "jul": 7, "juli": 7, "july": 7,
    "agu": 8, "agt": 8, "agustus": 8, "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "okt": 10, "oktober": 10, "oct": 10, "0ct": 10, "october": 10,
    "nov": 11, "november": 11,
    "des": 12, "desember": 12, "dec": 12, "december": 12,
}

# Official Sekolah.mu & Living English child-account handoff query parameters (for 09-cross-platform-learning-page middleware).
# Ensures that if the browser is logged into the Parent account (sharonpm1996@gmail.com), Sekolah.mu automatically
# switches to Gabriel's student session instead of throwing Error 500 ("Halaman Belum Berhasil Dimuat").
CHILD_HANDOFF_QUERY = (
    "src_ugp=2d5b9091-678a-42d1-a8a8-256ce2ac5638"
    "&src_email=sharonpm1996%2BGabrielAltair%2Bv2po7@gmail.com"
    "&src_is_sys_email=1"
    "&src_account_type=Anak/Remaja"
    "&src_parent_email=sharonpm1996@gmail.com"
)

# Verified fallback classroom (/c) URLs for each of Gabriel's 7 programs
# (used only when an activity or chapter has no closer verified sibling in catalog_verified.json).
VERIFIED_CLASSROOM_URLS = {
    "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027": (
        f"https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027/rabu-22-juli-2026-yuk-simak-bersama/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027": (
        f"https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027/thursday-6-august-2026-listening-to-audiobook-ready-set-brush/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027": (
        f"https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027/jumat-24-jul-2026-jangan-lupa-pemanasan-dan-pendinginan-gih5x/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-homeroom-20262027": (
        f"https://smm.sekolah.mu/program/year-1-homeroom-20262027/selamat-datang-di-kelas-1/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/memulai-belajar-di-smm-year-13-ta-20262027": (
        f"https://smm.sekolah.mu/program/memulai-belajar-di-smm-year-13-ta-20262027/kontak-sekolah-murid-merdeka-1-4-4-4/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://livingenglish.sekolah.mu/program/waydivers-1-term-1-ay-20262027": (
        f"https://livingenglish.sekolah.mu/program/waydivers-1-term-1-ay-20262027/group-session-2-meeting-1-61y2y/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027": (
        f"https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027/academic-calendar-j3bow/c?{CHILD_HANDOFF_QUERY}"
    ),
}

# Latest verified November classroom URLs per program (used for upcoming Nov-Dec curriculum weeks not yet uploaded by teachers)
LATEST_NOV_CLASSROOM_URLS = {
    "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027": (
        f"https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027/jumat-13-november-2026-unggah-lk-minggu-6/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027": (
        f"https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027/friday-6-november-2026-padlet-ten-apples-up-on-top/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027": (
        f"https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027/jumat-06-nov-2026-ayo-bergerak-bersama/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://smm.sekolah.mu/program/year-1-homeroom-20262027": (
        f"https://smm.sekolah.mu/program/year-1-homeroom-20262027/jumat-13-november-2026-belajar-live-homeroom-bagaimana-perasaanku/c?{CHILD_HANDOFF_QUERY}"
    ),
    "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027": (
        f"https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027/academic-calendar-j3bow/c?{CHILD_HANDOFF_QUERY}"
    ),
}

def get_my_learning_url(program_url, source_tab=""):
    if "livingenglish.sekolah.mu" in program_url or "Living English" in source_tab:
        return "https://livingenglish.sekolah.mu/my-learning"
    return "https://smm.sekolah.mu/my-learning"

def resolve_activity_classroom_url(program_url, module_str, title_clean, is_upcoming_schedule=False):
    clean_url = program_url.rstrip("/")
    pslug = clean_url.split("/")[-1]
    acts = [a for a in catalog_verified.get(pslug, {}).get("activities", []) if not a.get("is_addon")]
    mod_norm = module_str.strip()
    t_norm = title_clean.strip()

    # 1. Exact activity match (by chapter + activity title, or activity title)
    matched_act = None
    for a in acts:
        if a["activity_name"].strip() == t_norm and a["chapter_name"].strip() == mod_norm:
            matched_act = a
            break
    if not matched_act:
        for a in acts:
            if a["activity_name"].strip() == t_norm:
                matched_act = a
                break
    if matched_act and matched_act.get("verified_slug"):
        slug = matched_act["verified_slug"]
        return (f"{clean_url}/{slug}/c?{CHILD_HANDOFF_QUERY}", "exact_activity", matched_act["activity_id"])

    # 2. Same chapter + same date prefix (e.g. "Selasa, 10 November 2026")
    date_prefix = t_norm.split("|")[0].strip().lower() if "|" in t_norm else ""
    chap_verified = [a for a in acts if a["chapter_name"].strip() == mod_norm and a.get("verified_slug")]
    if date_prefix and chap_verified:
        for a in chap_verified:
            if a["activity_name"].strip().lower().startswith(date_prefix):
                slug = a["verified_slug"]
                return (f"{clean_url}/{slug}/c?{CHILD_HANDOFF_QUERY}", "same_date", a["activity_id"])

    # 3. Nearest verified activity in the SAME chapter/week (so the classroom sidebar opens at that exact week)
    if chap_verified:
        target_order = matched_act.get("activity_order", 1) if matched_act else 1
        nearest = min(chap_verified, key=lambda a: abs(a.get("activity_order", 1) - target_order))
        slug = nearest["verified_slug"]
        return (f"{clean_url}/{slug}/c?{CHILD_HANDOFF_QUERY}", "same_week", nearest["activity_id"])

    # 4. If it's an upcoming Nov-Dec curriculum item (or End of Semester Reflection), open the latest verified November week
    if is_upcoming_schedule or "refleksi" in mod_norm.lower() or "december" in mod_norm.lower() or "desember" in mod_norm.lower():
        if clean_url in LATEST_NOV_CLASSROOM_URLS:
            return (LATEST_NOV_CLASSROOM_URLS[clean_url], "latest_nov_week", None)

    # 5. Nearest verified activity in adjacent chapter (e.g. PJOK Triwulan 2 Week 1 -> Week 2)
    if matched_act:
        all_verified = [a for a in acts if a.get("verified_slug")]
        if all_verified:
            target_id = matched_act["activity_id"]
            nearest = min(all_verified, key=lambda a: abs(a["activity_id"] - target_id))
            slug = nearest["verified_slug"]
            return (f"{clean_url}/{slug}/c?{CHILD_HANDOFF_QUERY}", "nearest_chapter", nearest["activity_id"])

    return (VERIFIED_CLASSROOM_URLS.get(clean_url, clean_url), "program_entry", None)

def extract_date(module_str, title_str, program_str, act_num):
    m_low = module_str.lower()
    t_low = title_str.lower()

    # Special fix 1: SMM English Week 5 (2 - 6 November 2026) item #79 has portal typo "Thursday, 5 October 2026"
    if "2 - 6 november" in m_low and "5 october" in t_low:
        return "2026-11-05"

    # Special fix 2: End-of-Semester 1 Reflections ("Refleksi Akhir Tahun" or PJOK "REFLEKSI")
    if "refleksi akhir tahun" in m_low:
        return "2026-12-18"
    if m_low.strip() == "refleksi" and "PJOK" in program_str:
        return "2026-12-11"

    # Special fix 3: SMM English Theme 2 Live Session (covers Theme 2 up to Week 6 Nov)
    if "live session/tatap muka english theme 2" in m_low:
        if act_num == 53:
            return "2026-11-02"
        if act_num == 55:
            return "2026-11-06"

    # Special fix 4: Daring Rutin RISING & Tema 1 Minggu 8 (31 Agt-4 Sept) & Homeroom #28
    if "rising - sesi kurikulum" in m_low and act_num == 73:
        return "2026-08-22"
    if "31 agt-4 sept" in m_low or "31 aug - 4 september" in m_low:
        m_title = re.search(r"\b(\d{1,2})\s+([A-Za-z0]+)", title_str)
        if m_title and m_title.group(2).lower() in MONTH_MAP:
            d_val = int(m_title.group(1))
            m_val = MONTH_MAP[m_title.group(2).lower()]
            return f"2026-{m_val:02d}-{d_val:02d}"
        if act_num in (87, 88, 89):
            return "2026-08-31"
        if act_num == 94:
            return "2026-09-02"
        if act_num == 99:
            return "2026-09-04"
        return "2026-09-01"
    if "memulai belajar di tema 2" in t_low and "Homeroom" in program_str:
        return "2026-10-05"

    # Special fix 5: Living English Term 2 Academic Calendar, Summative Description & W5
    if "Waydivers 1 Term 2" in program_str:
        if "welcome to term 2" in m_low or "academic calendar" in t_low:
            return "2026-11-01"
        if "summative description" in m_low or "summative description" in t_low:
            return "2026-11-02"
        if "w5" in m_low or "2-7 november" in m_low:
            offset = max(0, min(5, act_num - 30))
            return f"2026-11-{2 + offset:02d}"

    # 1. Try explicit date in title_str or module_str
    for text in [title_str, module_str]:
        if text is title_str:
            m = re.search(r"\b(\d{1,2})\s+([A-Za-z0]+)(?:\s+(\d{4}))?", text)
            if m:
                day = int(m.group(1))
                mon_raw = m.group(2).lower()
                if mon_raw in MONTH_MAP and 1 <= day <= 31:
                    month = MONTH_MAP[mon_raw]
                    return f"2026-{month:02d}-{day:02d}"

        m2 = re.search(r"\b(\d{1,2})\s*-\s*(\d{1,2})\s+([A-Za-z0]+)", text)
        if m2:
            day_start = int(m2.group(1))
            day_end = int(m2.group(2))
            mon_raw = m2.group(3).lower()
            if mon_raw in MONTH_MAP and 1 <= day_start <= 31:
                month = MONTH_MAP[mon_raw]
                span = max(1, day_end - day_start + 1)
                day_adj = min(30, day_start + (act_num % span))
                return f"2026-{month:02d}-{day_adj:02d}"

        m = re.search(r"\b(\d{1,2})\s+([A-Za-z0]+)(?:\s+(\d{4}))?", text)
        if m:
            day = int(m.group(1))
            mon_raw = m.group(2).lower()
            if mon_raw in MONTH_MAP and 1 <= day <= 31:
                month = MONTH_MAP[mon_raw]
                return f"2026-{month:02d}-{day:02d}"

    # 2. Living English Term 1 / Term 2 week estimation (strictly chronological)
    if "Waydivers 1 Term 1" in program_str:
        w = re.search(r"Week\s*(\d+)", module_str, re.I)
        if w:
            wk = int(w.group(1))
            start_dt = date(2026, 7, 20) + timedelta(days=(wk - 1) * 7 + (act_num % 5))
            return start_dt.isoformat()
    if "Waydivers 1 Term 2" in program_str:
        w = re.search(r"W(\d+)", module_str, re.I)
        if w:
            wk = int(w.group(1))
            start_dt = date(2026, 10, 5) + timedelta(days=(wk - 1) * 7 + (act_num % 5))
            return start_dt.isoformat()
        return "2026-11-01"

    # 3. Homeroom / Memulai Belajar di SMM early orientation
    if "Memulai Belajar di SMM" in program_str:
        return "2026-07-12"
    if "Penguatan Komunitas" in module_str:
        return "2026-07-14"

    return "2026-09-30"

ISLAND_META = {
    "daring": {
        "id": "daring",
        "name": "Pulau Petualang Cilik",
        "subtitle": "Daring Rutin (Tema 1 & Tema 2 s/d Akhir Sem 1)",
        "icon": "🏝️",
        "color": "#0ea5e9",
        "zoneLabel": "Air Terjun & Hutan Tropis",
        "mapCenter": {"x": 25, "y": 45}
    },
    "english": {
        "id": "english",
        "name": "Pulau English Kingdom",
        "subtitle": "SMM Year 1 English (s/d Akhir Sem 1)",
        "icon": "🏰",
        "color": "#f59e0b",
        "zoneLabel": "Pondok Pantai Emas",
        "mapCenter": {"x": 61, "y": 26}
    },
    "living_english": {
        "id": "living_english",
        "name": "Pulau Kapal Pasar",
        "subtitle": "Living English Waydivers 1 (Term 1 & Term 2)",
        "icon": "⛵",
        "color": "#10b981",
        "zoneLabel": "Dermaga Kapal Layar",
        "mapCenter": {"x": 45, "y": 76}
    },
    "pjok": {
        "id": "pjok",
        "name": "Pulau Gerak Ceria",
        "subtitle": "PJOK Semester 1 (Mode Pemulihan Aman)",
        "icon": "🌋",
        "color": "#f97316",
        "zoneLabel": "Pulau Gunung Berapi Ramah",
        "mapCenter": {"x": 71, "y": 72}
    },
    "homeroom": {
        "id": "homeroom",
        "name": "Pulau Mercusuar",
        "subtitle": "Homeroom & Refleksi Semester 1",
        "icon": "🚨",
        "color": "#8b5cf6",
        "zoneLabel": "Menara Mercusuar",
        "mapCenter": {"x": 86, "y": 47}
    }
}

def get_island_id(program_str):
    if "Daring Rutin" in program_str:
        return "daring"
    if "Year 1 | English" in program_str:
        return "english"
    if "Waydivers" in program_str or "Living English" in program_str:
        return "living_english"
    if "PJOK" in program_str:
        return "pjok"
    return "homeroom"

def classify_quest(program_str, module_str, title_clean, jenis, iso_date, is_upcoming_schedule=False):
    t_low = title_clean.lower()
    m_low = module_str.lower()
    is_nov_to_end_sem1 = iso_date >= "2026-11-01"

    is_day_off = "day off" in t_low
    is_parent_admin = (
        "Memulai Belajar di SMM" in program_str
        or "panduan orang tua" in t_low
        or "buku panduan orang tua" in t_low
        or "daftar kebutuhan belajar" in t_low
        or "pembagian rombongan" in t_low
        or "kalender akademik" in t_low
        or "academic calendar" in t_low
        or "jadwal presentasi" in t_low
        or "zoom link and schedule" in t_low
        or "timeline tema" in t_low
        or "refleksi dan aspirasi orang tua" in t_low
    )
    is_live_session = (
        jenis == "Diskusi & Pertemuan"
        or "belajar live" in t_low
        or "group session" in t_low
        or "pertemuan belajar live" in t_low
    )
    is_physical_pjok = (
        "PJOK" in program_str
        and any(k in t_low or k in m_low for k in ["berlari", "melompat", "gerak kaki", "tantangan gerak", "senam", "aktivitas fisik", "kebugaran", "ketangkasan"])
    )
    is_boss = (
        jenis == "Tugas dan Asesment"
        or "sumatif" in t_low
        or "summative" in t_low
        or "formatif" in t_low
        or "formative" in t_low
        or "assessment" in t_low
        or "checkpoint" in t_low
        or "asesmen" in t_low
    )

    kid_actionable = True
    if is_boss:
        category = "boss_quest"
        stars = 3
        badge = "🏆 Misi Bintang 3 (Tugas & Asesmen)" if is_nov_to_end_sem1 else "🏆 Misi Bintang 3 (Tugas)"
    elif is_live_session:
        category = "live_session"
        stars = 2
        badge = "🎥 Kelas Live / Group Session (Nov–Des)" if is_nov_to_end_sem1 else "🎥 Sesi Live / Rekaman"
    elif is_parent_admin:
        category = "parent_admin"
        stars = 1
        badge = "📋 Panduan & Kebutuhan Belajar"
    elif is_day_off:
        category = "holiday"
        stars = 1
        badge = "🏖️ Info Hari Libur Portal"
    else:
        category = "story_quest"
        stars = 2
        badge = "📖 Misi Belajar (Materi Nov–Des)" if is_nov_to_end_sem1 else "📖 Misi Belajar (Materi)"

    if is_upcoming_schedule:
        timeline_status = "belum_berjalan"
        portal_unlock_status = "upcoming_sem1_schedule"
        timeline_badge = "🗓️ Belum Berjalan • Jadwal Nov–Akhir Sem 1"
    elif is_nov_to_end_sem1:
        timeline_status = "belum_berjalan"
        portal_unlock_status = "in_portal_nov_dec"
        timeline_badge = "📅 Belum Berjalan • Materi Nov–Akhir Sem 1"
    else:
        timeline_status = "belum_selesai"
        portal_unlock_status = "in_portal_overdue"
        timeline_badge = "⏳ Belum Selesai • Kejar Materi (Jul–Okt)"

    return {
        "category": category,
        "kidActionable": kid_actionable,
        "isPhysicalCaution": is_physical_pjok,
        "stars": stars,
        "badge": badge,
        "timelineStatus": timeline_status,
        "portalUnlockStatus": portal_unlock_status,
        "timelineBadge": timeline_badge,
        "isUpcomingCurriculum": is_upcoming_schedule,
    }

# Upcoming Semester 1 Curriculum items (Weeks 6 - 11: 9 November - 18 December 2026)
UPCOMING_SEM1_ITEMS = [
    # ================= DARING RUTIN (Minggu 6 Resmi di Portal: 9-13 Nov 2026 + Minggu 7-11: 16 Nov - 17 Des 2026) =================
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "199. Daftar Kebutuhan Belajar Minggu 6", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-09"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "200. Pertemuan Belajar Live 1: Sudah Sampai Mana, ya?", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-09"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "201. Senin, 9 November 2026 | Checkpoint Sumatif", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-09"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "202. Selasa, 10 November 2026 | Mengenang Jasa Pahlawan", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-10"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "203. Selasa, 10 November 2026 | Menulis Kosakata Baru", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-10"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "204. Selasa, 10 November 2026 | Kreasi Bunga Pahlawanku", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-10"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "205. Pertemuan Belajar Live 2: Berbagi dengan Temanku", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-11"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "206. Rabu, 11 November 2026 | Berapa Bagian yang Aku Miliki, ya?", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-11"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "207. Kamis, 12 November 2026 | Bantuan yang Kuberikan", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-12"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "208. Kamis, 12 November 2026 | Waktu Membaca: Riri dan Cuaca", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-12"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "209. Kamis, 12 November 2026 | Padlet Bercerita: Riri dan Cuaca", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-12"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 6 (9-13 Nov 2026) | Aku dan Sumatifku", "210. Jumat, 13 November 2026 | Unggah LK Minggu 6", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-13"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 7 (16-20 Nov 2026) | Pengerjaan Koper Keluargaku", "205. Senin, 16 November 2026 | Pertemuan Belajar Live 1: Pengerjaan Koper Aku dan Keluargaku", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-16"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 7 (16-20 Nov 2026) | Pengerjaan Koper Keluargaku", "206. Rabu, 18 November 2026 | Pertemuan Belajar Live 2 & Eksplorasi Cerita Tema 2", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-18"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 7 (16-20 Nov 2026) | Pengerjaan Koper Keluargaku", "207. Kamis, 19 November 2026 | Galeri Karya & Unggah LK Minggu 7", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-19"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "RISING - Sesi Kurikulum Terpersonalisasi Semester 1 (Tema 2)", "208. Jumat, 20 November 2026 | Sesi RISING Tema 2 (Kurikulum Terpersonalisasi)", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-20"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 8 (23-27 Nov 2026) | Finalisasi Sumatifku", "209. Senin, 23 November 2026 | Pertemuan Belajar Live 1: Menjadi Presenter Hebat Tema 2", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-23"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 8 (23-27 Nov 2026) | Finalisasi Sumatifku", "210. Selasa, 24 November 2026 | Checkpoint Sumatif 3: Koper Aku dan Keluargaku", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-24"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 8 (23-27 Nov 2026) | Finalisasi Sumatifku", "211. Jumat, 27 November 2026 | Asesmen Sumatif Tema 2: Koper Aku dan Keluargaku (Finalisasi)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-27"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 9 (30 Nov - 4 Des 2026) | Presentasi Sumatif 1", "212. Senin, 30 November 2026 | Pertemuan Belajar Live 1: Presentasi Sumatif 'Aku Penjelajah Dunia'", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-11-30"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 9 (30 Nov - 4 Des 2026) | Presentasi Sumatif 1", "213. Rabu, 2 Desember 2026 | Pertemuan Belajar Live 2: Presentasi Sumatif 'Aku Penjelajah Dunia'", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-02"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 9 (30 Nov - 4 Des 2026) | Presentasi Sumatif 1", "214. Jumat, 4 Desember 2026 | Latihan Literasi & Numerasi Minggu 9", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-04"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 10 (7-11 Des 2026) | Presentasi Sumatif 2 & Pameran", "215. Senin, 7 Desember 2026 | Pertemuan Belajar Live: Presentasi Sumatif Lanjutan", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-07"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 10 (7-11 Des 2026) | Presentasi Sumatif 2 & Pameran", "216. Rabu, 9 Desember 2026 | Memilih Karya Terbaik untuk Pameran Semester 1", "Materi", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-09"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 10 (7-11 Des 2026) | Presentasi Sumatif 2 & Pameran", "217. Kamis, 10 Desember 2026 | Unggah LK Minggu 10", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-10"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 11 (14-18 Des 2026) | Refleksiku Akhir Semester 1", "218. Selasa, 15 Desember 2026 | Apa yang Sudah Aku Pelajari di Tema 2 (Semester 1)?", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-15"),
    ("SMM", "Year 1 | Daring Rutin | Semester 1 | 2026/2027", "Tema 2 Minggu 11 (14-18 Des 2026) | Refleksiku Akhir Semester 1", "219. Kamis, 17 Desember 2026 | Pengumpulan Lensa Aksara Akhir Semester 1", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-daring-rutin-semester-1-20262027", "2026-12-17"),

    # ================= SMM ENGLISH (Week 6 - Week 10: 9 Nov - 11 Des 2026) =================
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 6 | 9 - 13 November 2026 | Actions & Daily Routines", "82. Monday, 9 November 2026 | Slides & Read-Aloud: What Are We Doing?", "Materi", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-09"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 6 | 9 - 13 November 2026 | Actions & Daily Routines", "83. Wednesday, 11 November 2026 | Word & Sentence Builder Game (Week 6)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-11"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 6 | 9 - 13 November 2026 | Actions & Daily Routines", "84. Friday, 13 November 2026 | Worksheet & Padlet Activity Week 6", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-13"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 7 | 16 - 20 November 2026 | My Family & Home Project", "85. Monday, 16 November 2026 | Slides of Theme 2 Summative Preparation", "Materi", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-16"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 7 | 16 - 20 November 2026 | My Family & Home Project", "86. Wednesday, 18 November 2026 | Summative Project Theme 2: Step 1 & 2", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-18"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 7 | 16 - 20 November 2026 | My Family & Home Project", "87. Thursday, 19 November 2026 | Summative Project Theme 2: Step 3", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-19"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 8 | 23 - 27 November 2026 | Project Showcase 1 (Theme 2)", "88. Monday, 23 November 2026 | Project Showcase 1 (Theme 2)", "Materi", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-23"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 8 | 23 - 27 November 2026 | Project Showcase 1 (Theme 2)", "89. Tuesday, 24 November 2026 | Phonics & Sight Words Practice (Theme 2)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-24"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 8 | 23 - 27 November 2026 | Project Showcase 1 (Theme 2)", "90. Thursday, 26 November 2026 | Let's Give Your Theme 2 Project One Last Check!", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-26"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 9 | 30 Nov - 4 December 2026 | Project Showcase 2 (Theme 2)", "91. Monday, 30 November 2026 | Project Showcase 2 (Theme 2)", "Materi", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-11-30"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 9 | 30 Nov - 4 December 2026 | Project Showcase 2 (Theme 2)", "92. Wednesday, 2 December 2026 | Reading & Listening Mystery Game (Theme 2)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-12-02"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 9 | 30 Nov - 4 December 2026 | Project Showcase 2 (Theme 2)", "93. Thursday, 3 December 2026 | Assessment Checkpoint (Theme 2)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-12-03"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 10 | 7-11 December 2026 | End of Theme 2", "94. Tuesday, 8 December 2026 | Padlet: Theme 2 Reflection & Project Gallery", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-12-08"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 10 | 7-11 December 2026 | End of Theme 2", "95. Thursday, 10 December 2026 | Final Assessment Checkpoint (Semester 1)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-12-10"),
    ("SMM", "Year 1 | English | Semester 1 | TA 2026/2027", "Week 10 | 7-11 December 2026 | End of Theme 2", "96. Friday, 11 December 2026 | Deadline All Assessments (Theme 2 / Semester 1)", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-english-semester-1-ta-20262027", "2026-12-11"),

    # ================= LIVING ENGLISH (Term 2 W6 - W11: 9 Nov - 18 Des 2026) =================
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W6 / 9-14 November - Developing & Designing Information", "38. Pre-Learning 1 & 2 (Week 6)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-09"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W6 / 9-14 November - Developing & Designing Information", "39. Group Session 1 (Online Session - Week 6)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-10"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W6 / 9-14 November - Developing & Designing Information", "40. Group Session 2 & 3 (Meeting 11 & 12)", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-12"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W6 / 9-14 November - Developing & Designing Information", "41. Individualized Session (Week 6)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-14"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W7 / 16-21 November - Formative Assessment & Progress Check", "42. Group Session 1 (Online Session - Week 7)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-16"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W7 / 16-21 November - Formative Assessment & Progress Check", "43. Group Session 2 & 3 (Meeting 13 & 14) - Progress Check", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-19"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W7 / 16-21 November - Formative Assessment & Progress Check", "44. Formative Assessment & Individualized Session (Week 7)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-21"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W8 / 23-28 November - Building Term 2 Summative Project", "45. Pre-Learning 1 & 2 (Week 8)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-23"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W8 / 23-28 November - Building Term 2 Summative Project", "46. Group Session 1, 2 & 3 (Meeting 15 & 16)", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-26"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W8 / 23-28 November - Building Term 2 Summative Project", "47. Individualized Session (Week 8)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-28"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W9 / 30 Nov - 5 December - Rehearsing Term 2 Presentation", "48. Pre-Learning 1 & 2 (Week 9)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-11-30"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W9 / 30 Nov - 5 December - Rehearsing Term 2 Presentation", "49. Group Session 1, 2 & 3 (Meeting 17 & 18)", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-03"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W9 / 30 Nov - 5 December - Rehearsing Term 2 Presentation", "50. Individualized Session (Week 9)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-05"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W10 / 7-12 December - Term 2 Summative Showcase", "51. Pre-Learning 1, 2 & 3 (Week 10 - Showcase Prep)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-07"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W10 / 7-12 December - Term 2 Summative Showcase", "52. Group Session 1, 2 & 3 (Meeting 19 & 20 - Summative Showcase)", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-10"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W10 / 7-12 December - Term 2 Summative Showcase", "53. Individualized Session (Week 10 - Showcase Evaluation)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-12"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W11 / 14-18 December - End of Term 2 & Semester 1 Wrap-Up", "54. Pre-Learning 1 & 2 (Week 11 - Term 2 Reflection)", "Materi", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-14"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W11 / 14-18 December - End of Term 2 & Semester 1 Wrap-Up", "55. Group Session 1, 2 & 3 (Meeting 21 & 22 - Term 2 Closing)", "Diskusi & Pertemuan", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-16"),
    ("Living English", "Waydivers 1 Term 2 AY 2026/2027", "W11 / 14-18 December - End of Term 2 & Semester 1 Wrap-Up", "56. Individualized Session (Week 11 - Final Semester 1 Feedback)", "Tugas dan Asesment", "https://livingenglish.sekolah.mu/program/waydivers-1-term-2-ay-20262027", "2026-12-18"),

    # ================= PJOK (Week 6 - Week 9: 9 Nov - 4 Des 2026) =================
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 6 | 09 - 13 November 2026 | Aktivitas Fisik 2", "82. Selasa, 10 Nov 2026 | Mengenal Latihan Daya Tahan & Kebugaran Tubuh", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-10"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 6 | 09 - 13 November 2026 | Aktivitas Fisik 2", "83. Jumat, 13 Nov 2026 | Praktik Gerak Aktivitas Fisik 2 Dengan Aman", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-13"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 7 | 16 - 20 November 2026 | Formatif Aktivitas Fisik", "84. Selasa, 17 Nov 2026 | Mengenal Kebersihan & Kesehatan Diri Setelah Berolahraga", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-17"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 7 | 16 - 20 November 2026 | Formatif Aktivitas Fisik", "85. Jumat, 20 Nov 2026 | [AKTIVITAS MANDIRI] Formatif Aktivitas Fisik Tema 2", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-20"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 8 | 23 - 27 November 2026 | Permainan & Ketangkasan", "86. Selasa, 24 Nov 2026 | Mengenal Permainan Ketangkasan Sederhana di Rumah", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-24"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 8 | 23 - 27 November 2026 | Permainan & Ketangkasan", "87. Jumat, 27 Nov 2026 | Tantangan Gerak Ketangkasan & Keseimbangan", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-11-27"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 9 | 30 Nov - 04 December 2026 | Kilas Balik & Evaluasi Akhir Semester 1", "88. Selasa, 01 Des 2026 | Mengulas Kebiasaan Hidup Sehat Semester 1", "Materi", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-12-01"),
    ("SMM", "Year 1 | PJOK | Semester 1 | TA 2026/2027", "Week 9 | 30 Nov - 04 December 2026 | Kilas Balik & Evaluasi Akhir Semester 1", "89. Jumat, 04 Des 2026 | Evaluasi & Catatan Kebugaran Akhir Semester 1", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-pjok-semester-1-ta-20262027", "2026-12-04"),

    # ================= HOMEROOM (Minggu 7 - Minggu 10: 20 Nov - 11 Des 2026) =================
    ("SMM", "Year 1 | Homeroom | 2026/2027", "Tema 2: Penjelajah Dunia", "36. Jumat, 20 November 2026 | Menulis Jurnal Refleksi Minggu 7", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-homeroom-20262027", "2026-11-20"),
    ("SMM", "Year 1 | Homeroom | 2026/2027", "Tema 2: Penjelajah Dunia", "37. Jumat, 27 November 2026 | [Belajar Live Homeroom] Siap Presentasi Proyek Sumatifku!", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-homeroom-20262027", "2026-11-27"),
    ("SMM", "Year 1 | Homeroom | 2026/2027", "Tema 2: Penjelajah Dunia", "38. Jumat, 4 Desember 2026 | Menulis Jurnal Refleksi Minggu 9", "Tugas dan Asesment", "https://smm.sekolah.mu/program/year-1-homeroom-20262027", "2026-12-04"),
    ("SMM", "Year 1 | Homeroom | 2026/2027", "Tema 2: Penjelajah Dunia", "39. Jumat, 11 Desember 2026 | [Belajar Live Homeroom] Apresiasi Karya & Perayaan Akhir Semester 1", "Diskusi & Pertemuan", "https://smm.sekolah.mu/program/year-1-homeroom-20262027", "2026-12-11"),
]

all_quests = []

for source_tab, rows in [("SMM", raw["smmItems"]), ("Living English", raw["leItems"])]:
    for idx, r in enumerate(rows, start=1):
        program_str = r[0].strip()
        module_str = r[1].strip()
        raw_title = r[2].strip()
        jenis = r[3].strip()
        program_url = r[4].strip().rstrip("/")

        m_num = re.match(r"^(\d+)\.\s*(.*)$", raw_title)
        if m_num:
            act_num = int(m_num.group(1))
            act_num_str = m_num.group(1)
            title_clean = m_num.group(2).strip()
        else:
            act_num = idx
            act_num_str = str(idx)
            title_clean = raw_title

        my_learning_url = get_my_learning_url(program_url, source_tab)
        direct_url, link_match_type, matched_aid = resolve_activity_classroom_url(
            program_url, module_str, title_clean, is_upcoming_schedule=False
        )
        exact_verified = (link_match_type == "exact_activity")

        iso_date = extract_date(module_str, title_clean, program_str, act_num)
        island_id = get_island_id(program_str)
        meta = classify_quest(program_str, module_str, title_clean, jenis, iso_date, is_upcoming_schedule=False)

        quest_id = f"{source_tab.lower().replace(' ', '_')}_{idx}"
        all_quests.append({
            "id": quest_id,
            "sheetRowIndex": idx,
            "sourceTab": source_tab,
            "program": program_str,
            "islandId": island_id,
            "islandName": ISLAND_META[island_id]["name"],
            "islandIcon": ISLAND_META[island_id]["icon"],
            "module": module_str,
            "activityNumber": act_num,
            "rawTitle": raw_title,
            "title": title_clean,
            "jenis": jenis,
            "programUrl": program_url,
            "myLearningUrl": my_learning_url,
            "directUrl": direct_url,
            "linkMatchType": link_match_type,
            "activityId": matched_aid,
            "exactVerified": exact_verified,
            "date": iso_date,
            **meta
        })

# Append Upcoming Semester 1 Curriculum items (Weeks 6 - 11: Nov - Akhir Semester 1)
for u_idx, item in enumerate(UPCOMING_SEM1_ITEMS, start=1):
    source_tab, program_str, module_str, raw_title, jenis, program_url, iso_date = item
    program_url = program_url.strip().rstrip("/")
    m_num = re.match(r"^(\d+)\.\s*(.*)$", raw_title)
    if m_num:
        act_num = int(m_num.group(1))
        title_clean = m_num.group(2).strip()
    else:
        act_num = 300 + u_idx
        title_clean = raw_title

    my_learning_url = get_my_learning_url(program_url, source_tab)
    direct_url, link_match_type, matched_aid = resolve_activity_classroom_url(
        program_url, module_str, title_clean, is_upcoming_schedule=True
    )
    already_in_portal = link_match_type in ("exact_activity", "same_date", "same_week")
    island_id = get_island_id(program_str)
    meta = classify_quest(program_str, module_str, title_clean, jenis, iso_date, is_upcoming_schedule=(not already_in_portal))

    quest_id = f"upcoming_sem1_{u_idx}"
    all_quests.append({
        "id": quest_id,
        "sheetRowIndex": 1000 + u_idx,
        "sourceTab": source_tab if already_in_portal else f"{source_tab} (Jadwal Sem 1)",
        "program": program_str,
        "islandId": island_id,
        "islandName": ISLAND_META[island_id]["name"],
        "islandIcon": ISLAND_META[island_id]["icon"],
        "module": module_str,
        "activityNumber": act_num,
        "rawTitle": raw_title,
        "title": title_clean,
        "jenis": jenis,
        "programUrl": program_url,
        "myLearningUrl": my_learning_url,
        "directUrl": direct_url,
        "linkMatchType": link_match_type,
        "activityId": matched_aid,
        "exactVerified": (link_match_type == "exact_activity"),
        "date": iso_date,
        **meta
    })

# Sort strictly chronologically by (date, island order, activityNumber)
ISLAND_ORDER = {"daring": 1, "english": 2, "living_english": 3, "pjok": 4, "homeroom": 5}
all_quests.sort(key=lambda q: (q["date"], ISLAND_ORDER.get(q["islandId"], 9), q["activityNumber"]))

kid_quests = [q for q in all_quests if q["kidActionable"]]

for global_idx, q in enumerate(kid_quests, start=1):
    q["chronologicalLevel"] = global_idx

island_counters = {}
for q in kid_quests:
    iid = q["islandId"]
    island_counters[iid] = island_counters.get(iid, 0) + 1
    q["islandLevel"] = island_counters[iid]

belum_selesai_count = sum(1 for q in kid_quests if q["timelineStatus"] == "belum_selesai")
belum_berjalan_count = sum(1 for q in kid_quests if q["timelineStatus"] == "belum_berjalan")
belum_berjalan_portal_count = sum(1 for q in kid_quests if q["portalUnlockStatus"] == "in_portal_nov_dec")
belum_berjalan_schedule_count = sum(1 for q in kid_quests if q["portalUnlockStatus"] == "upcoming_sem1_schedule")

output_payload = {
    "generatedAt": datetime.now().isoformat(),
    "portalCompletedExcludedCount": 240,  # 191 SMM + 49 Living English already TRUE on sekolah.mu
    "portalUncheckedNonKidExcludedCount": len(all_quests) - len(kid_quests),
    "totalQuests": len(kid_quests),
    "kidActionableCount": len(kid_quests),
    "bossQuestCount": sum(1 for q in kid_quests if q["category"] == "boss_quest"),
    "belumSelesaiCount": belum_selesai_count,
    "belumBerjalanCount": belum_berjalan_count,
    "belumBerjalanPortalCount": belum_berjalan_portal_count,
    "belumBerjalanScheduleCount": belum_berjalan_schedule_count,
    "islands": ISLAND_META,
    "quests": kid_quests
}

with open("/Users/sharonxu/gabriel-quest-map/quests_data.js", "w", encoding="utf-8") as f:
    f.write("window.GABRIEL_QUEST_DATA = ")
    json.dump(output_payload, f, ensure_ascii=False, indent=2)
    f.write(";\n")

with open("/Users/sharonxu/gabriel-quest-map/gabriel_quests_with_deeplinks.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Level Kronologis", "Pulau", "Status Periode", "Tab Sumber", "Program / Mapel", "Bagian / Modul",
        "No Aktivitas", "Judul Aktivitas", "Jenis", "Kategori Quest", "Tanggal Estimasi",
        "Link Ruang Kelas Materi (/c)", "Link Halaman Program (/program/slug)"
    ])
    for q in kid_quests:
        writer.writerow([
            q["chronologicalLevel"], q["islandName"], q["timelineBadge"], q["sourceTab"], q["program"], q["module"],
            q["activityNumber"], q["rawTitle"], q["jenis"], q["badge"], q["date"],
            q["directUrl"], q["programUrl"]
        ])

print(f"Successfully generated {len(kid_quests)} total quests (excluded 240 portal-completed items)!")
print(f" - Belum Selesai (Jul-Okt Overdue in Portal): {belum_selesai_count}")
print(f" - Belum Berjalan (Nov - Akhir Sem 1): {belum_berjalan_count} ({belum_berjalan_portal_count} sudah di portal + {belum_berjalan_schedule_count} jadwal Minggu 6-11 Akhir Sem 1)")
print(f" - Boss Quests (Tugas & Asesmen): {output_payload['bossQuestCount']}")
for iid, meta in ISLAND_META.items():
    iq = [q for q in kid_quests if q["islandId"] == iid]
    iq_ov = sum(1 for q in iq if q["timelineStatus"] == "belum_selesai")
    iq_up = sum(1 for q in iq if q["timelineStatus"] == "belum_berjalan")
    print(f"   * {meta['name']} ({iid}): {len(iq)} total ({iq_ov} Jul-Okt + {iq_up} Nov-Akhir Sem 1)")
