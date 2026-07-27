# Datasheet for DriftHealth Benchmark

## 1. Motivation
- **Purpose**: DriftHealth is constructed to evaluate federated continual learning algorithms (DriftAdapt) under realistic spatial, seasonal, linguistic, and protocol concept drift across Community Health Worker (CHW) clinics.
- **Creators**: DriftAdapt Research Team.

## 2. Composition & Provenance
- **Raw Corpora**:
  - MedMCQA (License: Apache-2.0 (Academic Q&A dataset))
  - MedQA (License: MIT License (USMLE & Medical Board Q&A))
  - HealthCareMagic (License: CC-BY 4.0 (Doctor-Patient Dialogues))
  - MedDialog (License: MIT License (Clinical Consultation Dialogues))
  - PubMedQA (License: MIT License (Biomedical Literature Q&A))
- **Ontology Coverage**: 100.0% mapped across 16 CHW condition categories.
- **Discard Rate**: 0.0% unmapped items discarded.

## 3. Structure & Simulation
- **Clinics**: 4 simulated CHW clinics assigned to 4 regional epidemiological profiles.
- **Time Horizon**: 12 monthly steps.
- **Items per Shard**: ≥200 items per (clinic, month) pair.
- **Drift Injections**: Deterministic linguistic drift (local disease terms, code-mixing, clinical abbreviations) and step-change protocol drift.

## 4. Intended Use & Limitations
- **Intended Use**: Benchmarking federated continual learning, drift estimation, and concept drift mitigation models.
- **Limitations**: Synthetic sampling distributions modeled on epidemiological data; does not replace real clinical field trials.
