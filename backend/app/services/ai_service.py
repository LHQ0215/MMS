from ..config import settings
import warnings
import requests
import json
import re

# Suppress SSL warnings for self-signed/unverified HTTPS
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

# Force direct connections - prevents ProxyError when auto-detected proxy does not exist
_NO_PROXY = {"http": "", "https": ""}


# ---------------------------------------------------------------------------
# Comprehensive Medical Knowledge Base
# ---------------------------------------------------------------------------

_KNOWLEDGE = [
    {
        "keywords": ["发烧", "发热", "高热", "低烧", "体温高", "temperature"],
        "diagnosis": "急性发热待查",
        "department": "内科",
        "common": "发热",
        "advice": "多休息，多饮水，注意监测体温。体温超过38.5℃可考虑物理降温或服用退烧药（如布洛芬）。如持续发热超过3天或伴有意识改变、呼吸困难，请立即就医。"
    },
    {
        "keywords": ["咳嗽", "咳痰", "干咳", "咳血", "咯血", "气喘", "气短", "呼吸困难", "胸闷", "胸痛", "呼吸"],
        "diagnosis": "呼吸道感染待查",
        "department": "内科",
        "common": "咳嗽",
        "advice": "注意休息，保持室内空气流通。多饮用温开水，可使用加湿器缓解干咳。避免吸烟及二手烟环境。咳嗽超过2周或伴有发热、呼吸困难时请及时就医。"
    },
    {
        "keywords": ["流鼻涕", "鼻塞", "打喷嚏", "咽痛", "喉咙痛", "咽喉痛", "嗓子痛", "扁桃体", "感冒", "流感", "鼻咽"],
        "diagnosis": "上呼吸道感染（感冒）",
        "department": "内科",
        "common": "感冒",
        "advice": "注意保暖，保证充足休息。多喝温开水或姜茶，可服用维生素C。可用盐水漱口缓解咽喉痛。如高烧不退或症状加重，请及时就医。"
    },
    {
        "keywords": ["头痛", "偏头痛", "头胀", "头晕", "眩晕", "天旋地转", "头重脚轻"],
        "diagnosis": "头痛待查",
        "department": "神经内科",
        "common": "头痛",
        "advice": "保持充足睡眠，避免过度疲劳和长时间使用电子设备。可适当按摩太阳穴。偏头痛患者应避免强光和噪音刺激。剧烈头痛或伴有呕吐、意识障碍时请立即就医。"
    },
    {
        "keywords": ["胃痛", "胃疼", "胃胀", "胃酸", "反酸", "烧心", "嗳气", "打嗝", "消化不良", "食欲不振"],
        "diagnosis": "胃部不适待查",
        "department": "消化内科",
        "common": "胃部不适",
        "advice": "规律饮食，少食多餐，避免辛辣、油腻、生冷食物。饭后不宜立即躺下。如伴有黑便、呕血或体重下降，请尽快进行胃镜检查。"
    },
    {
        "keywords": ["腹痛", "肚子痛", "腹泻", "拉肚子", "恶心", "呕吐", "便秘", "腹胀", "肠鸣", "便血", "大便异常"],
        "diagnosis": "消化系统疾病待查",
        "department": "消化内科",
        "common": "腹痛腹泻",
        "advice": "注意饮食卫生，避免食用不洁食物。腹泻时注意补充水分和电解质（可饮用淡盐水或口服补液盐）。腹痛剧烈、便血或伴有高热时需立即就医。"
    },
    {
        "keywords": ["皮肤", "皮疹", "瘙痒", "红疹", "荨麻疹", "湿疹", "过敏", "红斑", "痘痘", "痤疮", "水疱", "脱屑", "癣"],
        "diagnosis": "皮肤病变待查",
        "department": "皮肤科",
        "common": "皮肤病",
        "advice": "注意皮肤清洁和保湿，避免搔抓以防感染。避免接触过敏原。不自行使用激素类药物。皮疹伴有发热或迅速扩散时应立即就医。"
    },
    {
        "keywords": ["眼睛痛", "眼痛", "视力", "视力下降", "模糊", "红眼", "眼红", "流泪", "畏光", "眼干", "干眼", "飞蚊", "眼胀"],
        "diagnosis": "眼部疾病待查",
        "department": "眼科",
        "common": "眼病",
        "advice": "注意用眼卫生，每45分钟休息眼睛。避免用手揉眼。使用合适的照明环境。视力突然变化、剧烈眼痛或眼外伤需立即就医。"
    },
    {
        "keywords": ["耳痛", "耳鸣", "听力", "听力下降", "耳聋", "耳朵", "中耳", "耳流脓", "耳闷"],
        "diagnosis": "耳部疾病待查",
        "department": "耳鼻喉科",
        "common": "耳病",
        "advice": "避免用棉签等物品掏耳。洗澡时注意防止耳道进水。耳痛剧烈或伴有发热需尽早就医。突发性耳聋需在72小时内进行治疗。"
    },
    {
        "keywords": ["鼻炎", "鼻窦", "鼻出血", "鼻血", "鼻息肉", "嗅觉", "打鼾", "鼻塞"],
        "diagnosis": "鼻部疾病待查",
        "department": "耳鼻喉科",
        "common": "鼻病",
        "advice": "保持鼻腔湿润，可用生理盐水洗鼻。鼻出血时保持坐姿前倾，捏住鼻翼10分钟。长期鼻塞或反复鼻出血需就医检查。"
    },
    {
        "keywords": ["牙痛", "牙疼", "牙龈", "牙齿", "口腔溃疡", "口腔", "舌", "颌", "腮"],
        "diagnosis": "口腔疾病待查",
        "department": "口腔科",
        "common": "口腔病",
        "advice": "注意口腔卫生，每天刷牙两次并使用牙线。避免过冷过热刺激。口腔溃疡超过2周未愈合需就医检查。牙痛剧烈可服用布洛芬缓解。"
    },
    {
        "keywords": ["心悸", "心慌", "心跳", "心律", "心动过速", "胸闷", "心前区", "胸痛", "心绞痛", "压榨感"],
        "diagnosis": "心血管系统疾病待查",
        "department": "心血管内科",
        "common": "心脏不适",
        "advice": "立即休息，避免情绪激动和剧烈运动。低盐低脂饮食，控制血压和血脂。胸痛持续不缓解或伴有出冷汗、恶心时请立即拨打急救电话。",
        "risk_boost": "high"
    },
    {
        "keywords": ["高血压", "血压高", "血压"],
        "diagnosis": "高血压待查",
        "department": "心血管内科",
        "common": "高血压",
        "advice": "规律监测血压，低盐饮食（每日不超过5g盐），戒烟限酒，适度运动。定期服用降压药，不可随意停药。血压急剧升高（≥180/120）需立即就医。",
        "risk_boost": "medium"
    },
    {
        "keywords": ["糖尿病", "血糖高", "多饮多尿", "消瘦", "口渴", "血糖"],
        "diagnosis": "血糖异常/糖尿病待查",
        "department": "内分泌科",
        "common": "糖尿病",
        "advice": "控制碳水化合物摄入，少食多餐。规律监测血糖，坚持运动。遵医嘱用药，不可自行调整药量。出现意识模糊或恶心呕吐需立即就医。",
        "risk_boost": "medium"
    },
    {
        "keywords": ["外伤", "骨折", "扭伤", "挫伤", "伤口", "出血", "跌打", "损伤", "关节肿", "淤青"],
        "diagnosis": "外伤待查",
        "department": "外科",
        "common": "外伤",
        "advice": "伤口用干净纱布压迫止血，用碘伏消毒后包扎。疑似骨折时应固定患肢避免移动。严重出血或意识不清请立即拨打急救电话。",
        "risk_boost": "high"
    },
    {
        "keywords": ["腰痛", "背痛", "腰疼", "腰椎", "椎间盘", "坐骨", "腰酸", "腰肌"],
        "diagnosis": "腰背部疼痛待查",
        "department": "骨科",
        "common": "腰痛",
        "advice": "避免久坐久站，保持正确的坐姿。可使用热敷缓解肌肉紧张。疼痛超过两周或伴下肢麻木、大小便障碍时请尽早就医。",
        "risk_boost": "medium"
    },
    {
        "keywords": ["关节痛", "关节肿", "关节炎", "风湿", "膝盖痛", "膝关节", "肩痛", "肩周", "颈椎", "颈痛"],
        "diagnosis": "骨关节疾病待查",
        "department": "骨科",
        "common": "关节痛",
        "advice": "注意保暖，适度活动关节，避免过度负重。控制体重以减轻关节负担。关节红肿热痛或伴有发热需就医检查。"
    },
    {
        "keywords": ["失眠", "入睡困难", "多梦", "易醒", "睡眠", "梦魇"],
        "diagnosis": "睡眠障碍待查",
        "department": "神经内科",
        "common": "失眠",
        "advice": "保持规律作息，睡前避免使用电子设备。减少咖啡因摄入，可进行冥想或深呼吸放松。长期失眠需咨询医生，不可自行长期服用安眠药。"
    },
    {
        "keywords": ["焦虑", "紧张", "恐慌", "害怕", "烦躁", "易怒", "不安", "抑郁", "情绪低落", "心情", "压力"],
        "diagnosis": "情绪/心理障碍待查",
        "department": "心理科",
        "common": "心理问题",
        "advice": "尝试与亲友倾诉，保持规律运动，练习正念冥想。严重或持续的情绪问题建议寻求心理咨询师或精神科医生的帮助。有自伤意念时请立即拨打心理援助热线。",
        "risk_boost": "medium"
    },
    {
        "keywords": ["过敏", "过敏反应", "荨麻疹", "红肿", "过敏性", "药疹", "食物过敏", "花粉"],
        "diagnosis": "过敏反应待查",
        "department": "皮肤科",
        "common": "过敏",
        "advice": "避免接触已知过敏原。轻度过敏可服用抗组胺药（如氯雷他定）。出现呼吸困难、喉头水肿等严重过敏反应需立即就医或拨打急救电话。",
        "risk_boost": "high"
    },
    {
        "keywords": ["恶心", "呕吐", "反胃", "厌食"],
        "diagnosis": "恶心/呕吐待查",
        "department": "消化内科",
        "common": "恶心呕吐",
        "advice": "少食多餐，吃清淡易消化的食物。避免油腻和刺激性食物。呕吐频繁需补充水分和电解质，防止脱水。持续超过48小时请就医。"
    },
    {
        "keywords": ["乏力", "疲劳", "无力", "精神不济", "虚弱", "没精神", "疲惫"],
        "diagnosis": "全身乏力待查",
        "department": "内科",
        "common": "乏力",
        "advice": "保持规律的作息和均衡饮食，适度运动。如伴有消瘦、发热、夜间盗汗等其他症状，建议进行血常规、甲状腺功能等检查。"
    },
    {
        "keywords": ["尿频", "尿急", "尿痛", "排尿", "血尿", "尿路", "尿道", "膀胱", "肾"],
        "diagnosis": "泌尿系统感染待查",
        "department": "泌尿外科",
        "common": "泌尿问题",
        "advice": "多饮水，勤排尿，注意个人卫生。避免憋尿。伴有发热或腰痛时需及时就医。建议进行尿常规检查。"
    },
    {
        "keywords": ["月经", "痛经", "月经不调", "白带", "阴道", "妇科", "盆腔", "乳房", "乳腺"],
        "diagnosis": "妇科疾病待查",
        "department": "妇产科",
        "common": "妇科问题",
        "advice": "保持外阴清洁卫生，规律进行妇科检查。月经异常或持续腹痛建议尽早就医。发现乳房肿块请进行乳腺超声检查。"
    },
    {
        "keywords": ["儿童", "小儿", "婴儿", "幼儿"],
        "diagnosis": "儿科疾病待查",
        "department": "儿科",
        "common": "儿科问题",
        "advice": "儿童病情变化快，建议尽早就医。注意测量体温，观察精神状态和饮食情况。3个月以下婴儿发热需立即就医。遵医嘱用药，不可给儿童使用成人药物。",
        "risk_boost": "high"
    },
    {
        "keywords": ["中医", "中药", "调理", "养生", "气血", "阴虚", "阳虚", "湿气", "体质"],
        "diagnosis": "中医体质调理",
        "department": "中医科",
        "common": "中医调理",
        "advice": "中医讲究辨证论治，建议到正规中医院就诊。根据体质进行调理：清淡饮食、规律作息、适当运动。避免自行配药服用。"
    },
    {
        "keywords": ["急诊", "急救", "猝死", "昏迷", "休克", "大出血", "中毒", "烧伤", "烫伤", "溺水", "电击"],
        "diagnosis": "急症待查",
        "department": "急诊科",
        "common": "急诊",
        "advice": "请立刻拨打120急救电话！在等待救护车期间：保持患者呼吸道通畅，如出血用干净布料压迫止血，不要随意移动疑似脊柱损伤的患者。",
        "risk_boost": "emergency"
    }
]

