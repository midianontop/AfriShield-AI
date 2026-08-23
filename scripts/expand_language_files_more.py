import json
import pathlib

root = pathlib.Path(r'C:/Users/pc/cyber-rag/languages')

updates = {
    'english': {
        'translations': {
            'password reset': {'english': 'password reset', 'confidence': 'verified'},
            'account suspended': {'english': 'account suspended', 'confidence': 'verified'},
            'verification code': {'english': 'verification code', 'confidence': 'verified'},
            'two-factor authentication': {'english': 'two-factor authentication', 'confidence': 'verified'},
            'one-time password': {'english': 'otp', 'confidence': 'verified'},
            'banking app': {'english': 'banking app', 'confidence': 'verified'},
            'mobile wallet': {'english': 'mobile wallet', 'confidence': 'verified'},
            'customer support': {'english': 'customer support', 'confidence': 'verified'},
            'fake link': {'english': 'fake link', 'confidence': 'verified'},
            'fraud alert': {'english': 'fraud alert', 'confidence': 'verified'},
        },
        'phrases': {
            'they asked for my verification code': {'english': 'they asked for my verification code', 'confidence': 'verified'},
            'they asked for my otp': {'english': 'they asked for my otp', 'confidence': 'common'},
            'they asked for my password': {'english': 'they asked for my password', 'confidence': 'verified'},
            'they asked for my bvn': {'english': 'they asked for my bvn', 'confidence': 'common'},
            'they asked for my account number': {'english': 'they asked for my account number', 'confidence': 'common'},
            'they asked me to install this app': {'english': 'they asked me to install this app', 'confidence': 'common'},
            'my sim card was swapped': {'english': 'my sim card was swapped', 'confidence': 'common'},
            'my bank app was hacked': {'english': 'my bank app was hacked', 'confidence': 'common'},
            'i received a phishing message from bank': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'i was told to reset my password immediately': {'english': 'i was told to reset my password immediately', 'confidence': 'common'},
        },
    },
    'arabic': {
        'translations': {
            'إعادة تعيين كلمة المرور': {'english': 'password reset', 'confidence': 'verified'},
            'الحساب معلق': {'english': 'account suspended', 'confidence': 'verified'},
            'خدمة العملاء': {'english': 'customer support', 'confidence': 'verified'},
            'تنبيه احتيال': {'english': 'fraud alert', 'confidence': 'verified'},
            'رابط زائف': {'english': 'fake link', 'confidence': 'verified'},
            'تطبيق بنكي': {'english': 'banking app', 'confidence': 'common'},
            'محفظة إلكترونية': {'english': 'mobile wallet', 'confidence': 'common'},
            'رمز مرور لمرة واحدة': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'طلبوا رمز التحقق مني': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'طلبوا كلمة المرور الخاصة بي': {'english': 'they asked for my password', 'confidence': 'common'},
            'قالوا لي أن أُعيد ضبط كلمة المرور فوراً': {'english': 'i was told to reset my password immediately', 'confidence': 'common'},
            'تلقيت رابطًا زائفًا': {'english': 'i received a fake link', 'confidence': 'common'},
            'تلقيت رسالة احتيال من البنك': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'تم تبديل شريحتي': {'english': 'my SIM card was swapped', 'confidence': 'common'},
        },
    },
    'french': {
        'translations': {
            'réinitialisation du mot de passe': {'english': 'password reset', 'confidence': 'verified'},
            'compte suspendu': {'english': 'account suspended', 'confidence': 'verified'},
            'support client': {'english': 'customer support', 'confidence': 'verified'},
            'alerte fraude': {'english': 'fraud alert', 'confidence': 'verified'},
            'lien frauduleux': {'english': 'fake link', 'confidence': 'verified'},
            'portefeuille mobile': {'english': 'mobile wallet', 'confidence': 'common'},
            'application bancaire': {'english': 'banking app', 'confidence': 'common'},
            'mot de passe à usage unique': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'ils ont demandé mon code de vérification': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'ils ont demandé mon mot de passe': {'english': 'they asked for my password', 'confidence': 'common'},
            'j ai reçu un lien frauduleux': {'english': 'i received a fake link', 'confidence': 'common'},
            'j ai reçu un message de phishing de la banque': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'ma carte SIM a été changée': {'english': 'my SIM card was swapped', 'confidence': 'common'},
        },
    },
    'swahili': {
        'translations': {
            'kuwekwa upya nenosiri': {'english': 'password reset', 'confidence': 'verified'},
            'akaunti imezimwa': {'english': 'account suspended', 'confidence': 'verified'},
            'huduma kwa wateja': {'english': 'customer support', 'confidence': 'verified'},
            'anguko la ulaghai': {'english': 'fraud alert', 'confidence': 'common'},
            'kiungo bandia': {'english': 'fake link', 'confidence': 'common'},
            'app ya benki': {'english': 'banking app', 'confidence': 'common'},
            'mfuko wa simu': {'english': 'mobile wallet', 'confidence': 'common'},
            'nenosiri la matumizi mara moja': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'waliomba nambari yangu ya uthibitisho': {'english': 'they asked for my verification code', 'confidence': 'verified'},
            'waliomba nenosiri langu': {'english': 'they asked for my password', 'confidence': 'common'},
            'nilipokea kiungo bandia': {'english': 'i received a fake link', 'confidence': 'common'},
            'nilipokea barua pepe ya ulaghai kutoka benki': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'simu yangu iliibwa': {'english': 'my phone was stolen', 'confidence': 'common'},
        },
    },
    'yoruba': {
        'translations': {
            'tunse ọrọigbaniwọle': {'english': 'password reset', 'confidence': 'verified'},
            'iṣiro ti dina': {'english': 'account suspended', 'confidence': 'common'},
            'iṣẹ alabara': {'english': 'customer support', 'confidence': 'verified'},
            'ìkìlọ̀ ete jìbìtì': {'english': 'fraud alert', 'confidence': 'common'},
            'ọ̀nà asopọ èké': {'english': 'fake link', 'confidence': 'common'},
            'ẹ̀rọ ìfowópamọ́ alágbèéká': {'english': 'mobile wallet', 'confidence': 'common'},
            'app banki': {'english': 'banking app', 'confidence': 'common'},
            'koodu ìkanṣoṣo': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'wọ́n bẹ̀rẹ̀ koodu ìdánwò mi': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'wọ́n bẹ̀rẹ̀ paswọ́ọ̀dù mi': {'english': 'they asked for my password', 'confidence': 'common'},
            'mo gba ọna asopọ èké': {'english': 'i received a fake link', 'confidence': 'common'},
            'mo gba imeeli èké lati ọdọ banki': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'kaadi SIM mi ti yí padà': {'english': 'my SIM card was swapped', 'confidence': 'common'},
        },
    },
    'igbo': {
        'translations': {
            'túgharia paswọọdụ': {'english': 'password reset', 'confidence': 'verified'},
            'akụkọ a kwụsịrị': {'english': 'account suspended', 'confidence': 'common'},
            'dịkwa onye ahịa': {'english': 'customer support', 'confidence': 'verified'},
            'ndụmọdụ aghụghọ': {'english': 'fraud alert', 'confidence': 'common'},
            'njikọ ụgha': {'english': 'fake link', 'confidence': 'common'},
            'ngwugwu ekwentị': {'english': 'mobile wallet', 'confidence': 'common'},
            'ngwanrọ ụlọ akụ': {'english': 'banking app', 'confidence': 'common'},
        },
        'phrases': {
            'ha jụrụ m paswọọdụ m': {'english': 'they asked for my password', 'confidence': 'common'},
            'ha jụrụ m OTP m': {'english': 'they asked for my otp', 'confidence': 'common'},
            'enwetara m njikọ ụgha': {'english': 'i received a fake link', 'confidence': 'common'},
            'enwetara m ozi aghụghọ sitere na banki': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'a kpọrọ ekwentị m': {'english': 'my phone was stolen', 'confidence': 'common'},
        },
    },
    'xhosa': {
        'translations': {
            'ukumiselwa kwigama lokugqithisa': {'english': 'password reset', 'confidence': 'verified'},
            'akhawunti evaliweyo': {'english': 'account suspended', 'confidence': 'common'},
            'inkxaso yabathengi': {'english': 'customer support', 'confidence': 'verified'},
            'iliso lokukhohlisa': {'english': 'fraud alert', 'confidence': 'common'},
            'ikhonkco elingelilo': {'english': 'fake link', 'confidence': 'common'},
            'isicelo sebhanki': {'english': 'banking app', 'confidence': 'common'},
            'isisele esinye ixesha': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'bacele ikhodi yam yokuqinisekisa': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'bacele iphasiwedi yam': {'english': 'they asked for my password', 'confidence': 'common'},
            'ndamkela ikhonkco elingelilo': {'english': 'i received a fake link', 'confidence': 'common'},
            'ndamkela umyalezo wokukhohlisa ovela kwibhanki': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'ifowuni yam yebiwe': {'english': 'my phone was stolen', 'confidence': 'common'},
        },
    },
    'zulu': {
        'translations': {
            'ukusetha kabusha iphasiwedi': {'english': 'password reset', 'confidence': 'verified'},
            'i-akhawunti ivinjiwe': {'english': 'account suspended', 'confidence': 'common'},
            'ukwesekwa kwamakhasimende': {'english': 'customer support', 'confidence': 'verified'},
            'isaziso sobuqili': {'english': 'fraud alert', 'confidence': 'common'},
            'isixhumanisi sebuqili': {'english': 'fake link', 'confidence': 'common'},
            'uhlelo lokusebenza lwebhange': {'english': 'banking app', 'confidence': 'common'},
            'i-OTP': {'english': 'otp', 'confidence': 'verified'},
        },
        'phrases': {
            'bacela ikhodi yami yokuqinisekisa': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'bacela iphasiwedi yami': {'english': 'they asked for my password', 'confidence': 'common'},
            'ngithole isixhumanisi sebuqili': {'english': 'i received a fake link', 'confidence': 'common'},
            'ngithole i-imeyili yephishing evela ebhange': {'english': 'i received a phishing message from bank', 'confidence': 'common'},
            'ifoni yami yebiwe': {'english': 'my phone was stolen', 'confidence': 'common'},
        },
    },
    'oromo': {
        'translations': {
            'gaaffii jecha iccitii': {'english': 'password reset', 'confidence': 'common'},
            'herrega dhaabbate': {'english': 'account suspended', 'confidence': 'common'},
            'deeggarsa maamilaa': {'english': 'customer support', 'confidence': 'common'},
            'akeekkachiisa sobaa': {'english': 'fraud alert', 'confidence': 'common'},
            'linkii sobaa': {'english': 'fake link', 'confidence': 'common'}
        },
        'phrases': {
            'isinni koo ragaa na gaafate': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'OTP koo na gaafate': {'english': 'they asked for my otp', 'confidence': 'common'},
            'jecha iccitii koo na gaafate': {'english': 'they asked for my secret code', 'confidence': 'common'},
            'ergaa sobaa argadhe': {'english': 'i received a fake message', 'confidence': 'common'},
            'bilbilli koo hatame': {'english': 'my phone was stolen', 'confidence': 'common'},
        },
    },
    'amharic': {
        'translations': {
            'የፓስዎርድ መቀየሪያ': {'english': 'password reset', 'confidence': 'verified'},
            'አካውንት ተዘግቷል': {'english': 'account suspended', 'confidence': 'common'},
            'የደንበኛ ድጋፍ': {'english': 'customer support', 'confidence': 'verified'},
            'ማንኛውም የትክክለኛነት ማስጠንቀቂያ': {'english': 'fraud alert', 'confidence': 'common'},
            'የሐሰት አገናኝ': {'english': 'fake link', 'confidence': 'common'}
        },
        'phrases': {
            'ለእኔ የማረጋገጫ ኮድ ጠየቁ': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'OTP ያስፈልጋቸው': {'english': 'they asked for my otp', 'confidence': 'common'},
            'ፓስዎርድ ጠየቁ': {'english': 'they asked for my password', 'confidence': 'common'},
            'ስልኬ ታረፈ': {'english': 'my phone was stolen', 'confidence': 'common'},
            'መልእክት ሐሰት ተቀብልኩ': {'english': 'i received a fake message', 'confidence': 'common'},
        },
    },
    'fulfulde': {
        'translations': {
            'koodii njiyam': {'english': 'verification code', 'confidence': 'uncertain'},
            'koodii USSD': {'english': 'ussd code', 'confidence': 'uncertain'},
            'ceede': {'english': 'money', 'confidence': 'verified'},
            'banki': {'english': 'bank', 'confidence': 'common'},
            'sim': {'english': 'sim card', 'confidence': 'common'},
            'OTP': {'english': 'otp', 'confidence': 'common'},
            'paswod': {'english': 'password', 'confidence': 'common'},
        },
        'phrases': {
            'ɓe njiyaa koodii ngam noddii am': {'english': 'they asked for my verification code', 'confidence': 'uncertain'},
            'ɓe njiyaa paswod am': {'english': 'they asked for my password', 'confidence': 'uncertain'},
            'ɓe njiyaa OTP am': {'english': 'they asked for my otp', 'confidence': 'uncertain'},
            'bilal am wujjii': {'english': 'my account was compromised', 'confidence': 'uncertain'},
            'bilal am ɓooyay': {'english': 'my phone was stolen', 'confidence': 'uncertain'},
        },
    },
    'kanuri': {
        'translations': {
            'koodi tsarka': {'english': 'verification code', 'confidence': 'common'},
            'koodi USSD': {'english': 'ussd code', 'confidence': 'common'},
            'sim': {'english': 'sim card', 'confidence': 'common'},
            'OTP': {'english': 'otp', 'confidence': 'common'},
            'banki': {'english': 'bank', 'confidence': 'common'},
            'email': {'english': 'email', 'confidence': 'common'},
        },
        'phrases': {
            'ɓe nayi koodi tsarka': {'english': 'they asked for my verification code', 'confidence': 'common'},
            'ɓe nayi OTP am': {'english': 'they asked for my otp', 'confidence': 'common'},
            'sim am ɓe ɗakile': {'english': 'my sim card was swapped', 'confidence': 'common'},
            'akunti am ɓe wakkile': {'english': 'my account was compromised', 'confidence': 'common'},
        },
    },
}

for path in sorted(root.glob('*.json')):
    if path.name == 'hausa.json':
        continue

    data = json.loads(path.read_text(encoding='utf-8'))
    if isinstance(data.get('_metadata'), dict):
        data['_metadata']['version'] = '2.1.0'
    if 'categories' in data and isinstance(data['categories'], dict):
        for cat, items in updates.get('common_categories', {}).items():
            existing = data['categories'].get(cat, [])
            if isinstance(existing, list):
                data['categories'][cat] = existing + [item for item in items if item not in existing]
    if 'translations' not in data or not isinstance(data['translations'], dict):
        data['translations'] = {}
    if 'phrases' not in data or not isinstance(data['phrases'], dict):
        data['phrases'] = {}
    lang_key = path.stem
    lang_updates = updates.get(lang_key, {})
    for key, record in lang_updates.get('translations', {}).items():
        if key not in data['translations']:
            data['translations'][key] = record
    for key, record in lang_updates.get('phrases', {}).items():
        if key not in data['phrases']:
            data['phrases'][key] = record
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Updated {path.name}: translations={len(data["translations"])}, phrases={len(data["phrases"])})')
