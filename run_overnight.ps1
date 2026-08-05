$logFile = "overnight_run_log.txt"

"Starting overnight run at $(Get-Date)" | Out-File $logFile

Remove-Item -Path "data\processed\economic_surveys\*" -Force
Remove-Item -Path "data\chunks\economic_surveys\*" -Force
Remove-Item -Path "data\processed\budget_documents\*" -Force
Remove-Item -Path "data\chunks\budget_documents\*" -Force

"Cleared old files at $(Get-Date)" | Out-File $logFile -Append

python src\2.1_extract_text.py *>> $logFile
"Extraction finished at $(Get-Date)" | Out-File $logFile -Append

python src\3.1_chunk_budget_documents.py *>> $logFile
"Budget documents chunking finished at $(Get-Date)" | Out-File $logFile -Append

python src\3.2_chunk_economic_surveys.py *>> $logFile
"Economic surveys chunking finished at $(Get-Date)" | Out-File $logFile -Append

python src\4.3_load_chromadb.py *>> $logFile
"Embedding finished at $(Get-Date)" | Out-File $logFile -Append

"ALL DONE at $(Get-Date)" | Out-File $logFile -Append