_BODY_PARTS = {
    "头": "神经内科", "颈": "骨科", "肩": "骨科", "背": "骨科",
    "腰": "骨科", "腿": "骨科", "膝": "骨科", "足": "骨科",
    "手": "骨科", "臂": "骨科",
    "眼": "眼科", "耳": "耳鼻喉科", "鼻": "耳鼻喉科", "喉": "耳鼻喉科",
    "口": "口腔科", "舌": "口腔科", "齿": "口腔科", "牙": "口腔科",
    "胸": "心血管内科", "心": "心血管内科", "肺": "内科",
    "胃": "消化内科", "腹": "消化内科", "肠": "消化内科",
    "肝": "消化内科", "胆": "消化内科", "脾": "消化内科",
    "肾": "泌尿外科", "膀胱": "泌尿外科",
    "皮": "皮肤科", "肤": "皮肤科",
}


def _score_match(keywords, symptom):
    """Count how many keywords appear in the symptom text."""
    count = 0
    for kw in keywords:
        if kw in symptom:
            count += 1
    return count


def _analyze_symptoms(symptoms, duration, severity):
    """Main analysis engine using multi-keyword weighted scoring."""
    s = symptoms.lower().strip()
    if not s:
        return {
            "diagnosis": "未检测到症状描述，请重新输入",
            "confidence": 0.0,
            "department": "内科",
            "risk_level": "low",
            "advice": "请详细描述您的症状，以便获得准确的分析建议。"
        }

    # Score each knowledge entry
    scored = []
    for entry in _KNOWLEDGE:
        score = _score_match(entry["keywords"], s)
        if score > 0:
            if entry["common"] in s:
                score += 2
            scored.append((score, entry))

    scored.sort(key=lambda x: x[0], reverse=True)

    if not scored:
        department = "内科"
        for part, dept in _BODY_PARTS.items():
            if part in s:
                department = dept
                break
        return {
            "diagnosis": f"根据您的症状描述（{symptoms}），建议前往{department}进行详细检查以明确诊断",
            "confidence": 0.35,
            "department": department,
            "risk_level": "medium" if severity in ("moderate", "severe") else "low",
            "advice": "您描述的症状较为特殊，建议到医院就诊，向医生详细描述您的情况，进行必要的检查以明确诊断。"
        }

    best_score, best_entry = scored[0]

    # Determine risk level
    risk_boost = best_entry.get("risk_boost", "low")
    if severity == "severe":
        risk_map = {"low": "medium", "medium": "high", "high": "high", "emergency": "emergency"}
    elif severity == "moderate":
        risk_map = {"low": "low", "medium": "medium", "high": "high", "emergency": "emergency"}
    else:
        risk_map = {"low": "low", "medium": "low", "high": "medium", "emergency": "emergency"}
    risk_level = risk_map.get(risk_boost, "low")

    # Compute confidence
    matched_kw = best_score
    total_kw = len(best_entry["keywords"])
    ratio = matched_kw / total_kw if total_kw > 0 else 0
    confidence = round(0.60 + ratio * 0.35, 2)
    confidence = min(confidence, 0.95)
    if severity == "severe" and risk_level != "emergency":
        confidence = min(confidence + 0.05, 0.95)

    # Build detailed diagnosis text
    duration_text = f"{duration}，" if duration else ""
    diagnosis_text = (
        f"基于您提供的症状信息（{duration_text}{severity}程度），"
        f"系统分析认为您可能存在{best_entry['diagnosis']}的可能。"
    )

    return {
        "diagnosis": diagnosis_text,
        "confidence": confidence,
        "department": best_entry["department"],
        "risk_level": risk_level,
        "advice": best_entry["advice"]
    }


