# SatarkAI

Shak wale SMS, WhatsApp ya email ko check karne ke liye beginner-friendly Hinglish demo. Existing single-page UI aur transparent rule checks ko preserve kiya gaya hai; ab chhota reproducible ML prototype bhi response mein prediction deta hai.

> **Reality check:** `ml/dataset.csv` mein 60 hand-curated examples hain. Yeh public/representative dataset nahi hai, labels independent reviewers se verify nahi hue, aur chhota held-out test set real-world performance nahi batata. Isse hackathon prototype samjhein, fraud ka final detector nahi. Metrics `ml/metrics.json` mein training se generate hote hain.

## Local run (Windows)

1. Python 3.12 recommended hai, phir archive extract karein.
2. Extracted folder mein PowerShell kholkar chalayein:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python ml/train.py
python app.py
```

3. Browser mein `http://127.0.0.1:5000` kholein. Band karne ke liye `Ctrl+C`.

PowerShell activation block kare to:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe ml/train.py
.\.venv\Scripts\python.exe app.py
```

Model train na ho ya artifact missing/corrupt ho to app automatic rules-only fallback use karta hai. Local app kabhi message ko save nahi karta. User ka URL **sirf text ki tarah** inspect hota hai; server usse open, resolve, crawl ya fetch nahi karta. Browser ke fonts optional Google Fonts URL se aate hain, lekin message/API traffic localhost par rehta hai. Hosted mode header mein batata hai ki text hosted server ko bheja ja raha hai.

## Tests and evaluation

```powershell
python -m unittest discover -s tests -v
python ml/train.py
```

Training fixed stratified 75/25 split (`random_state=42`) use karta hai. Word + character TF-IDF aur logistic regression model hai. Accuracy, precision, recall, F1 aur confusion matrix `ml/metrics.json` mein hain. Har training run `ml/model.joblib` regenerate karta hai. Chhote test set ki wajah se ek bhi sample score ko kaafi badal sakta hai.

## Deployment

Docker + Gunicorn config included hai (`Dockerfile`, `render.yaml`). `deploy.ps1` Docker image build/run commands dikhata hai. Hosted deployment par user messages server ko bheje jayenge; local privacy promise sirf local run ke liye hai. Public deploy se pehle privacy policy, HTTPS, abuse controls aur larger independently-reviewed evaluation zaroor add karein.

## API

- `GET /api/health` — status and whether ML artifact loaded.
- `POST /api/analyze-message` — JSON `{ "message": "..." }`.
- Response contains rule indicators, ML prediction/confidence (when available), risk screening, actions, limitations, and `url_checked: false`.

## File map

- `app.py` — Flask routes, safe local text analysis, model integration and fallback.
- `templates/index.html`, `static/` — preserved SatarkAI UI and API client.
- `ml/dataset.csv`, `ml/train.py`, `ml/model.joblib`, `ml/metrics.json` — dataset, reproducible training, trained model and evaluation.
- `tests/` — API validation, screening and fallback tests.
- `Dockerfile`, `render.yaml`, `deploy.ps1` — deployment files.
- `docs/` — dataset notes, API and team push guide.


## Deployment notes

The included `Dockerfile` and `render.yaml` are the deployment configuration.
On Render, you can create a Blueprint using `render.yaml`, or create a Docker web
service using this repository. The service health check is `/api/health`.

For a local Docker test:

```bash
docker build -t satarkai .
docker run --rm -p 8080:8080 -e PORT=8080 satarkai
```

Hosted analysis sends the pasted message to the hosted SatarkAI service. Do not
claim localhost-only privacy for a public deployment. Before public use, add an
appropriate privacy notice, abuse controls, and stronger independently reviewed
model evaluation.

## Important: files needed to complete the project

This ZIP contains only the files that were uploaded in this chat. It does **not**
contain the `templates/`, `static/`, `ml/`, `tests/`, or `docs/` folders referenced
above, because those folders were not included in the uploaded files. In
particular, `app.py` expects `templates/index.html`, and ML functionality expects
`ml/model.joblib` (though the backend has a rules-only fallback). Add the missing
project folders from your original project before treating this as a complete,
deployable application.
