import json
import re
import logging
import io
import contextlib
import speech_recognition as sr
from groq import Groq
import pygame
import os
import time
import warnings
import datetime
import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from dotenv import load_dotenv
from ddgs import DDGS

warnings.filterwarnings("ignore")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
logging.getLogger("chatterbox").setLevel(logging.ERROR)
logging.getLogger("transformers").setLevel(logging.ERROR)

# ============================================================
# إعدادات Groq
# ============================================================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("[ERROR] مفيش GROQ_API_KEY! حط المفتاح في ملف .env")

groq_client = Groq(api_key=GROQ_API_KEY)

print("[WAIT] بنجهز النظام...")
pygame.mixer.init(frequency=24000, size=-16, channels=1, buffer=512)

# ============================================================
# تحميل موديل Chatterbox
# ============================================================
print("[WAIT] بنحمل موديل Chatterbox Multilingual...")
print("      (أول مرة هيحمله من النت ~1.5GB، بعد كده هيبقى محفوظ محلياً)")

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] هيشتغل على: {device.upper()}")

tts_model = ChatterboxMultilingualTTS.from_pretrained(device=device)

if device == "cuda":
    torch.set_float32_matmul_precision("high")
    print("[INFO] TF32 مفعّل — CUDA أسرع!")

print("[WAIT] بنسخن الموديل (Pre-warm)...")
with contextlib.redirect_stderr(io.StringIO()):
    _w = tts_model.generate("مرحبا", language_id="ar")
del _w

print("[OK] النظام جاهز!")

# ============================================================
# الذاكرة + ملف الصوت المرجعي
# ============================================================
conversation_history = []
VOICE_REFERENCE = "voice_ref.wav"

# ============================================================
# أداة البحث
# ============================================================
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "لا توجد نتائج."
        return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
    except Exception:
        return "حدث خطأ في البحث."

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Use this tool to search the web for current news, sports match results, or any information you don't know. DO NOT use this tool if the user is just greeting you.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query in Arabic language ",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

# ============================================================
# فلتر تنظيف صارم جداً (عربي + أرقام + مسافات فقط)
# ============================================================
STRICT_ARABIC_REGEX = re.compile(
    r'[^'
    r'\u0600-\u06FF'  # الحروف العربية الأساسية
    r'\u0750-\u077F'  # إضافات عربية
    r'\uFB50-\uFDFF'  # أشكال تقديم عربية A
    r'\uFE70-\uFEFF'  # أشكال تقديم عربية B
    r'0-9'            # الأرقام
    r'\s'             # المسافات
    r']+'
)

def clean_and_filter(text):
    
    return STRICT_ARABIC_REGEX.sub('', text)


def generate_and_speak(messages):
    print("رد الذكاء الاصطناعي: ", end="", flush=True)
    full_response = ""

    try:
        stream = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            stream=True,
        )
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if not token:
                continue
            
            token = clean_and_filter(token)
            
            if not token:
                continue

            print(token, end="", flush=True)
            full_response += token

    except Exception as e:
        print(f"\n[LLM ERROR] {e}")

    print()  # سطر جديد بعد انتهاء الكتابة

   
    if full_response.strip():
        audio_file = "temp_tts_full.wav"
        ref_audio = VOICE_REFERENCE if os.path.exists(VOICE_REFERENCE) else None
        
        try:
            # تحويل النص بالكامل لصوت
            with contextlib.redirect_stderr(io.StringIO()):
                wav = tts_model.generate(
                    full_response.strip(),
                    language_id="ar",
                    audio_prompt_path=ref_audio,
                    exaggeration=0.4,
                )
            
            # حفظ الملف
            ta.save(audio_file, wav.cpu().float(), tts_model.sr)
            
            # تشغيل الصوت
            if pygame.mixer.get_init():
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                # الانتظار حتى ينتهي الصوت
                while pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                    
        except Exception as e:
            print(f"[TTS/AUDIO ERROR] {e}")
            
        finally:
            # تنظيف الملف الصوتي بعد الانتهاء
            if pygame.mixer.get_init():
                try:
                    pygame.mixer.music.unload()
                except:
                    pass
            time.sleep(0.05)
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass

    return full_response


# ============================================================
# دالة الرد الرئيسية
# ============================================================
def chat_and_get_response(user_text):
    global conversation_history
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    system_prompt = (
        f"Today's date is {current_date}. "
        "You are a smart and helpful assistant. "
        "CRITICAL INSTRUCTION: You MUST reply ONLY in Modern Standard Arabic (اللغة العربية الفصحى). "
        "Use ONLY Arabic script. NEVER use any non-Arabic characters: no Chinese, no Japanese, no Latin, no symbols, no punctuation. "
        "Do NOT use Egyptian slang. Keep your answers concise and direct. "
        "If the user greets you, greet them back in Arabic without using any tools."
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_text})

    try:
        detection = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
        )

        resp_msg    = detection.choices[0].message
        tool_calls  = resp_msg.tool_calls

        if tool_calls:
            messages.append(resp_msg)
            for tc in tool_calls:
                args         = json.loads(tc.function.arguments)
                search_query = args.get("query")
                print(f"\n[SEARCH] بيبحث عن: {search_query}...")
                result = search_web(search_query)
                messages.append({
                    "tool_call_id": tc.id,
                    "role":         "tool",
                    "name":         tc.function.name,
                    "content":      result,
                })
            full_response = generate_and_speak(messages)

        else:
            full_response = generate_and_speak(messages)

        if full_response:
            conversation_history.append({"role": "user",      "content": user_text})
            conversation_history.append({"role": "assistant", "content": full_response})
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]

    except Exception as e:
        print(f"\n[ERROR] {e}")


# ============================================================
# دالة الاستماع
# ============================================================
def listen_and_transcribe():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold        = 200
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold          = 2.0
    recognizer.non_speaking_duration    = 0.8

    with sr.Microphone() as source:
        print("\n[LIVE] تحدث الآن، أنا أستمع...")
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=30)

    try:
        text = recognizer.recognize_google(audio, language="ar-EG")
        print(f"إنت قلت: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("[ERROR] مشكلة في الاتصال بالإنترنت!")
        return ""


# ============================================================
# دورة التشغيل
# ============================================================
while True:
    try:
        user_text = listen_and_transcribe()
        if not user_text or len(user_text) < 2:
            continue
        if "سلام" in user_text or "وداعاً" in user_text:
            print("إلى اللقاء!")
            pygame.mixer.quit()
            break
        chat_and_get_response(user_text)
    except KeyboardInterrupt:
        print("\nتم إغلاق البرنامج. إلى اللقاء!")
        try:
            pygame.mixer.quit()
        except:
            pass
        break
    except Exception as e:
        print(f"[ERROR] {e}")
        continue