class AIDiagnosisService:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.api_url = settings.AI_API_URL
        self.model = settings.AI_MODEL

    def diagnose(self, symptoms, duration, severity):
        """Call AI API for diagnosis. Falls back to local engine if API is unavailable."""
        if self.api_key:
            try:
                return self._call_api(symptoms, duration, severity)
            except Exception as e:
                print(f"AI API call failed: {e}, using local engine")
                return _analyze_symptoms(symptoms, duration, severity)
        return _analyze_symptoms(symptoms, duration, severity)

    def _clean_json_response(self, content):
        content = re.sub(r'^```(?:json)?\s*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n?```\s*$', '', content, flags=re.MULTILINE)
        return content.strip()

    def _call_api(self, symptoms, duration, severity):
        prompt = self._build_prompt(symptoms, duration, severity)
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的AI辅助诊断系统。请根据患者症状给出初步诊断建议、置信度、建议科室、风险等级（low/medium/high/emergency）和生活建议。返回JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 1000
        }
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=30, verify=False, proxies=_NO_PROXY)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        content = self._clean_json_response(content)
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return self._parse_text_response(content)

    def _build_prompt(self, symptoms, duration, severity):
        return f"""患者症状：{symptoms}
症状持续时间：{duration or '未说明'}
严重程度：{severity}
请分析并提供以下JSON格式的回复：
{{
    "diagnosis": "初步诊断结论",
    "confidence": 0.85,
    "department": "建议就诊科室",
    "risk_level": "low/medium/high/emergency",
    "advice": "给患者的生活建议"
}}"""

    def _parse_text_response(self, text):
        diag = re.search(r"诊断[：:](.*?)(?:\n|$)", text)
        dept = re.search(r"科室[：:](.*?)(?:\n|$)", text)
        return {
            "diagnosis": diag.group(1).strip() if diag else "请咨询专业医生",
            "confidence": 0.7,
            "department": dept.group(1).strip() if dept else "内科",
            "risk_level": "low",
            "advice": "建议及时就医，注意休息，保持良好的生活习惯。"
        }


ai_diagnosis_service = AIDiagnosisService()
# ---------------------------------------------------------------------------
# Free-form DeepSeek Chat Service (no medical guardrails)
# ---------------------------------------------------------------------------

class AIChatService:
    """Lightweight chat service that talks to DeepSeek without structured diagnosis constraints."""

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.api_url = settings.AI_API_URL
        self.model = settings.AI_MODEL

    def chat(self, messages):
        """Send a list of messages to DeepSeek and return the text response."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": self.model, "messages": messages, "temperature": 0.7, "max_tokens": 2000}
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=60, verify=False, proxies=_NO_PROXY)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()

    def __bool__(self):
        return bool(self.api_key)

ai_chat_service = AIChatService()
