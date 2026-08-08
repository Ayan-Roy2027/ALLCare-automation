import pandas as pd
from pathlib import Path
from app.db.local_store import count_opt_in_sends_today,insert_opt_in_record,update_opt_in_status,get_opt_in_status
from app.models.schemas import OptInRecord,OptInStatus
from app.integrations.whatsapp_client import send_template_message
from app.integrations.gemini_client import generate_text


df = pd.read_csv("contacts.csv",dtype={"phone":str})
DAILY_CAP = 500
def send_opt_in(df):
    count_today = count_opt_in_sends_today()

    for index,row in df.iterrows():
        if count_today >= DAILY_CAP:
            print("500 opt-ins sent today-- stopping.")
            break

        phone = row['phone']
        record = get_opt_in_status(phone)

        if record is None:
            insert_opt_in_record(OptInRecord(phone=phone))
            print(f"--OPT IN REQUEST SENT VIA WHATSAPP-- to {phone}")
            update_opt_in_status(phone=phone,new_status=OptInStatus.OPT_IN_SENT)
            count_today += 1
            continue

        if record.status == OptInStatus.OPTED_IN:
            text= generate_text(prompt='Send daily update about cctv or any other services')
            print(f'DIGITAL MESSAGE : {text} SENT VIA WHATSAPP TO {phone}')
            count_today+=1
            continue
        
        if record.status ==  OptInStatus.OPT_IN_SENT:
            continue

        if record.status == OptInStatus.OPTED_OUT:
            continue       

        if record.status == OptInStatus.NOT_CONTACTED:
            print(f"--OPT IN REQUEST SENT VIA WHATSAPP-- to {phone}")
            update_opt_in_status(phone=phone, new_status=OptInStatus.OPT_IN_SENT)
            count_today += 1
            continue

    print("DRIP CAMPAIGN COMPLETED FOR TODAY....")



