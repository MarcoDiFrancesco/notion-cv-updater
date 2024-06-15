# Notion CV Updater

Update the CV from a job posting.

## How it works

- **Create a new Dataset**: You can copy the [template](https://marcodifrancesco.notion.site/8993d6d12560487fbfa2ebd3e93962ad?v=f10b880e1c0f472981705bfbbcb066b6&pvs=4).

<div style="max-width: 700px;">
    <p align="center">
        <kbd>
            <img src="assets/dataset-example.png" />
        </kbd>
    </p>
</div>

- **Create a new Job Posting**: job posting contains inside the full job description.

- **Underline your skills**: make in bold your skill, for example including technologies (e.g. “PySpark”) and tasks (e.g. “data mining”).

<div style="max-width: 400px;">
    <p align="center">
        <kbd>
            <img src="assets/post-example.png" />
        </kbd>
    </p>
</div>

## Setup API

```bash
pip install -r requirements.txt
```

- **Creat Notion Integration**: create and then get API key [Notion Integrations Guide](https://developers.notion.com/docs/create-a-notion-integration#getting-started).

- **Rename**: `.env.example` -> `.env`. Place here the API key.

<div style="max-width: 300px;">
    <p align="center">
        <kbd>
         <img src="assets/add-integration-to-dataset.png" />
        </kbd>
    </p>
</div>

- **Run the notebook**