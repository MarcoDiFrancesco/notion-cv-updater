import os
from dotenv import load_dotenv
from openai import OpenAI
from notion_client import Client
from time import sleep
import httpx
import datetime


load_dotenv()

notion = Client(auth=os.environ["NOTION_API_TOKEN"])


# Disable SSL check for proxy
notion.client = httpx.Client(verify=False)


def get_job_desc(page_id):
    """
    Get description from page. Remove all styles except from bold.

    From:
        We are looking for this person.
        ### Who you are:
        - You are **below 150cm**.
        - You are a *fan*.
    To:
        We are looking for this person.
        Who you are:
        You are **below 150cm**.
        You are a fan.
    """
    blocks = notion.blocks.children.list(page_id)
    lines = []
    for b in blocks["results"]:
        # Type can be e.g. 'paragraph' or 'bulleted_list_item'
        b_type = b["type"]
        line_text = ""
        for chunk in b[b_type]["rich_text"]:
            # If bold underline the text, Notion API separates syles in "Block" into "Chunks"
            if chunk["annotations"]["bold"]:
                line_text += f"**{chunk['plain_text']}**"
            else:
                line_text += chunk["plain_text"]
        lines.append(line_text)
    job_desc = "\n".join(lines)
    return job_desc


def get_gpt_query(job_desc):
    # Import prompt examples
    with open("gpt-prompt-examples.txt", "r") as f:
        job_desc_examples = f.read()

    gpt_query = f"""
Write 1 paragraph of max 100 words for the CV Description, keeping the EXACT SAME structure as the examples.
Mention all the underlined keywords of the new job desciption like in the examples.

### NEW Job description.
{job_desc}

{job_desc_examples}
    """
    return gpt_query


# Example Job Application page:
# https://www.notion.so/e0d7f45ee32b4647b1d2a2fde900e1f3
job_desc = get_job_desc("e0d7f45ee32b4647b1d2a2fde900e1f3")
gpt_query = get_gpt_query(job_desc)

# Test the query on ChatGPT
with open("gpt-prompt-output.txt", "w") as f:
    f.write(gpt_query)


client = OpenAI()


def get_gpt_response(GPT_QUERY):
    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are an expert in writing CV, specialized in writing CVs for with only very technical words.",
            },
            {"role": "user", "content": GPT_QUERY},
        ],
    )

    print("Query cost:", completion.usage)

    gpt_response = completion.choices[0].message.content
    return gpt_response


def get_db(db_id):
    db = notion.databases.query(
        **{
            "database_id": db_id,
            # "filter": {
            #     "property": "Landmark",
            #     "rich_text": {
            #         "contains": "Bridge",
            #     },
            # },
        }
    )
    return db


def set_to_processing(page_id):
    update_properties = {
        "properties": {
            "_Req Desc Prog": {
                "rich_text": [{"type": "text", "text": {"content": "🟡 Processing..."}}]
            }
        }
    }

    response = notion.pages.update(page_id=page_id, **update_properties)


def set_descr_in_notion(page_id, gpt_response):
    # Set Description, and change status to "Done"
    update_properties = {
        "properties": {
            "CV Description": {
                "rich_text": [{"type": "text", "text": {"content": gpt_response}}]
            },
            "_Req Desc Prog": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🟢 Done. Click button 'Req Desc' to request again."
                        },
                    }
                ]
            },
        }
    }

    response = notion.pages.update(page_id=page_id, **update_properties)


def update_db(db):
    for job_post in db["results"]:
        change_req = job_post["properties"]["_Req Desc Prog"]["rich_text"]
        if len(change_req) != 0:
            assert len(change_req) == 1, "Unhandled case"
            if change_req[0]["text"]["content"] == "🔵 Requested…":
                set_to_processing(job_post["id"])
                job_desc = get_job_desc(job_post["id"])
                gpt_query = get_gpt_query(job_desc)
                gpt_response = get_gpt_response(gpt_query)
                # gpt_response = "TMP"
                set_descr_in_notion(job_post["id"], gpt_response)
                print(f"Updated {job_post['id']}")


def main():
    while True:
        # Example Dataset
        db_id = "8993d6d12560487fbfa2ebd3e93962ad"
        # Personal ID
        db_id = "52acad8fd3ac4c9cb9c01472750dbfac"
        db = get_db(db_id)
        update_db(db)
        sleep(2)
        now = datetime.datetime.now().strftime("%y-%m-%d_%H:%M:%S.%f")[:-3]
        print(f"{now} DB checked (https://www.notion.so/{db_id})")


main()
