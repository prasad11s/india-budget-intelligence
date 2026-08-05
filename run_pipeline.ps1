$env:PYTHONIOENCODING = "utf-8"
$logFile = "run_pipeline_log.txt"

"Starting run at $(Get-Date)" | Out-File $logFile

python cleanup_broken_processed.py *>> $logFile
"Cleanup finished at $(Get-Date)" | Out-File $logFile -Append

python src\2.1_extract_text.py *>> $logFile
"Extraction finished at $(Get-Date)" | Out-File $logFile -Append

python src\3.1_chunk_budget_documents.py *>> $logFile
"Budget documents chunking finished at $(Get-Date)" | Out-File $logFile -Append

python src\3.2_chunk_economic_surveys.py *>> $logFile
"Economic surveys chunking finished at $(Get-Date)" | Out-File $logFile -Append

python src\4.3_load_chromadb.py *>> $logFile
"Embedding finished at $(Get-Date)" | Out-File $logFile -Append

"ALL DONE at $(Get-Date)" | Out-File $logFile -Append