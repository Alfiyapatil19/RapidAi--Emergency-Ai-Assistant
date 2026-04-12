"""
RapidAid - First Aid Data Routes
Serves multilingual first aid instructions as JSON.
No login required.
"""

from flask import Blueprint, jsonify, session
from database.db import get_db

firstaid_bp = Blueprint("firstaid", __name__)

# ─── FIRST AID CONTENT DATABASE ───────────────────────────────────────────────
FIRST_AID = {
    "en": {
        "burns": {
            "title": "Burns First Aid",
            "warning": "Seek medical help immediately for large, deep, or facial burns.",
            "steps": [
                {"title": "Cool the burn", "detail": "Hold the burned area under cool (not cold) running water for at least 10–20 minutes."},
                {"title": "Remove constrictions", "detail": "Carefully remove rings, watches, or clothing near the burn before swelling starts."},
                {"title": "Do NOT use ice or butter", "detail": "Never apply ice, butter, or toothpaste — these can worsen tissue damage."},
                {"title": "Cover the burn", "detail": "Cover loosely with a sterile, non-fluffy dressing or cling film."},
                {"title": "Manage pain", "detail": "Take paracetamol or ibuprofen if needed for pain relief."},
                {"title": "Call for help if severe", "detail": "Call 108 for burns larger than a palm, or on face, hands, feet, or genitals."},
            ],
        },
        "bleeding": {
            "title": "Bleeding First Aid",
            "warning": "If bleeding does not stop within 10 minutes, call 108 immediately.",
            "steps": [
                {"title": "Apply direct pressure", "detail": "Press firmly on the wound with a clean cloth, bandage, or your hand."},
                {"title": "Maintain pressure", "detail": "Keep pressing for at least 10 minutes without lifting. Do not remove the cloth."},
                {"title": "Elevate the injured area", "detail": "Raise the injured body part above heart level to slow blood flow."},
                {"title": "Secure the dressing", "detail": "Once bleeding slows, secure the cloth with a bandage or tape."},
                {"title": "Watch for shock", "detail": "If the person becomes pale, cold, or confused — lay them flat and elevate legs."},
                {"title": "Seek medical help", "detail": "Deep, wide, or non-stopping wounds require professional medical care."},
            ],
        },
        "fracture": {
            "title": "Fracture First Aid",
            "warning": "Do not attempt to realign the bone. Immobilize and get professional help.",
            "steps": [
                {"title": "Stop any bleeding", "detail": "If the fracture is open (bone visible), apply gentle pressure around the wound."},
                {"title": "Immobilize the injury", "detail": "Splint the injured area using padding and a rigid support. Do NOT move it."},
                {"title": "Apply ice pack", "detail": "Wrap ice in cloth and apply to reduce swelling. Never apply ice directly to skin."},
                {"title": "Treat for shock", "detail": "If patient feels faint or looks pale, keep them warm and calm."},
                {"title": "Do not give food/water", "detail": "The patient may need surgery — avoid giving anything by mouth."},
                {"title": "Call for transport", "detail": "Call 108 for spine, hip, or pelvis fractures. Do not move the patient."},
            ],
        },
        "choking": {
            "title": "Choking First Aid",
            "warning": "If the person becomes unconscious, start CPR and call 108 immediately.",
            "steps": [
                {"title": "Assess the situation", "detail": "Ask 'Are you choking?' If they can speak or cough, encourage forceful coughing."},
                {"title": "Give back blows", "detail": "Lean person forward. Give 5 firm blows between shoulder blades with heel of hand."},
                {"title": "Perform abdominal thrusts", "detail": "Stand behind, make a fist above navel, cover with other hand. Pull sharply inward and upward x5."},
                {"title": "Alternate blows & thrusts", "detail": "Repeat 5 back blows + 5 abdominal thrusts until object is expelled or help arrives."},
                {"title": "For infants (under 1 year)", "detail": "Use 5 back blows + 5 chest thrusts (NOT abdominal). Support head carefully."},
                {"title": "Call emergency services", "detail": "Call 108 if choking continues. Start CPR if person becomes unconscious."},
            ],
        },
        "heart": {
            "title": "Heart Attack First Aid",
            "warning": "Call 108 immediately. Every second counts during a heart attack.",
            "steps": [
                {"title": "Call emergency services", "detail": "Call 108 immediately — do not drive yourself. State 'possible heart attack'."},
                {"title": "Make person comfortable", "detail": "Help them sit or lie comfortably. Loosen tight clothing around neck and chest."},
                {"title": "Aspirin if available", "detail": "Give 325mg aspirin (chewed) if not allergic and the person is conscious."},
                {"title": "Monitor breathing", "detail": "Stay with the person. If they stop breathing, prepare to start CPR."},
                {"title": "Perform CPR if needed", "detail": "If no pulse: 30 chest compressions (hard/fast) + 2 rescue breaths. Repeat."},
                {"title": "Use AED if available", "detail": "Automated defibrillators are in many public places. Turn on and follow prompts."},
            ],
        },
        "drowning": {
            "title": "Drowning First Aid",
            "warning": "Call 108 immediately. Drowning can occur silently with little splashing.",
            "steps": [
                {"title": "Ensure safety first", "detail": "Do not jump in unless trained. Throw a rope, life ring, or extend a long object."},
                {"title": "Get person to safety", "detail": "Bring them to land or a boat. Support their head and neck at all times."},
                {"title": "Call 108", "detail": "Call emergency services immediately, even if the person seems okay."},
                {"title": "Check responsiveness", "detail": "If unresponsive, check for breathing. Do not waste time draining water."},
                {"title": "Start rescue breathing", "detail": "Give 5 initial rescue breaths if not breathing. Then begin full CPR."},
                {"title": "Continue CPR", "detail": "Perform 30 chest compressions followed by 2 rescue breaths. Continue until help arrives."},
            ],
        },
    },
    "hi": {
        "burns": {
            "title": "जलन के लिए प्राथमिक उपचार",
            "warning": "बड़ी या गहरी जलन के लिए तुरंत चिकित्सा सहायता लें।",
            "steps": [
                {"title": "जलन को ठंडा करें", "detail": "जले हुए हिस्से को 10-20 मिनट तक ठंडे बहते पानी में रखें।"},
                {"title": "कसी चीजें हटाएं", "detail": "सूजन से पहले जले हिस्से के पास अंगूठी, घड़ी या कपड़े हटा दें।"},
                {"title": "बर्फ या मक्खन न लगाएं", "detail": "कभी भी बर्फ, मक्खन या टूथपेस्ट न लगाएं — ये नुकसान बढ़ा सकते हैं।"},
                {"title": "जलन को ढकें", "detail": "साफ, गैर-रोएंदार पट्टी या क्लिंग फिल्म से हल्के से ढकें।"},
                {"title": "दर्द का प्रबंधन", "detail": "जरूरत पड़ने पर पेरासिटामॉल या इबुप्रोफेन ले सकते हैं।"},
                {"title": "गंभीर होने पर सहायता लें", "detail": "हथेली से बड़ी जलन के लिए 108 पर कॉल करें।"},
            ],
        },
        "bleeding": {
            "title": "रक्तस्राव के लिए प्राथमिक उपचार",
            "warning": "10 मिनट में रक्तस्राव न रुके तो 108 पर तुरंत कॉल करें।",
            "steps": [
                {"title": "सीधा दबाव डालें", "detail": "साफ कपड़े या पट्टी से घाव पर मजबूती से दबाएं।"},
                {"title": "दबाव बनाए रखें", "detail": "कम से कम 10 मिनट तक बिना हटाए दबाव बनाए रखें।"},
                {"title": "घायल हिस्सा उठाएं", "detail": "रक्त प्रवाह धीमा करने के लिए घायल हिस्से को हृदय से ऊंचा रखें।"},
                {"title": "पट्टी बांधें", "detail": "रक्तस्राव कम होने पर कपड़े को बैंडेज से सुरक्षित करें।"},
                {"title": "सदमे का ध्यान रखें", "detail": "पीला, ठंडा या भ्रमित होने पर लेटा दें और पैर ऊंचे करें।"},
                {"title": "चिकित्सा सहायता लें", "detail": "गहरे या न रुकने वाले घावों के लिए तुरंत डॉक्टर से मिलें।"},
            ],
        },
        "fracture": {"title": "फ्रैक्चर के लिए प्राथमिक उपचार", "warning": "हड्डी सीधी करने की कोशिश न करें।", "steps": [{"title": "रक्तस्राव रोकें", "detail": "खुले फ्रैक्चर में घाव के आसपास हल्के से दबाएं।"}, {"title": "चोट को स्थिर करें", "detail": "पैडिंग और सख्त सहारे से स्प्लिंट करें।"}, {"title": "बर्फ लगाएं", "detail": "कपड़े में बर्फ लपेटकर लगाएं। सीधे त्वचा पर न लगाएं।"}, {"title": "सदमे का इलाज", "detail": "चक्कर या पीलापन हो तो गर्म और शांत रखें।"}, {"title": "खाना-पानी न दें", "detail": "सर्जरी की जरूरत हो सकती है।"}, {"title": "108 पर कॉल करें", "detail": "रीढ़ या कूल्हे के फ्रैक्चर के लिए 108 कॉल करें।"}]},
        "choking": {"title": "गले में अटकने पर प्राथमिक उपचार", "warning": "बेहोश होने पर CPR शुरू करें।", "steps": [{"title": "स्थिति का आकलन", "detail": "पूछें क्या आप घुट रहे हैं? बोल सकते हैं तो खांसने को कहें।"}, {"title": "पीठ पर थपकी", "detail": "आगे झुकाएं, कंधों के बीच 5 बार थपकी दें।"}, {"title": "हेम्लिच मैन्युवर", "detail": "नाभि के ऊपर मुट्ठी रखकर 5 बार अंदर-ऊपर खींचें।"}, {"title": "बारी-बारी करें", "detail": "5 थपकी + 5 दबाव तब तक दोहराएं।"}, {"title": "शिशुओं के लिए", "detail": "5 पीठ थपकी + 5 छाती दबाव।"}, {"title": "108 पर कॉल करें", "detail": "घुटन जारी रहे तो 108 पर कॉल करें।"}]},
        "heart": {"title": "दिल के दौरे के लिए प्राथमिक उपचार", "warning": "तुरंत 108 पर कॉल करें।", "steps": [{"title": "108 पर कॉल करें", "detail": "तुरंत 108 पर कॉल करें।"}, {"title": "आरामदायक स्थिति", "detail": "बैठने या लेटने में मदद करें।"}, {"title": "एस्पिरिन दें", "detail": "एलर्जी न हो तो 325mg एस्पिरिन चबाकर दें।"}, {"title": "सांस की निगरानी", "detail": "सांस रुके तो CPR के लिए तैयार रहें।"}, {"title": "CPR करें", "detail": "30 छाती दबाव + 2 सांसें दोहराएं।"}, {"title": "AED का उपयोग", "detail": "डिफिब्रिलेटर उपलब्ध हो तो चालू करें।"}]},
        "drowning": {"title": "डूबने पर प्राथमिक उपचार", "warning": "तुरंत 108 पर कॉल करें।", "steps": [{"title": "सुरक्षा पहले", "detail": "प्रशिक्षित न हों तो पानी में न कूदें।"}, {"title": "सुरक्षित स्थान पर लाएं", "detail": "जमीन पर लाएं, सिर-गर्दन सहारा दें।"}, {"title": "108 पर कॉल करें", "detail": "तुरंत आपातकालीन सेवाएं बुलाएं।"}, {"title": "होश जांचें", "detail": "बेहोश हो तो सांस जांचें।"}, {"title": "सांस दें", "detail": "5 बचाव सांसें दें, फिर CPR शुरू करें।"}, {"title": "CPR जारी रखें", "detail": "30 दबाव + 2 सांसें जारी रखें।"}]},
    },
    "mr": {
        "burns": {"title": "जळण्यासाठी प्रथमोपचार", "warning": "मोठ्या जळण्यासाठी ताबडतोब वैद्यकीय मदत घ्या.", "steps": [{"title": "जळण थंड करा", "detail": "10-20 मिनिटे थंड वाहत्या पाण्याखाली ठेवा."}, {"title": "कडक वस्तू काढा", "detail": "सूज येण्यापूर्वी अंगठी, घड्याळ काढा."}, {"title": "बर्फ लावू नका", "detail": "बर्फ, लोणी किंवा टूथपेस्ट लावू नका."}, {"title": "जळण झाका", "detail": "स्वच्छ कापडाने हळूवारपणे झाका."}, {"title": "वेदना व्यवस्थापन", "detail": "पॅरासिटामॉल घ्या."}, {"title": "गंभीर असल्यास 108", "detail": "मोठ्या जळण्यासाठी 108 वर कॉल करा."}]},
        "bleeding": {"title": "रक्तस्रावासाठी प्रथमोपचार", "warning": "10 मिनिटांत रक्तस्राव थांबला नाही तर 108 वर कॉल करा.", "steps": [{"title": "थेट दाब द्या", "detail": "स्वच्छ कापडाने जखमेवर घट्ट दाब द्या."}, {"title": "दाब ठेवा", "detail": "10 मिनिटे न उचलता दाब ठेवा."}, {"title": "जखमी भाग वर करा", "detail": "हृदयापेक्षा वर ठेवा."}, {"title": "पट्टी बांधा", "detail": "बँडेजने सुरक्षित करा."}, {"title": "धक्का लक्षात घ्या", "detail": "फिकट असल्यास झोपवा, पाय वर करा."}, {"title": "डॉक्टरांकडे जा", "detail": "खोल जखमांसाठी डॉक्टर गाठा."}]},
        "fracture": {"title": "फ्रॅक्चरसाठी प्रथमोपचार", "warning": "हाड सरळ करण्याचा प्रयत्न करू नका.", "steps": [{"title": "रक्तस्राव थांबवा", "detail": "जखमेभोवती हळूवारपणे दाब द्या."}, {"title": "स्थिर करा", "detail": "स्प्लिंट करा, हलवू नका."}, {"title": "बर्फ लावा", "detail": "कापडात बर्फ गुंडाळून लावा."}, {"title": "धक्का उपचार", "detail": "उबदार आणि शांत ठेवा."}, {"title": "काहीही देऊ नका", "detail": "शस्त्रक्रिया लागू शकते."}, {"title": "108 वर कॉल करा", "detail": "मणका फ्रॅक्चरसाठी 108."}]},
        "choking": {"title": "श्वास अडकल्यास प्रथमोपचार", "warning": "बेशुद्ध झाल्यास CPR सुरू करा.", "steps": [{"title": "परिस्थिती मूल्यांकन", "detail": "बोलत असल्यास जोरात खोकण्यास सांगा."}, {"title": "पाठीवर थाप", "detail": "5 वेळा जोरात थाप द्या."}, {"title": "हेम्लिच मॅन्युव्हर", "detail": "नाभीच्या वर मुठ ठेवून 5 वेळा खेचा."}, {"title": "आळीपाळीने करा", "detail": "5 थापा + 5 दाब करा."}, {"title": "लहान मुलांसाठी", "detail": "5 थापा + 5 छातीचे दाब."}, {"title": "108 वर कॉल करा", "detail": "श्वास अडकत राहिल्यास 108."}]},
        "heart": {"title": "हृदयविकाराच्या झटक्यासाठी प्रथमोपचार", "warning": "ताबडतोब 108 वर कॉल करा.", "steps": [{"title": "108 वर कॉल करा", "detail": "ताबडतोब 108 वर कॉल करा."}, {"title": "आरामदायक स्थिती", "detail": "बसण्यास मदत करा, कपडे सैल करा."}, {"title": "अॅस्पिरिन द्या", "detail": "अॅलर्जी नसल्यास 325mg अॅस्पिरिन चावून द्या."}, {"title": "श्वासावर लक्ष", "detail": "श्वास थांबला तर CPR करा."}, {"title": "CPR करा", "detail": "30 दाब + 2 श्वास दोहराते राहा."}, {"title": "AED वापरा", "detail": "डिफिब्रिलेटर असल्यास वापरा."}]},
        "drowning": {"title": "बुडण्यासाठी प्रथमोपचार", "warning": "ताबडतोब 108 वर कॉल करा.", "steps": [{"title": "आधी स्वतःची सुरक्षा", "detail": "प्रशिक्षित नसल्यास पाण्यात उडी मारू नका."}, {"title": "सुरक्षित ठिकाणी आणा", "detail": "जमिनीवर आणा, डोके आधार द्या."}, {"title": "108 वर कॉल करा", "detail": "ताबडतोब आपत्कालीन सेवा बोलवा."}, {"title": "शुद्धी तपासा", "detail": "श्वास तपासा."}, {"title": "श्वास द्या", "detail": "5 वेळा तोंडाने श्वास द्या, मग CPR."}, {"title": "CPR चालू ठेवा", "detail": "30 दाब + 2 श्वास मदत येईपर्यंत."}]},
    },
}


