**THIS IS AN AUTOMATION PROJECT FOR : ALL CARE CORPORATION BASED IN KOLKATA.**

**-->HOW TO RUN THIS PROGRAMME?<--**

_-open up the terminal interface_

_-run pip install -r requirements.txt_

_-create a seperate ".env" file with the secret values to be used_





**-->Operations of different functions of files<--**

●app/db/local_store.py

    get_connection()
        ----establishes connection with the sql database
    
    create_tables()
        ----creates the sqlite database if not exisits

    insert_lead()
        ----inserts a new lead with Lead as the class and lead_id as primary key

    get_all_leads_by_phone()
        ----fetches records of all leads open or closed by a specific phone number
    
    get_active_lead()
        ----fetches the active leads of a phone number only
    
    update_lead_status()
        ----updates lead status to required value listed in LeadStatus classs

    
    