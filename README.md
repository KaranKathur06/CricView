# CricView — Cricket Intelligence Platform 🏏

> A production-grade T20 International cricket analytics dashboard built with Streamlit, powered by ~2,500 Cricsheet match files.

## 🚀 Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run ETL pipeline (one-time, ~50 seconds)
python scripts/ingest.py

# 4. Launch the app
streamlit run app.py
```

## 📊 Dashboard Pages

| Page | Description |
|---|---|
| **Overview** | Global KPIs, scoring trends, boundary evolution, toss analysis, venue intelligence |
| **Player Stats** | Individual player deep-dive with career summary, phase splits, opponent matchups, innings log |
| **Comparison** | Player vs Player radar charts, Team vs Team head-to-head records |
| **Overall Analysis** | Historical trends, batting/bowling all-time records, partnerships |
| **Team Analytics** | Team performance with opponent filter, phase analysis, toss impact |
| **Year Explorer** | Season-by-season breakdown, team standings, top performers, match results |

## 🏗️ Architecture

```
CricView/
├── app.py                    ← Entry point
├── pages/                    ← 6 Streamlit pages
├── src/                      ← Analysis modules (batting, bowling, team, charts)
├── components/               ← Reusable UI components (KPI cards, filters, CSS)
├── config/                   ← Theme, constants
├── scripts/ingest.py         ← ETL: JSON → SQLite → Parquet
├── data/
│   ├── cricket.db            ← SQLite database
│   └── processed/            ← 9 parquet cache files
└── .streamlit/config.toml    ← Dark theme
```

## 📈 Data Scale

| Metric | Value |
|---|---|
| JSON match files processed | 3,798 |
| Valid T20I matches | 2,503 |
| Ball-by-ball deliveries | 567,679 |
| Unique batters | 2,889 |
| Unique bowlers | 2,396 |
| Venues | 307 |
| Years covered | 2005–2024 |
| Cold start time | < 1 second (from parquet) |

## 🛠️ Tech Stack

- **Frontend:** Streamlit 1.56+
- **Charts:** Plotly 6.7
- **Data:** Pandas + PyArrow (Parquet)
- **Database:** SQLite
- **ML:** scikit-learn (for future predictive models)

## 📄 License

@[LICENSE](LICENSE)

#

# **`CricView` License Agreement**

Copyright (c) 2026 Karan Kathur

**Effective Date:** April 23, 2026

**Version:** 1.0

---

## **1. Acceptance of Terms**

By accessing or using **CricView** (hereinafter referred to as the “Software,” “Project,” or “Application”), you agree to be bound by the terms and conditions of this License Agreement. If you do not agree to all terms, you may not use the Software.

---

## **2. Grant of License**

**CricView** is provided under the **MIT License**. Subject to the terms of this Agreement, the Licensor grants you a non-exclusive, royalty-free, perpetual, irrevocable license to:

1.  **Use:** Use the Software for any purpose, including commercial use.
2.  **Modify:** Modify, adapt, translate, or create derivative works based on the Software.
3.  **Distribute:** Distribute copies of the Software or derivative works.
4.  **Sublicense:** Sublicense the Software, provided the sublicensee agrees to the terms of this License.
5.  **Display and Perform:** Display and perform the Software publicly.

---

## **3. Source Code and Distribution**

When distributing the Software or derivative works, you must:

1.  **Retain License:** Keep the original license notice and copyright notice.
2.  **Indicate Changes:** Clearly indicate any changes you have made to the Software.
3.  **Provide License:** Include a copy of this MIT License with the distribution.

---

## **4. Limitations**

- **No Warranty:** The Software is provided “as is,” without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.
- **No Liability:** In no event shall the Licensor be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the Software or the use or other dealings in the Software.
- **No Support:** The Licensor is not obligated to provide maintenance, support, updates, or enhancements for the Software.

---

## **5. Data Usage and Attribution**

- **Cricsheet Data:** This project uses data from [Cricsheet](https://cricsheet.org/), which is licensed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/). Users must comply with Cricsheet's terms and provide appropriate attribution.
- **Attribution Requirement:** When distributing CricView or derivative works, you must credit the original creators and Cricsheet as the data source.

---

## **6. Intellectual Property**

All intellectual property rights in the Software, including copyright and trade secrets, belong to **Karan Kathur**. No ownership rights are transferred to the licensee under this Agreement.

---

## **7. Termination**

This License Agreement terminates automatically if you fail to comply with any of its terms or conditions. Upon termination, you must immediately cease all use of the Software and destroy all copies.

---

## **8. Modifications**

This License Agreement may be updated from time to time. Material changes will be communicated through updates to the project documentation. Continued use of the Software after changes constitutes acceptance of the revised terms.

---

## **9. Governing Law**

This License Agreement shall be governed by and construed in accordance with the laws of **India**, without regard to its conflict of law principles.

---

## **10. Contact Information**

For questions regarding this License Agreement, please contact:

**Karan Kathur**  
**Email:** [EMAIL_ADDRESS]  
**GitHub:** [https://github.com/KaranKathur06](https://github.com/KaranKathur06)