@firstaid_bp.route("/<lang>/<emergency_type>", methods=["GET"])
def get_instructions(lang, emergency_type):
    """Return first aid instructions for a given language and emergency type."""
    lang = lang if lang in FIRST_AID else "en"
    data = FIRST_AID[lang].get(emergency_type)

    if not data:
        return jsonify({"success": False, "message": "Emergency type not found."}), 404

    # Log to history if user is logged in
    if "user_id" in session:
        try:
            db = get_db()
            db.execute(
                "INSERT INTO history (user_id, emergency_type, action, language) VALUES (?, ?, ?, ?)",
                (session["user_id"], emergency_type, "Viewed first aid", lang),
            )
            db.commit()
        except Exception:
            pass

    return jsonify({"success": True, "lang": lang, "type": emergency_type, "data": data})


@firstaid_bp.route("/types", methods=["GET"])
def get_types():
    """Return list of all available emergency types."""
    types = [
        {"id": "burns",    "label": "Burns",        "icon": "🔥", "sub": "Heat / chemical"},
        {"id": "bleeding", "label": "Bleeding",     "icon": "🩸", "sub": "Wound / cut"},
        {"id": "fracture", "label": "Fracture",     "icon": "🦴", "sub": "Broken bone"},
        {"id": "choking",  "label": "Choking",      "icon": "😮‍💨","sub": "Airway blocked"},
        {"id": "heart",    "label": "Heart Attack", "icon": "❤️", "sub": "Cardiac event"},
        {"id": "drowning", "label": "Drowning",     "icon": "🌊", "sub": "Water rescue"},
    ]
    return jsonify({"success": True, "types": types})
