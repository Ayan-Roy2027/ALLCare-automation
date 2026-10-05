import random

from app.integrations.gbp_client import get_credentials
from app.integrations.gemini_client import generate_text, generate_json
from googleapiclient.discovery import build

DRY_RUN = True  # see every proposed change before anything auto-applies

PINCODES = [
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
    "700131", "700132", "700133", "700134", "700135", "700136", "700137", "700138", "700139", "700140",
    "700141", "700142", "700143", "700144", "700145", "700146", "700148", "700149", "700150", "700151",
    "700152", "700153", "700154", "700155", "700156", "700157",
    "711101", "711102", "711103", "711104", "711105", "711106", "711107", "711108", "711109", "711110",
    "711111", "711112", "711113", "711114", "711115", "711201", "711202", "711203", "711204", "711205",
    "711206",
    "712101", "712102", "712103", "712104", "712105", "712121", "712123", "712124", "712125", "712136",
    "712137", "712138", "712139", "712201", "712202", "712203", "712204", "712221", "712222", "712223",
    "712232", "712233", "712234", "712235", "712245", "712246", "712247", "712248", "712249", "712250",
    "712258", "712310", "712311", "712502", "712503",
    "743122", "743123", "743124", "743125", "743126", "743127", "743128", "743129", "743130", "743133",
    "743134", "743135", "743136", "743144", "743145", "743165", "743166", "743193", "743194", "743221",
    "743222", "743223", "743232", "743233", "743234", "743235", "743244", "743245", "743247", "743248",
    "743249", "743251", "743252", "743262", "743263", "743268", "743269", "743270", "743271", "743272",
    "743273", "743274", "743276", "743286", "743287", "743288", "743289", "743290", "743291", "743292",
    "743293", "743294", "743295",
]
# deduplicated from your original list — a few numbers appeared twice


def get_full_location_data(location_name: str) -> dict:
    creds = get_credentials()
    service = build("mybusinessbusinessinformation", "v1", credentials=creds)

    location = service.locations().get(
        name=location_name,
        readMask="title,storefrontAddress,phoneNumbers,websiteUri,categories,serviceItems,profile"
    ).execute()

    return location


def sample_pincodes(n: int = 3) -> list[str]:
    return random.sample(PINCODES, min(n, len(PINCODES)))


# ---------- overall profile description audit ----------

def audit_seo(location_name: str) -> dict:
    location = get_full_location_data(location_name)

    current_description = location.get("profile", {}).get("description", "")
    current_services = location.get("serviceItems", [])
    categories = location.get("categories", {})
    sample = sample_pincodes(3)

    prompt = f"""
You are an SEO auditor for Allcare Corporation's Google Business Profile, an IT
infrastructure and security systems supplier in Kolkata, West Bengal, India.

Current business description: "{current_description}"
Current primary category: {categories.get("primaryCategory", {}).get("displayName")}
Current listed services/products: {current_services}
A sample of real service-area pincodes (do not treat this as the full list,
just use 2-3 of these naturally if relevant): {", ".join(sample)}

Analyze this for local SEO effectiveness and respond as JSON with this exact shape:
{{
  "description_issues": "what's missing or weak in the current description",
  "suggested_description": "a rewritten description, under 750 characters, naturally
    including primary/secondary keywords (CCTV installation, biometric systems,
    fire alarm, networking, Kolkata, West Bengal) and 2-3 of the sample pincodes",
  "missing_keywords": ["list", "of", "keywords", "not", "currently", "represented"],
  "service_description_issues": "gaps or weak descriptions in the listed services"
}}

Do not invent services, brands, or pincodes not given to you above. Only work with
what's given.
"""
    audit_result = generate_json(prompt)
    return audit_result


def apply_description_change(location_name: str, new_description: str):
    creds = get_credentials()
    service = build("mybusinessbusinessinformation", "v1", credentials=creds)

    result = service.locations().patch(
        name=location_name,
        updateMask="profile",
        body={"profile": {"description": new_description}},
    ).execute()

    return result


# ---------- per-service description generation ----------

def generate_service_descriptions(service_items: list[dict]) -> list[dict]:
    results = []

    for item in service_items:
        service_name = (
            item.get("structuredServiceItem", {}).get("serviceTypeId", "")
            or item.get("freeFormServiceItem", {}).get("label", {}).get("displayName", "Unknown service")
        )
        sample = sample_pincodes(1)

        prompt = f"""
You are writing a short Google Business Profile service description for Allcare
Corporation, an IT infrastructure and security systems supplier in Kolkata, West Bengal.

Service name: "{service_name}"
A real service-area pincode you may mention naturally, or skip if it doesn't fit: {sample[0]}

Write a concise service description (under 300 characters) that:
- Naturally includes the service name and relevant local SEO terms (Kolkata, West Bengal).
- Does NOT mention specific brands, prices, or claims not given above.
- Output ONLY the description text, no preamble, no quotation marks.
"""
        description = generate_text(prompt)
        results.append({"service": service_name, "suggested_description": description})

    return results


def apply_service_description(location_name: str, service_item: dict, new_description: str):
    # NOTE: the exact field/updateMask for patching an individual serviceItem's
    # description has not been verified against a real response yet — confirm
    # the correct structured path before relying on this in DRY_RUN = False mode.
    raise NotImplementedError(
        "Per-service description patching needs verification against a real "
        "serviceItems response before this is safe to call."
    )


# ---------- orchestration ----------

def run_seo_audit(location_name: str):
    audit_result = audit_seo(location_name)

    print("--- SEO Audit: Business Description ---")
    print(f"Description issues: {audit_result['description_issues']}")
    print(f"Suggested description: {audit_result['suggested_description']}")
    print(f"Missing keywords: {audit_result['missing_keywords']}")
    print(f"Service description issues: {audit_result['service_description_issues']}")

    if DRY_RUN:
        print("\nDRY RUN — description change not applied.")
    else:
        apply_description_change(location_name, audit_result["suggested_description"])
        print("\nApplied new description to GMB profile.")

    location = get_full_location_data(location_name)
    service_items = location.get("serviceItems", [])

    if not service_items:
        print("\nNo structured service items found on this profile — skipping service descriptions.")
        return

    descriptions = generate_service_descriptions(service_items)

    print(f"\n--- Service Description Suggestions ({len(descriptions)} services) ---")
    for d in descriptions:
        print(f"\nService: {d['service']}")
        print(f"Suggested description: {d['suggested_description']}")

    if DRY_RUN:
        print("\nDRY RUN — service descriptions not applied.")
    else:
        print("\nService-level auto-apply is not implemented yet — see apply_service_description().")


if __name__ == "__main__":
    location_name = "locations/5159737380424683697"
    run_seo_audit(location_name)