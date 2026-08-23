import json
import pathlib

root = pathlib.Path(r'C:/Users/pc/cyber-rag/languages')

common_categories = {
    "account_compromise": ["hacked", "hack", "unauthorized access", "sim swap", "compromised"],
    "financial_fraud": ["scam", "fraud", "money", "bank", "account", "otp", "pin", "card", "debit card", "credit card", "atm", "transaction", "mobile money", "wire transfer", "gift card", "loan scam", "investment scam", "crypto scam", "romance scam", "fake lottery", "employment scam", "parcel scam", "giveaway"],
    "malware_technical": ["virus", "malware", "computer", "internet", "data", "security", "ransomware", "trojan", "worm", "spyware", "keylogger", "botnet", "ddos", "vpn", "firewall", "backup", "restore", "recovery"],
    "phishing_social_engineering": ["password", "link", "click", "email", "website", "phishing", "social engineering", "authentication", "verification code", "2fa", "mfa", "urgent", "verify now", "claim prize", "account suspended"],
    "actions": ["steal", "attack", "warn", "report", "change", "contact", "monitor", "scan", "update", "open", "close", "recover"],
    "people_institutions": ["thief", "fraudster", "police", "criminal"],
    "devices": ["phone", "computer", "sim card", "laptop", "router", "wifi", "usb"],
    "authentication": ["password", "otp", "2fa", "mfa", "verification code"],
    "banking": ["bank", "mobile money", "airtime", "bank transfer", "debit card", "credit card", "atm", "transaction", "account number", "payment", "merchant", "ussd"],
    "mobile_security": ["android", "iphone", "apk", "play store", "app store", "sms", "call", "contact list", "camera", "microphone"],
    "network_security": ["vpn", "firewall", "dns", "domain", "ssl", "tls", "router", "wifi"],
    "incident_response": ["breach", "incident", "compromised", "infected", "encrypted", "locked", "backup", "restore", "recovery", "monitor", "containment", "eradication"],
    "social_media": ["telegram", "whatsapp", "facebook", "instagram", "gmail"]
}

