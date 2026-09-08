# 🌍 Global AML/CFT Country Risk Index (GACRI)

An independent analytical framework combining FATF, EU AMLR (Regulation EU 2024/1624), AML/CFT effectiveness (FATF Mutual Evaluations), and additional jurisdictional risk indicators into a transparent, reproducible 0–100 country-risk score.

## Features
- 🌍 **Interactive Global Risk Map** with Plotly click-selection
- 🎯 **0–100 Jurisdictional Risk Score** with dynamic missing-weight scaling
- 🚦 **Risk Bands:** Low, Moderate, Elevated, High, Critical
- 🔍 **"Why?" Explainability Engine** detailing weighted contributions
- 📈 **Historical Risk Score Evolution** time-series tracking
- 🔄 **Regulatory Changes & Deltas Audit Log** tracking FATF/EU list movements
- 📚 **Full Data Provenance & Lineage** with primary document citations

## Methodology v1.0
| Component | Weight | Source |
|---|---:|---|
| **FATF Status** | 35% | FATF ICRG Call for Action & Increased Monitoring |
| **EU AMLR** | 30% | Regulation (EU) 2024/1624 (Articles 29, 30, 31) |
| **Effectiveness** | 20% | FATF Mutual Evaluations (Immediate Outcomes IO1–IO11) |
| **Structural Risk** | 10% | Governance & Corruption Perceptions Index |
| **Sanctions / PF** | 5% | UN Consolidated Sanctions & PF Indicators |

## Disclaimer
This project is an independent analytical model. It is not an official FATF, European Union, AMLA, governmental, or regulatory risk rating.

## Tech Stack
`Python` | `Streamlit` | `Pandas` | `Plotly` | `GitHub`
