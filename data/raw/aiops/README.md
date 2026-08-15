# AIOps Challenge 2020 Dataset

This folder should contain the CSV files from the AIOps-Challenge-2020 dataset. However, the data must be downloaded manually from the official sources.

## Download Instructions

The dataset is not available as a public git repository. You need to download it from one of these sources:

### Option 1: Google Drive (Recommended)
1. Go to: https://drive.google.com/file/d/1nkEsD1g7THm_T58KwUQZ7o-b174fdx-n/view?usp=sharing
2. Download the ZIP file
3. Extract the contents to this directory (`data/raw/aiops/`)

### Option 2: Tsinghua Cloud
1. Go to: https://cloud.tsinghua.edu.cn/f/c1ea3426ce444bc9baae/
2. Download the ZIP file
3. Extract the contents to this directory (`data/raw/aiops/`)

## Dataset Contents

Once extracted, you should have:
- `故障整理（预赛）.csv` - Failure description file with timestamps, fault types, and locations
- `AIOps挑战赛数据/` - Main data directory containing daily data folders:
  - `业务指标/` - Business metrics
  - `平台指标/` - Infrastructure metrics
  - `调用链指标/` - Traces/span data

## Notes

- Last updated: 2020-10-19
- MD5 checksum: fac7fe1b4e048c81ef88874334b73534 (verify after download)
- License: For non-commercial use only (research, education)
- For traces data, `id` is the span ID and `pid` is the parent span ID (see OpenTracing: https://opentracing.io/docs/overview/spans/)