language_updates = {
    "english": {
        "translations": {
            "verification code": {"english": "verification code", "confidence": "verified"},
            "OTP": {"english": "otp", "confidence": "verified"},
            "sim swap": {"english": "sim swap", "confidence": "verified"},
            "bank account": {"english": "bank account", "confidence": "verified"},
            "credit card": {"english": "credit card", "confidence": "verified"},
            "debit card": {"english": "debit card", "confidence": "verified"},
            "ussd": {"english": "ussd", "confidence": "verified"},
            "phone number": {"english": "phone number", "confidence": "verified"},
            "transaction": {"english": "transaction", "confidence": "verified"},
            "payment": {"english": "payment", "confidence": "verified"}
        },
        "phrases": {
            "they asked for my verification code": {"english": "they asked for my verification code", "confidence": "verified"},
            "they asked for my otp": {"english": "they asked for my otp", "confidence": "common"},
            "they asked for my password": {"english": "they asked for my password", "confidence": "verified"},
            "my account was hacked": {"english": "my account was hacked", "confidence": "verified"},
            "my phone was stolen": {"english": "my phone was stolen", "confidence": "verified"},
            "i received a fake message": {"english": "i received a fake message", "confidence": "verified"},
            "my sim card was swapped": {"english": "my sim card was swapped", "confidence": "common"},
            "my bank account was compromised": {"english": "my bank account was compromised", "confidence": "common"}
        }
    },
    "arabic": {
        "translations": {
            "رمز التحقق": {"english": "verification code", "confidence": "verified"},
            "رمز التأكيد": {"english": "verification code", "confidence": "verified"},
            "طلبوا رمز التحقق مني": {"english": "they asked for my verification code", "confidence": "common"},
            "تلقيت رسالة احتيالية": {"english": "i received a fake message", "confidence": "common"},
            "تم اختراق حسابي": {"english": "my account was hacked", "confidence": "verified"},
            "تم سرقة هاتفي": {"english": "my phone was stolen", "confidence": "common"},
            "تم تبديل شريحتي": {"english": "my SIM card was swapped", "confidence": "common"},
            "بطاقة SIM": {"english": "sim card", "confidence": "verified"},
            "رمز USSD": {"english": "ussd code", "confidence": "common"},
            "حساب بنكي": {"english": "bank account", "confidence": "verified"},
            "تحويل مالي": {"english": "bank transfer", "confidence": "common"},
            "رقم الهاتف": {"english": "phone number", "confidence": "verified"}
        },
        "phrases": {
            "طلبوا رمز التحقق مني": {"english": "they asked for my verification code", "confidence": "common"},
            "طلبوا كلمة المرور الخاصة بي": {"english": "they asked for my password", "confidence": "common"},
            "تم اختراق حسابي": {"english": "my account was hacked", "confidence": "verified"},
            "تلقيت رسالة احتيالية": {"english": "i received a fake message", "confidence": "common"},
            "تم سرقة هاتفي": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "french": {
        "translations": {
            "code de vérification": {"english": "verification code", "confidence": "verified"},
            "mot de passe": {"english": "password", "confidence": "verified"},
            "carte SIM": {"english": "sim card", "confidence": "verified"},
            "code USSD": {"english": "ussd code", "confidence": "common"},
            "compte bancaire": {"english": "bank account", "confidence": "verified"},
            "virement bancaire": {"english": "bank transfer", "confidence": "common"},
            "numéro de téléphone": {"english": "phone number", "confidence": "verified"},
            "transaction non autorisée": {"english": "unauthorized transaction", "confidence": "common"},
            "message frauduleux": {"english": "fake message", "confidence": "verified"}
        },
        "phrases": {
            "ils ont demandé mon code de vérification": {"english": "they asked for my verification code", "confidence": "common"},
            "ils ont demandé mon mot de passe": {"english": "they asked for my password", "confidence": "common"},
            "mon compte a été piraté": {"english": "my account was hacked", "confidence": "verified"},
            "j'ai reçu un message frauduleux": {"english": "i received a fake message", "confidence": "verified"},
            "ma carte SIM a été changée": {"english": "my SIM card was swapped", "confidence": "common"}
        }
    },
    "swahili": {
        "translations": {
            "nambari ya kuthibitisha": {"english": "verification code", "confidence": "verified"},
            "kadi ya benki": {"english": "bank card", "confidence": "verified"},
            "kadi ya malipo": {"english": "debit card", "confidence": "verified"},
            "nambari ya USSD": {"english": "ussd code", "confidence": "verified"},
            "simu ya SIM": {"english": "sim card", "confidence": "verified"},
            "ushiriki": {"english": "phishing", "confidence": "common"},
            "ulaghai": {"english": "fraud", "confidence": "verified"}
        },
        "phrases": {
            "waliomba nambari yangu ya uthibitisho": {"english": "they asked for my verification code", "confidence": "verified"},
            "waliomba OTP yangu": {"english": "they asked for my otp", "confidence": "common"},
            "waliomba nenosiri langu": {"english": "they asked for my password", "confidence": "common"},
            "akaunti yangu ilidukuliwa": {"english": "my account was compromised", "confidence": "verified"},
            "nilipokea ujumbe wa ulaghai": {"english": "i received a fake message", "confidence": "verified"},
            "simu yangu iliibwa": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "yoruba": {
        "translations": {
            "koodu ìdánwò": {"english": "verification code", "confidence": "verified"},
            "koodu ìfọwọ́sì": {"english": "confirmation code", "confidence": "verified"},
            "kàdì SIM": {"english": "sim card", "confidence": "verified"},
            "nọ́mbà USSD": {"english": "ussd code", "confidence": "common"},
            "iṣowo banki": {"english": "bank transaction", "confidence": "common"},
            "ìsanwó": {"english": "payment", "confidence": "verified"}
        },
        "phrases": {
            "wọ́n bẹ̀rẹ̀ koodu ìdánwò mi": {"english": "they asked for my verification code", "confidence": "common"},
            "wọ́n bẹ̀rẹ̀ OTP mi": {"english": "they asked for my otp", "confidence": "common"},
            "akọ́ọ̀lẹ́ mi ti jẹ́ pirated": {"english": "my account was hacked", "confidence": "common"},
            "mo gba ifiranṣẹ iro": {"english": "i received a fake message", "confidence": "verified"},
            "kaadi SIM mi ti yí padà": {"english": "my SIM card was swapped", "confidence": "common"}
        }
    },
    "igbo": {
        "translations": {
            "koodu nkwenye": {"english": "verification code", "confidence": "verified"},
            "kadi SIM": {"english": "sim card", "confidence": "verified"},
            "nọmba USSD": {"english": "ussd code", "confidence": "common"},
            "ụgwọ": {"english": "payment", "confidence": "verified"},
            "ntinye PIN": {"english": "pin entry", "confidence": "common"}
        },
        "phrases": {
            "ha jụrụ m koodu nkwenye m": {"english": "they asked for my verification code", "confidence": "common"},
            "ha jụrụ m OTP m": {"english": "they asked for my otp", "confidence": "common"},
            "akaụntụ m emezughị": {"english": "my account was compromised", "confidence": "common"},
            "enwetara m ozi aghụghọ": {"english": "i received a fake message", "confidence": "verified"},
            "a kpọrọ ekwentị m": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "xhosa": {
        "translations": {
            "ikhodi yokuqinisekisa": {"english": "verification code", "confidence": "verified"},
            "ikhadi le-SIM": {"english": "sim card", "confidence": "verified"},
            "inombolo ye-USSD": {"english": "ussd code", "confidence": "common"},
            "inkokeli yokhuseleko": {"english": "security warning", "confidence": "common"}
        },
        "phrases": {
            "bacele ikhodi yam yokuqinisekisa": {"english": "they asked for my verification code", "confidence": "common"},
            "bacele i-OTP yam": {"english": "they asked for my otp", "confidence": "common"},
            "akhawunti yam yaphulwe": {"english": "my account was hacked", "confidence": "common"},
            "ndamkela umyalezo wobuxoki": {"english": "i received a fake message", "confidence": "verified"},
            "ifowuni yam yebiwe": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "zulu": {
        "translations": {
            "ikhodi yokuqinisekisa": {"english": "verification code", "confidence": "verified"},
            "ikhadi le-SIM": {"english": "sim card", "confidence": "verified"},
            "inombolo ye-USSD": {"english": "ussd code", "confidence": "common"},
            "ukudluliselwa kwemali": {"english": "bank transfer", "confidence": "common"}
        },
        "phrases": {
            "bacela ikhodi yami yokuqinisekisa": {"english": "they asked for my verification code", "confidence": "common"},
            "bacela i-OTP yami": {"english": "they asked for my otp", "confidence": "common"},
            "i-akhawunti yami yephulwe": {"english": "my account was hacked", "confidence": "common"},
            "ngithole umyalezo wokukhohlisa": {"english": "i received a fake message", "confidence": "verified"},
            "ifoni yami yebiwe": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "oromo": {
        "translations": {
            "koodii mirkaneessaa": {"english": "verification code", "confidence": "verified"},
            "kaardii SIM": {"english": "sim card", "confidence": "common"},
            "lakk. USSD": {"english": "ussd code", "confidence": "common"},
            "herrega kiyya": {"english": "my account", "confidence": "common"},
            "bilbilli koo": {"english": "my phone", "confidence": "verified"}
        },
        "phrases": {
            "isinni koo ragaa na gaafate": {"english": "they asked for my verification code", "confidence": "common"},
            "OTP koo na gaafate": {"english": "they asked for my otp", "confidence": "common"},
            "jecha iccitii koo na gaafate": {"english": "they asked for my secret code", "confidence": "common"},
            "herrega kiyya hatame": {"english": "my account was compromised", "confidence": "common"},
            "bilbilli koo hatame": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "amharic": {
        "translations": {
            "ማረጋገጫ ኮድ": {"english": "verification code", "confidence": "verified"},
            "የOTP ኮድ": {"english": "otp code", "confidence": "verified"},
            "ካርድ ሲም": {"english": "sim card", "confidence": "verified"},
            "የUSSD ኮድ": {"english": "ussd code", "confidence": "common"},
            "የባንክ ካርድ": {"english": "bank card", "confidence": "common"},
            "የገንዘብ ስርዓት": {"english": "payment system", "confidence": "common"}
        },
        "phrases": {
            "ለእኔ የማረጋገጫ ኮድ ጠየቁ": {"english": "they asked for my verification code", "confidence": "common"},
            "ኦቲፒዬን ጠየቁ": {"english": "they asked for my otp", "confidence": "common"},
            "የይለፍ ቃሌን ጠየቁ": {"english": "they asked for my password", "confidence": "common"},
            "መለያዬ ተሳምቷል": {"english": "my account was compromised", "confidence": "verified"},
            "ስልኬ ታረፈ": {"english": "my phone was stolen", "confidence": "common"}
        }
    },
    "fulfulde": {
        "translations": {
            "koodii njiyam": {"english": "verification code", "confidence": "uncertain"},
            "SIM": {"english": "sim card", "confidence": "common"},
            "OTP": {"english": "otp", "confidence": "common"},
            "banki": {"english": "bank", "confidence": "common"},
            "ceede": {"english": "money", "confidence": "verified"}
        },
        "phrases": {
            "ɓe njiyaa koodii ngam noddii am": {"english": "they asked for my verification code", "confidence": "uncertain"},
            "OTP am njiyaa": {"english": "they asked for my otp", "confidence": "uncertain"},
            "muɗɗo jogii tefŋal am": {"english": "my account was compromised", "confidence": "uncertain"}
        }
    },
    "kanuri": {
        "translations": {
            "koodi tsarka": {"english": "verification code", "confidence": "common"},
            "SIM": {"english": "sim card", "confidence": "common"},
            "OTP": {"english": "otp", "confidence": "common"},
            "bank": {"english": "bank", "confidence": "common"},
            "email": {"english": "email", "confidence": "common"}
        },
        "phrases": {
            "ɓe nayi koodi tsarka": {"english": "they asked for my verification code", "confidence": "common"},
            "sim am ɓe ɗakile": {"english": "my sim card was swapped", "confidence": "common"}
        }
    }
}

for path in sorted(root.glob('*.json')):
    if path.name == 'hausa.json':
        continue

    data = json.loads(path.read_text(encoding='utf-8'))

    if isinstance(data.get('_metadata'), dict):
        data['_metadata']['version'] = '2.1.0'

    if isinstance(data.get('categories'), dict):
        for cat, items in common_categories.items():
            existing = data['categories'].get(cat, [])
            if not isinstance(existing, list):
                continue
            merged = existing + [item for item in items if item not in existing]
            data['categories'][cat] = merged

    if 'translations' not in data or not isinstance(data['translations'], dict):
        data['translations'] = {}
    if 'phrases' not in data or not isinstance(data['phrases'], dict):
        data['phrases'] = {}

    lang_key = path.stem
    updates = language_updates.get(lang_key, {})
    translations = updates.get('translations', {})
    phrases = updates.get('phrases', {})

    for key, record in translations.items():
        if key not in data['translations']:
            data['translations'][key] = record

    for key, record in phrases.items():
        if key not in data['phrases']:
            data['phrases'][key] = record

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated {path.name}: {len(data["translations"])} translations, {len(data["phrases"])} phrases')
