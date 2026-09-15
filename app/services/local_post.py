from app.integrations.gemini_client import generate_post_caption,generate_picture
from app.integrations.gbp_client import create_local_post
from app.integrations.img_bb_client import upload_image_and_get_url
SERVICES = [
    "Tally Installation",
    "Printers and Scanner Installation",
    "CCTV Installation",
    "Biometric Installation",
    "Fire Alarm Installation",
    "EPBX & Intercom Installation",
    "Networking",
    "WiFi Installation",
    "Server & Workstation Installation",
    "UPS Installation",
    "Desktop & Laptop Installation",
]
SERVICE_PINCODES = [
    "700001", "700002", "700003", "700004", "700005", "700006", "700007", "700008", "700009", "700010",
    "700011", "700012", "700013", "700014", "700015", "700016", "700017", "700018", "700019", "700020",
    "700021", "700022", "700023", "700024", "700025", "700026", "700027", "700028", "700029", "700030",
    "700031", "700032", "700033", "700034", "700035", "700036", "700037", "700038", "700039", "700040",
    "700041", "700042", "700043", "700044", "700045", "700046", "700047", "700048", "700049", "700050",
    "700051", "700052", "700053", "700054", "700055", "700056", "700057", "700058", "700059", "700060",
    "700061", "700062", "700063", "700064", "700065", "700066", "700067", "700068", "700069", "700070",
    "700071", "700072", "700073", "700074", "700075", "700076", "700077", "700078", "700079", "700080",
    "700081", "700082", "700083", "700084", "700085", "700086", "700087", "700088", "700089", "700090",
    "700091", "700092", "700093", "700094", "700095", "700096", "700097", "700098", "700099", "700100",
    "700101", "700102", "700103", "700104", "700105", "700106", "700107", "700108", "700109", "700110",
    "700111", "700112", "700113", "700114", "700115", "700116", "700117", "700118", "700119", "700120",
    "700121", "700122", "700123", "700124", "700125", "700126", "700127", "700128", "700129", "700130",
    "700131", "700132", "700133", "700134", "700135", "700136", "700137", "700048", "700055", "700056",
    "700059", "700064", "700089", "700091", "700097", "700098", "700101", "700102", "700103", "700104",
    "700105", "700106", "700110", "700113", "700119", "700120", "700121", "700122", "700123", "700124",
    "700125", "700126", "700127", "700128", "700129", "700130", "700131", "700132", "700133", "700135",
    "700136", "700137", "700138", "700139", "700140", "700141", "700142", "700143", "700144", "700145",
    "700146", "700148", "700149", "700150", "700151", "700152", "700153", "700154", "700155", "700156",
    "700157", "711101", "711102", "711103", "711104", "711105", "711106", "711107", "711108", "711109",
    "711110", "711111", "711112", "711113", "711114", "711115", "711201", "711202", "711203", "711204",
    "711205", "711206", "712101", "712102", "712103", "712104", "712105", "712121", "712123", "712124",
    "712125", "712136", "712137", "712138", "712139", "712201", "712202", "712203", "712204", "712221",
    "712222", "712223", "712232", "712233", "712234", "712235", "712245", "712246", "712247", "712248",
    "712249", "712250", "712258", "712310", "712311", "712502", "712503", "743122", "743123", "743124",
    "743125", "743126", "743127", "743128", "743129", "743130", "743133", "743134", "743135", "743136",
    "743144", "743145", "743165", "743166", "743193", "743194", "743221", "743222", "743223", "743232",
    "743233", "743234", "743235", "743244", "743245", "743247", "743248", "743249", "743251", "743252",
    "743262", "743263", "743268", "743269", "743270", "743271", "743272", "743273", "743274", "743276",
    "743286", "743287", "743288", "743289", "743290", "743291", "743292", "743293", "743294", "743295"
]


DRY_RUN = True

picture_prompt = f"""
f"Professional photo representing {SERVICES} services for an IT infrastructure "
f"and security systems company in West Bengal, India. Realistic , the name of the company is ALL CARE CORPORATION."     
f"Mention the name of the company with the phone number icon with phone number : "+91 098362 13939", make the pictures of few services
f"dont invent details like pricing and all just make for a promotion post with a good heading , make it look nice"
"""



def post_daily_content(account_location: str):
    
    caption = generate_post_caption(services=SERVICES, pincodes=SERVICE_PINCODES)
    print(f"Generated caption: {caption}")

    # local_filename = generate_picture(
    #     f"Professional photo representing {SERVICES} services for an IT infrastructure"
    #     f"and security systems company in Kolkata, India. Realistic , the name of the company is ALL CARE CORPORATION."
    #     f"Make it look treat to eyes, also mention the company name in the photo..."
    # )
    # print(f"Generated image: {local_filename}")

    if DRY_RUN:
        print("DRY RUN — not posting. Caption and image ready above for review.")
        return

    photo_url = upload_image_and_get_url("teest.png")
    result = create_local_post(account_location, caption,photo_url)
    print("Posted:", result.get("name"))

if __name__ == "__main__":
    account_location = "accounts/117897107069643471601/locations/5159737380424683697"
    post_daily_content(account_location)