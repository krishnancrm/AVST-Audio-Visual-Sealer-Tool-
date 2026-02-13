#!/bin/bash
# run_audit.sh - Digital Fort Batch Automation

echo "==============================================="
echo " DIGITAL FORT: COMMENCING FORENSIC BATCH AUDIT"
echo "==============================================="

# 1. Start the Python Master Script
# This will process all files in the /Screenshots folder
python main_batch_test.py

# 2. Post-Run Summary
echo ""
echo "==============================================="
echo " AUDIT COMPLETE"
echo "==============================================="
echo " Results saved to: final_forensic_report_batch.csv"
echo " Disfigured images: /jigsaw_encoded/"
echo "==============================================="

# Optional: List the first few lines of the report for a quick check
head -n 5 final_forensic_report_batch.csv